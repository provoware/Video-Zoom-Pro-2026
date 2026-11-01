"""Autonomer WAV/Bild-Workflow: lokale Dateien, persistente Aufträge, sichere Archivierung."""
from __future__ import annotations

import fcntl
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import threading
import time
import unicodedata
from datetime import datetime, timezone

FORMATE = {
    "HOCH": (1080, 1920), "BREI": (1920, 1080), "QUAD": (1080, 1080),
    "KLAS": (800, 600), "4K": (3840, 2160),
}
BILDTYPEN = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}
KATEGORIEN = {"PROVOWARE", "CODING", "THEMA"}
UEBERGAENGE = ("fade", "smoothleft", "smoothright", "wipeleft", "circleopen")


def zeit() -> str:
    return datetime.now(timezone.utc).isoformat()


def pruefsumme(pfad: Path) -> str:
    h = hashlib.sha256()
    with pfad.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def titel(dateiname: str) -> str:
    """Nur erkannte Provideranhänge abschneiden, nicht willkürlich Titelwörter."""
    name = Path(dateiname).stem
    marker = re.search(
        r"(?i)(?:[ _-]+|^)(?:https?[:_/-]*)?(?:www[._-]*)?"
        r"(?:suno|youtube|youtu|soundcloud|tiktok|instagram)[._-]+(?:com|be)\b",
        name,
    )
    if marker:
        name = name[:marker.start()]
    name = re.sub(r"[ _-]+20\d{2}[-_]?\d{2}[-_]?\d{2}(?:[-_T ]?\d{4,6})?$", "", name)
    name = unicodedata.normalize("NFC", name)
    name = "".join(c if c.isalnum() or c in " _-" else " " for c in name)
    return re.sub(r"[ _-]{2,}", " ", name).strip(" _-")[:100] or "Unbenannter Song"


def slug(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text.replace("ß", "ss"))
    plain = "".join(c for c in normalized if not unicodedata.combining(c)).lower()
    return re.sub(r"[^a-z0-9]+", "-", plain).strip("-")[:80] or "song"


def kategorie(name: str) -> str | None:
    if Path(name).suffix.lower() not in BILDTYPEN:
        return None
    words = set(re.findall(r"[a-z0-9]+", Path(name).stem.casefold()))
    if "chatgpt" not in words:
        return None
    if "coding" in words and not ({"thema", "provoware", "provovare"} & words):
        return "CODING"
    if "thema" in words and "coding" not in words:
        return "THEMA"
    if ({"provoware", "provovare"} & words) and "coding" not in words:
        return "PROVOWARE"
    return None


def regulaer(pfad: Path) -> bool:
    return pfad.is_file() and not pfad.is_symlink()


def stabil(pfad: Path, sekunden: int = 5) -> bool:
    try:
        s = pfad.stat(follow_symlinks=False)
        return regulaer(pfad) and s.st_size > 100 and time.time() - s.st_mtime >= sekunden
    except OSError:
        return False


def json_sicher(pfad: Path, wert: dict) -> None:
    """Atomisch, kein beschädigtes Zwischen-Journal als bestätigter Zustand."""
    pfad.parent.mkdir(parents=True, exist_ok=True)
    tmp = pfad.with_name("." + pfad.name + "." + str(os.getpid()) + ".tmp")
    fd = os.open(tmp, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as out:
            json.dump(wert, out, ensure_ascii=False, indent=2)
            out.flush()
            os.fsync(out.fileno())
        os.replace(tmp, pfad)
    finally:
        tmp.unlink(missing_ok=True)


def lesen(pfad: Path, standard: dict) -> dict:
    if not pfad.exists():
        return standard
    if pfad.is_symlink():
        raise RuntimeError("Unsichere Zustandsdatei: symbolische Verknüpfung.")
    try:
        wert = json.loads(pfad.read_text(encoding="utf-8"))
        if not isinstance(wert, dict):
            raise ValueError("kein Objekt")
        return wert
    except (ValueError, UnicodeError, OSError) as exc:
        raise RuntimeError("Auftragsjournal beschädigt. Original bleibt unangetastet: " + str(exc)) from exc


def konfiguration() -> dict:
    return {
        "downloads": str(Path.home() / "Downloads"),
        "arbeitsordner": str(Path.home() / "Video-Zoom-Pro"),
        "format": "BREI", "kategorie": "PROVOWARE",
        "fps": 25, "cpu_prozent": 30, "ram_mb": 2048,
        "intervall": 15, "uebergang": 0.45, "stapelgroesse": 3,
    }


def konfigurieren(cfg: dict) -> dict:
    data = konfiguration()
    data.update({k: v for k, v in cfg.items() if k in data})
    if data["format"] not in FORMATE or data["kategorie"] not in KATEGORIEN:
        raise ValueError("Ungültiger Formatcode oder Kategorie.")
    for key, low, high in (("cpu_prozent", 1, 30), ("ram_mb", 256, 32768),
                           ("intervall", 5, 3600), ("stapelgroesse", 1, 20)):
        value = int(data[key])
        if not low <= value <= high:
            raise ValueError(key + " außerhalb der zulässigen Grenzen.")
        data[key] = value
    data["fps"] = 25
    data["uebergang"] = min(1.2, max(0.0, float(data["uebergang"])))
    return data


def medieninfo(pfad: Path) -> dict:
    p = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries",
         "format=duration:stream=codec_type,width,height", "-of", "json", str(pfad)],
        capture_output=True, text=True, timeout=30, check=True,
    )
    return json.loads(p.stdout)


def dauer(audio: Path) -> float:
    info = medieninfo(audio)
    if not any(s.get("codec_type") == "audio" for s in info.get("streams", [])):
        raise ValueError("WAV enthält keine lesbare Tonspur.")
    value = float(info.get("format", {}).get("duration", 0))
    if not (0.4 < value < 28800 and math.isfinite(value)):
        raise ValueError("WAV-Länge ungültig.")
    return value


def zeitplan(sekunden: float, bilder: int, fps: int = 25, uebergang: float = 0.45) -> tuple[float, float, float]:
    if bilder < 1 or bilder > 40:
        raise ValueError("Für eine Produktion sind 1 bis 40 Bilder erlaubt.")
    if not math.isfinite(sekunden) or sekunden < bilder * 0.55 + 0.4:
        raise ValueError("Zu viele Bilder für die Songlänge.")
    schnell_frames = max(1, min(round(fps * 0.55), int(sekunden * fps * 0.2 / bilder)))
    schnell = schnell_frames / fps
    rest = sekunden - bilder * schnell
    blend_frames = min(int(fps * uebergang), int(rest * fps / bilder * 0.23)) if bilder > 1 else 0
    blend = blend_frames / fps
    pro_bild = math.ceil((rest * fps + (bilder - 1) * blend_frames) / bilder) / fps
    return schnell, pro_bild, blend


def ffmpeg_befehl(audio: Path, bilder: list[Path], ziel: Path, laenge: float,
                  cfg: dict, weich: bool = False) -> list[str]:
    breite, hoehe = FORMATE[cfg["format"]]
    fps = cfg["fps"]
    schnell, langsam, blend = zeitplan(laenge, len(bilder), fps, cfg["uebergang"])
    befehl = ["ffmpeg", "-hide_banner", "-nostdin", "-loglevel", "error", "-n"]
    for bild in bilder:
        befehl += ["-loop", "1", "-framerate", str(fps), "-t", f"{langsam:.6f}", "-i", str(bild)]
    befehl += ["-i", str(audio)]
    # 88%-Sicherheitsrahmen: kein Abschneiden unbekannter Bildränder und Schrift.
    innen_b, innen_h = 2 * int(breite * .44), 2 * int(hoehe * .44)
    basis = (f"scale={innen_b}:{innen_h}:force_original_aspect_ratio=decrease,"
             f"pad={breite}:{hoehe}:(ow-iw)/2:(oh-ih)/2:color=black,setsar=1")
    graph, rueck, vor = [], [], []
    for i in range(len(bilder)):
        graph.append(f"[{i}:v]split=2[r{i}][v{i}]")
        graph.append(f"[r{i}]{basis},fps={fps},trim=duration={schnell:.6f},"
                     f"setpts=PTS-STARTPTS,settb=AVTB,format=yuv420p[s{i}]")
        rueck.append(f"s{i}")
        if i % 4 == 0:
            z, x = "min(1+on*0.001,1.10)", "iw/2-iw/zoom/2"
        elif i % 4 == 1:
            z, x = "max(1.10-on*0.001,1)", "iw/2-iw/zoom/2"
        elif i % 4 == 2:
            z, x = "1.08", f"(iw-iw/zoom)*on/{max(1,int(langsam*fps))}"
        else:
            z, x = "1.08", f"(iw-iw/zoom)*(1-on/{max(1,int(langsam*fps))})"
        y = "ih/2-ih/zoom/2"
        graph.append(f"[v{i}]{basis},zoompan=z='{z}':x='{x}':y='{y}':"
                     f"d=1:s={breite}x{hoehe}:fps={fps},trim=duration={langsam:.6f},"
                     f"setpts=PTS-STARTPTS,fps={fps},settb=AVTB,format=yuv420p[vout{i}]")
        vor.append(f"vout{i}")
    graph.append("".join(f"[{label}]" for label in reversed(rueck)) +
                 f"concat=n={len(bilder)}:v=1:a=0[anfang]")
    aktuell = vor[0]
    for i, incoming in enumerate(vor[1:], start=1):
        label = f"uebergang{i}"
        if blend:
            typ = "fade" if weich else UEBERGAENGE[(i - 1) % len(UEBERGAENGE)]
            offset = max(0.0, i * (langsam - blend))
            graph.append(f"[{aktuell}][{incoming}]xfade=transition={typ}:"
                         f"duration={blend:.6f}:offset={offset:.6f}[{label}]")
        else:
            graph.append(f"[{aktuell}][{incoming}]concat=n=2:v=1:a=0[{label}]")
        aktuell = label
    graph.append(f"[anfang][{aktuell}]concat=n=2:v=1:a=0[video]")
    return befehl + [
        "-filter_complex", ";".join(graph), "-map", "[video]", "-map", f"{len(bilder)}:a:0",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", "-t", f"{laenge:.6f}",
        "-movflags", "+faststart", "-threads", "2", "-progress", "pipe:1",
        "-nostats", str(ziel),
    ]


def quota_befehl(befehl: list[str], cfg: dict) -> list[str]:
    kerne = len(os.sched_getaffinity(0)) if hasattr(os, "sched_getaffinity") else (os.cpu_count() or 1)
    anteil = max(1, int(kerne * cfg["cpu_prozent"]))
    return ["systemd-run", "--user", "--scope", "--quiet", "--collect", "-p",
            f"CPUQuota={anteil}%", "-p", f"MemoryMax={cfg['ram_mb']}M", "--", *befehl]


def kopieren_und_archivieren(quelle: Path, ziel: Path, hashwert: str) -> None:
    """Prüfbare 2-Phasen-Ablage, Quelle nur nach bestätigtem Archiv löschen."""
    if not regulaer(quelle):
        if regulaer(ziel) and pruefsumme(ziel) == hashwert:
            return  # Wiederaufnahme, Datei wurde bereits sicher verschoben.
        raise RuntimeError("Originaldatei fehlt; Archiv nicht bestätigt.")
    if pruefsumme(quelle) != hashwert:
        raise RuntimeError("Quelle seit Vorbereitung verändert.")
    ziel.parent.mkdir(parents=True, exist_ok=True)
    if ziel.exists() or ziel.is_symlink():
        if not regulaer(ziel) or pruefsumme(ziel) != hashwert:
            raise RuntimeError("Archiv-Zielkonflikt – keine Datei überschrieben.")
    else:
        tmp = ziel.with_name("." + ziel.name + "." + hashwert[:12] + ".teil")
        with quelle.open("rb") as src, tmp.open("xb") as dest:
            shutil.copyfileobj(src, dest, 1024 * 1024)
            dest.flush()
            os.fsync(dest.fileno())
        try:
            if pruefsumme(tmp) != hashwert:
                raise RuntimeError("Archivkopie fehlerhaft.")
            os.link(tmp, ziel, follow_symlinks=False)
        finally:
            tmp.unlink(missing_ok=True)
    if pruefsumme(quelle) != hashwert:
        raise RuntimeError("Quelle hat sich während der Archivierung verändert.")
    quelle.unlink()


class Workflow:
    """Zwei voneinander getrennte Schritte: vorbereiten, dann Stapel abarbeiten."""

    def __init__(self, cfg: dict, meldung=None, fortschritt=None, testmodus: bool = False):
        self.cfg = konfigurieren(cfg)
        self.downloads = Path(self.cfg["downloads"]).expanduser().absolute()
        self.ordner = Path(self.cfg["arbeitsordner"]).expanduser().absolute()
        if not self.downloads.is_dir() or self.downloads.is_symlink():
            raise ValueError("Downloads-Ordner fehlt oder ist unsicher.")
        if self.ordner == self.downloads or self.downloads in self.ordner.parents:
            raise ValueError("Arbeitsordner darf nicht innerhalb des Downloads-Ordners liegen.")
        self.meldung = meldung or (lambda text: None)
        self.fortschritt = fortschritt or (lambda event: None)
        self.testmodus = testmodus
        self.stop = threading.Event()
        self.lock_file = None
        for folder in ("EINGANG", "BILDER", "FERTIG", "VERWENDET", "PROTOKOLLE"):
            (self.ordner / folder).mkdir(parents=True, exist_ok=True)
        self.journal = self.ordner / "PROTOKOLLE" / "auftraege.json"
        self.zustand = lesen(self.journal, {"schema": 1, "auftraege": {}})
        if self.zustand.get("schema") != 1 or not isinstance(self.zustand.get("auftraege"), dict):
            raise RuntimeError("Unbekanntes Auftragsjournal – keine automatische Ersetzung.")
        self.ereignis = {"phase": "bereit", "prozent": 0}

    def sperren(self):
        pfad = self.ordner / "PROTOKOLLE" / "dienst.lock"
        self.lock_file = pfad.open("a+")
        try:
            fcntl.flock(self.lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            self.lock_file.close()
            self.lock_file = None
            raise RuntimeError("Bereits eine Verarbeitung aktiv.") from exc

    def freigeben(self):
        if self.lock_file is not None:
            fcntl.flock(self.lock_file.fileno(), fcntl.LOCK_UN)
            self.lock_file.close()
            self.lock_file = None

    def status(self):
        stats = {}
        for job in self.zustand["auftraege"].values():
            key = job["status"]
            stats[key] = stats.get(key, 0) + 1
        disk = shutil.disk_usage(self.ordner)
        try:
            mem = {}
            for line in Path("/proc/meminfo").read_text().splitlines():
                if line.startswith(("MemTotal:", "MemAvailable:")):
                    key, value = line.split(":", 1)
                    mem[key] = int(value.strip().split()[0]) // 1024
        except (OSError, ValueError, IndexError):
            mem = {}
        return {"zeit_utc": zeit(), "auftraege": stats, "aktueller_vorgang": self.ereignis,
                "sensoren": {"freier_speicher_gb": round(disk.free / 1024**3, 2),
                            "cpu_kerne": len(os.sched_getaffinity(0)) if hasattr(os, "sched_getaffinity") else os.cpu_count(),
                            "ram_gesamt_mb": mem.get("MemTotal"),
                            "ram_verfuegbar_mb": mem.get("MemAvailable")},
                "cpu_ziel_prozent": self.cfg["cpu_prozent"]}

    def fortschreiben(self, phase, prozent, **details):
        self.ereignis = {"phase": phase, "prozent": min(100, max(0, int(prozent))), **details}
        self.fortschritt(self.ereignis)
        json_sicher(self.ordner / "PROTOKOLLE" / "STATUS.json", self.status())

    def speichern(self):
        json_sicher(self.journal, self.zustand)
        self.fortschreiben(self.ereignis["phase"], self.ereignis["prozent"])

    def melden(self, text):
        self.meldung(text)
        pfad = self.ordner / "PROTOKOLLE" / "ereignisse.jsonl"
        with pfad.open("a", encoding="utf-8") as file:
            file.write(json.dumps({"zeit": zeit(), "meldung": text}, ensure_ascii=False) + "\n")

    def bilder_einsortieren(self):
        """Nur ausdrücklich markierte ChatGPT-Bilder mit verifizierter Kopie ablegen."""
        sortiert, offen = 0, 0
        for bild in sorted(self.downloads.iterdir()):
            if bild.suffix.lower() not in BILDTYPEN or not stabil(bild):
                continue
            zielkategorie = kategorie(bild.name)
            if zielkategorie is None:
                offen += 1
                continue
            try:
                info = medieninfo(bild)
                stream = next(s for s in info["streams"] if s.get("codec_type") == "video")
                breite, hoehe = int(stream["width"]), int(stream["height"])
                if not 1 <= breite <= 16384 or not 1 <= hoehe <= 16384:
                    raise ValueError("Bildabmessungen außerhalb der Sicherheitsgrenze.")
                digest = pruefsumme(bild)
                ordner = self.ordner / "BILDER" / zielkategorie
                ordner.mkdir(parents=True, exist_ok=True)
                ziel = ordner / bild.name
                if ziel.exists() and (not regulaer(ziel) or pruefsumme(ziel) != digest):
                    ziel = ordner / (bild.stem + "_" + digest[:12] + bild.suffix)
                if ziel.is_symlink():
                    raise RuntimeError("Unsichere Zieldatei, Bild bleibt im Download.")
                kopieren_und_archivieren(bild, ziel, digest)
                json_sicher(ziel.with_name(ziel.name + ".json"), {
                    "schema": 1, "kategorie": zielkategorie, "herkunft": "chatgpt",
                    "bild": ziel.name, "breite": breite, "hoehe": hoehe,
                    "seitenverhaeltnis": round(breite / hoehe, 4), "sha256": digest,
                    "zeit_utc": zeit(),
                })
                self.melden("Bild einsortiert: " + zielkategorie + "/" + ziel.name)
                sortiert += 1
            except (OSError, ValueError, RuntimeError, StopIteration,
                    subprocess.SubprocessError) as exc:
                offen += 1
                self.melden("Bild bleibt unverändert zur Prüfung: " + bild.name +
                            " – " + str(exc)[-220:])
        return sortiert, offen

    def vorbereiten(self):
        self.bilder_einsortieren()
        wavs = sorted(p for p in self.downloads.glob("*.wav") if stabil(p))
        bereit = wartet = 0
        for idx, pfad in enumerate(wavs, 1):
            if self.stop.is_set():
                break
            name = titel(pfad.name)
            bilder_ordner = self.ordner / "EINGANG" / slug(name) / "BILDER"
            bilder_ordner.mkdir(parents=True, exist_ok=True)
            bilder = sorted(p for p in bilder_ordner.iterdir()
                            if p.suffix.lower() in BILDTYPEN and stabil(p))
            key = hashlib.sha256(str(pfad).encode()).hexdigest()[:24]
            old = self.zustand["auftraege"].get(key, {})
            if old.get("status") in ("ARCHIVIERT", "ARCHIV_WARTET", "FERTIG"):
                continue
            if not bilder:
                self.zustand["auftraege"][key] = {"titel": name, "status": "WARTET",
                                                  "hinweis": f"Bilder nach {bilder_ordner} kopieren."}
                wartet += 1
            else:
                try:
                    length = dauer(pfad)
                    zeitplan(length, len(bilder), self.cfg["fps"], self.cfg["uebergang"])
                    paths = [pfad, *bilder]
                    manifest = [{"pfad": str(p), "sha256": pruefsumme(p),
                                 "groesse": p.stat().st_size, "mtime_ns": p.stat().st_mtime_ns} for p in paths]
                    self.zustand["auftraege"][key] = {"titel": name, "status": "BEREIT",
                                                      "dateien": manifest, "laenge": length,
                                                      "versuche": old.get("versuche", 0)}
                    bereit += 1
                except (OSError, ValueError, subprocess.SubprocessError) as exc:
                    self.zustand["auftraege"][key] = {"titel": name, "status": "PRUEFEN",
                                                      "hinweis": str(exc)[:300]}
                    wartet += 1
            self.fortschreiben("vorbereiten", idx / max(1,len(wavs)) * 100, titel=name)
            self.speichern()
        self.melden(f"Vorbereitung: {bereit} bereit, {wartet} warten.")
        return bereit, wartet

    def _archive(self, key: str, job: dict):
        if not job.get("video"):
            raise RuntimeError("Videopfad fehlt.")
        output = Path(job["video"])
        if not regulaer(output) or pruefsumme(output) != job["video_hash"]:
            raise RuntimeError("Video beschädigt oder nicht vorhanden.")
        receipt = self.ordner / "PROTOKOLLE" / "archiv.jsonl"
        for entry in job["dateien"]:
            src = Path(entry["pfad"])
            dest = self.ordner / "VERWENDET" / (src.stem + "_verwendet_" + entry["sha256"][:8] + src.suffix)
            kopieren_und_archivieren(src, dest, entry["sha256"])
            with receipt.open("a", encoding="utf-8") as log:
                log.write(json.dumps({"zeit": zeit(), "quelle": str(src), "ziel": str(dest),
                                      "sha256": entry["sha256"], "auftrag": key}, ensure_ascii=False) + "\n")
            self.fortschreiben("archivieren", 95, titel=job["titel"], datei=src.name)
        job["status"] = "ARCHIVIERT"
        self.speichern()

    def _render(self, job: dict):
        audio, *images = [Path(item["pfad"]) for item in job["dateien"]]
        for item in job["dateien"]:
            p = Path(item["pfad"])
            if not regulaer(p) or pruefsumme(p) != item["sha256"]:
                raise RuntimeError("Datenfehler: Quellmedium fehlt oder wurde verändert.")
        zielbasis = slug(job["titel"]) + "_" + self.cfg["format"]
        zielordner = self.ordner / "FERTIG"
        ziel = next((zielordner / (zielbasis + ("" if i == 0 else "_" + str(i)) + ".mp4")
                     for i in range(10000) if not (zielordner / (zielbasis + ("" if i == 0 else "_" + str(i)) + ".mp4")).exists()), None)
        if ziel is None:
            raise RuntimeError("Kein sicherer Ausgabename mehr verfügbar.")
        teil = ziel.with_name(ziel.stem + ".teil.mp4")
        if teil.exists() or teil.is_symlink():
            raise RuntimeError("Eine unvollständige Videodatei liegt bereits vor.")
        if not self.testmodus:
            from .diagnose import scope_verfuegbar
            if not scope_verfuegbar():
                raise RuntimeError("CPU-/RAM-Begrenzung derzeit nicht verfügbar.")
        def starten(weich=False):
            command = ffmpeg_befehl(audio, images, teil, job["laenge"], self.cfg, weich)
            if not self.testmodus:
                command = quota_befehl(command, self.cfg)
            with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                  text=True, bufsize=1) as proc:
                try:
                    for line in proc.stdout:
                        if self.stop.is_set():
                            proc.terminate()
                            raise RuntimeError("Produktion angehalten; Auftrag bleibt gespeichert.")
                        if line.startswith("out_time_ms="):
                            micros = int(line.split("=",1)[1])
                            pct = min(90, max(1, int(micros / (job["laenge"] * 1e6) * 90)))
                            self.fortschreiben("rendern", pct, titel=job["titel"])
                    _, err = proc.communicate(timeout=max(90, job["laenge"] * 35))
                    if proc.returncode:
                        raise RuntimeError(err[-900:])
                finally:
                    if proc.poll() is None:
                        proc.kill()
                        proc.wait()
        try:
            try:
                starten()
            except RuntimeError as exc:
                if "transition" not in str(exc).lower():
                    raise
                teil.unlink(missing_ok=True)
                self.melden("Übergang inkompatibel, sichere Standardblende gewählt.")
                starten(weich=True)
            info = medieninfo(teil)
            streams = info.get("streams", [])
            duration = float(info.get("format", {}).get("duration", 0))
            if not {"video", "audio"}.issubset({s.get("codec_type") for s in streams}):
                raise RuntimeError("Ergebnis enthält nicht Bild und Ton.")
            if abs(duration - job["laenge"]) > max(1.2, job["laenge"] * .015):
                raise RuntimeError("Videolänge und Songlänge passen nicht.")
            # Atomisch und kollisionssicher; bestehende Datei niemals überschreiben.
            os.link(teil, ziel, follow_symlinks=False)
            teil.unlink()
            return ziel
        except Exception:
            if teil.exists():
                teil.rename(teil.with_name(teil.name + ".fehler"))
            raise

    def stapel(self):
        from .diagnose import scope_verfuegbar
        jobs = self.zustand["auftraege"]
        for key, job in list(jobs.items()):
            if job.get("status") in ("FERTIG", "ARCHIV_WARTET"):
                try:
                    self._archive(key, job)
                except (OSError, RuntimeError) as exc:
                    job["status"] = "ARCHIV_WARTET"
                    job["hinweis"] = str(exc)
                    self.speichern()
        ready = [(key, job) for key, job in jobs.items() if job["status"] == "BEREIT"]
        if ready and not self.testmodus and not scope_verfuegbar():
            self.fortschreiben("pausiert_ressourcen", 0, hinweis="systemd-Benutzersitzung prüfen")
            return 0, len(ready)
        done = 0
        for index, (key, job) in enumerate(ready[:self.cfg["stapelgroesse"]],1):
            if self.stop.is_set():
                break
            job["status"] = "LAEUFT"
            job["versuche"] = job.get("versuche", 0) + 1
            self.speichern()
            try:
                ziel = self._render(job)
                job["video"] = str(ziel)
                job["video_hash"] = pruefsumme(ziel)
                job["status"] = "FERTIG"
                self.speichern()
                try:
                    self._archive(key, job)
                except (OSError, RuntimeError) as exc:
                    job["status"] = "ARCHIV_WARTET"
                    job["hinweis"] = str(exc)
                    self.speichern()
                done += 1
            except (OSError, RuntimeError, ValueError, subprocess.SubprocessError) as exc:
                job["status"] = "PRUEFEN" if "Datenfehler" in str(exc) else "BEREIT"
                job["hinweis"] = str(exc)[-500:]
                if job["versuche"] >= 2:
                    job["status"] = "PRUEFEN"
                self.speichern()
                self.melden(job["titel"] + ": " + job["hinweis"])
            self.fortschreiben("stapel", index / max(1,len(ready)) * 100,
                               titel=job["titel"], status=job["status"])
        self.melden(f"Stapel: {done} Videos berechnet; {len(ready)-done} noch offen.")
        return done, max(0,len(ready)-done)

    def einmal(self):
        self.sperren()
        try:
            self.vorbereiten()
            return self.stapel()
        finally:
            self.freigeben()

    def beobachten(self):
        self.sperren()
        try:
            self.melden("Automatik gestartet.")
            while not self.stop.is_set():
                try:
                    self.vorbereiten()
                    self.stapel()
                except (OSError, RuntimeError, ValueError) as exc:
                    self.melden("Automatik: " + str(exc))
                self.stop.wait(self.cfg["intervall"])
        finally:
            self.freigeben()
