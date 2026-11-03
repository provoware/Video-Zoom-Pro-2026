"""Startprüfung ohne Tk. Systempakete nur nach Simulation und Zustimmung."""
from __future__ import annotations
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys


def run(args, timeout=20):
    try:
        p = subprocess.run(args, capture_output=True, text=True, timeout=timeout, check=False)
        return p.returncode == 0, p.stdout + "\n" + p.stderr
    except (OSError, subprocess.TimeoutExpired) as exc:
        return False, str(exc)


def scope_verfuegbar(cfg: dict | None = None):
    """Prüft exakt dieselben Grenzwerte wie der konkrete Videoauftrag."""
    if not shutil.which("systemd-run"):
        return False
    from .core import konfiguration, quota_befehl

    command = quota_befehl(["/usr/bin/true"], cfg if cfg is not None else konfiguration())
    ok, _ = run(command, 10)
    return ok


def pruefen(real_scope=True, cfg: dict | None = None):
    checks = []
    actions = {
        "Python":"Python 3.11 oder neuer über die Systemverwaltung bereitstellen.",
        "ffmpeg":"FFmpeg über die angebotene, vorher simulierte Reparatur installieren.",
        "ffprobe":"FFmpeg-Paket über die angebotene, vorher simulierte Reparatur prüfen.",
        "Filter":"FFmpeg-Paket und benötigte Filter über die Systemverwaltung prüfen.",
        "Kodierer":"FFmpeg mit libx264 und AAC über die Systemverwaltung bereitstellen.",
        "Begrenzung":"Im normalen Linux-Benutzerkonto mit aktiver systemd-Benutzersitzung starten.",
        "Downloads":"Vorhandenen beschreibbaren Downloads-Ordner wählen und Einstellungen speichern.",
        "Arbeitsordner":"Eigenen beschreibbaren Arbeitsordner außerhalb der Downloads wählen und speichern.",
    }
    def add(name, ok, detail):
        checks.append({"name":name,"ok":bool(ok),"hinweis":detail,
                       "handlung":"Keine Korrektur nötig." if ok else actions.get(name,"Einstellung prüfen.")})
    from .core import konfigurieren
    config = konfigurieren(cfg or {})
    downloads = Path(config["downloads"]).expanduser().absolute()
    arbeit = Path(config["arbeitsordner"]).expanduser().absolute()
    def sicher(p):
        return not any(x.is_symlink() for x in (p,*p.parents))
    add("Downloads",downloads.is_dir() and sicher(downloads) and os.access(downloads,os.R_OK|os.W_OK|os.X_OK),
        "Eingangsordner muss vorhanden, lesbar und beschreibbar sein.")
    try:
        from .eingang import ordner_pruefen
        folders=ordner_pruefen(config)
        arbeits_ok=next(p['ok'] for p in folders['ordner'] if p['name']=='Arbeitsordner')
    except (ValueError,RuntimeError,OSError):
        arbeits_ok=False
    add("Arbeitsordner",arbeits_ok,"Eigener vorhandener Arbeitsordner außerhalb des Eingangs; über Ordner prüfen & anlegen einrichten.")
    add("Python",sys.version_info >= (3,11),"Mindestens Python 3.11.")
    for name in ("ffmpeg","ffprobe"):
        vorhanden = bool(shutil.which(name))
        ok, version = run([name,"-version"],5) if vorhanden else (False,"")
        add(name, vorhanden and ok,
            version.splitlines()[0][:200] if ok and version.splitlines() else "Wird zur lokalen Medienprüfung benötigt.")
    if shutil.which("ffmpeg"):
        ok, raw = run(["ffmpeg","-hide_banner","-filters"],12)
        present = set(re.findall(r"(?m)^\s*[TSC\.]{3}\s+(\w+)\s",raw))
        missing = sorted({"zoompan","xfade","concat","scale","pad"} - present)
        add("Filter",ok and not missing,", ".join(missing) or "Verfügbar.")
        ok, raw = run(["ffmpeg","-hide_banner","-encoders"],12)
        present = set(re.findall(r"(?m)^\s*[VAS\.FSXBD]{6}\s+(\w+)\s",raw))
        missing = sorted({"libx264","aac"} - present)
        add("Kodierer",ok and not missing,", ".join(missing) or "Verfügbar.")
    if real_scope:
        add("Begrenzung",scope_verfuegbar(cfg),"CPU und RAM werden über systemd begrenzt.")
    return {"pruefungen":checks,"startbereit":all(c["ok"] for c in checks)}


def installation_simulieren(pakete):
    if set(pakete) != {"ffmpeg"} or not shutil.which("apt-get"):
        return {"sicher":False,"grund":"Nur FFmpeg darf automatisch zur Installation vorgeschlagen werden."}
    ok, raw = run(["apt-get","-s","install","--no-install-recommends","ffmpeg"],25)
    entfernt = re.findall(r"(?m)^Remv\s+(\S+)",raw)
    aktualisiert = re.findall(r"(?m)^Inst\s+\S+\s+\[[^]]+\]",raw)
    return {"sicher":bool(ok and not entfernt and not aktualisiert),
            "entfernt":entfernt,"aktualisiert":aktualisiert}


def reparatur(frage):
    if shutil.which("ffmpeg") and shutil.which("ffprobe"):
        return "FFmpeg und FFprobe sind vorhanden."
    plan = installation_simulieren(["ffmpeg"])
    if not plan["sicher"]:
        return "Systemänderung verhindert: " + str(plan)
    if not frage("FFmpeg fehlt. Sicher geprüfte Pakete installieren?"):
        return "Keine Installation ohne Zustimmung."
    cmd = ["/usr/bin/apt-get","install","-y","--no-install-recommends","ffmpeg"]
    if os.geteuid() != 0:
        if not shutil.which("pkexec"): return "pkexec fehlt. Installation manuell starten."
        cmd.insert(0,shutil.which("pkexec"))
    ok, _ = run(cmd,180)
    return "Installation erfolgreich." if ok else "Installation fehlgeschlagen."
