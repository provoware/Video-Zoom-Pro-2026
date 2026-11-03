"""Kurze echte Vorschau: gleiche Regie, kleines Format, keine Archivierung."""
import os
from pathlib import Path
import re
import secrets

from .auftraege import quellen
from .core import (ffmpeg_befehl, quota_befehl, speicher_pruefen, regulaer,
                   pruefsumme, medieninfo, ProduktionGestoppt)
from .render_watchdog import rendern


def erzeugen(workflow, key):
    from .diagnose import scope_verfuegbar
    job, paths = quellen(workflow, key)
    if job.get("status") not in {"BEREIT", "PAUSIERT", "PRUEFEN"}:
        raise ValueError("Vorschau nur für vorbereitete, noch nicht archivierte Songs.")
    if not workflow.testmodus and not scope_verfuegbar(workflow.cfg):
        raise RuntimeError("CPU-/RAM-Begrenzung fehlt. Vorschau bleibt gesperrt.")
    folder = workflow.ordner / "VORSCHAU"
    if any(p.is_symlink() for p in (folder, *folder.parents)):
        raise RuntimeError("Unsicherer Vorschauordner; Originale unverändert.")
    folder.mkdir(exist_ok=True)
    speicher_pruefen(folder, 64 * 1024**2)
    path = folder / (secrets.token_hex(16) + ".mp4")
    part = path.with_suffix(".teil.mp4")
    cmd = ffmpeg_befehl(paths[0], paths[1:], part, job["laenge"], workflow.cfg, vorschau=True)
    if not workflow.testmodus:
        cmd = quota_befehl(cmd, workflow.cfg)
    workflow.fortschreiben("vorschau", 0, titel=job["titel"], hinweis="Nur Vorschau; keine Archivierung.")
    try:
        rendern(cmd, workflow.stop, lambda _: None, workflow.melden)
        quellen(workflow, key)  # Quellenänderung während der Vorschau verhindert Veröffentlichung.
        info = medieninfo(part)
        if {s.get("codec_type") for s in info.get("streams", [])} != {"audio", "video"}:
            raise RuntimeError("Vorschau enthält nicht Bild und Ton.")
        if abs(float(info["format"]["duration"]) - min(10, job["laenge"])) > .25:
            raise RuntimeError("Vorschau hat eine falsche Dauer.")
        # Die kurze Datei vollständig lesen; dieselbe Ressourcenhülle wie beim Rendern.
        check = ["ffmpeg", "-v", "error", "-nostdin", "-xerror", "-err_detect", "explode",
                 "-i", str(part), "-threads", "2", "-f", "null", "-progress", "pipe:1", "-"]
        if not workflow.testmodus:
            check = quota_befehl(check, workflow.cfg)
        rendern(check, workflow.stop, lambda _: None, workflow.melden)
        with part.open("rb") as stream:
            os.fsync(stream.fileno())
        os.link(part, path, follow_symlinks=False)
        part.unlink()
        job["vorschau"] = {"pfad": str(path), "sha256": pruefsumme(path),
                           "dauer": min(10, job["laenge"])}
        workflow.speichern()
        workflow.melden(job["titel"] + ": Vorschau bereit; Produktionsstatus unverändert.")
        return path
    finally:
        if regulaer(part):
            part.unlink()  # Nur eigene kurze Zwischenvorschau, niemals Originalmedien.


def datei(workfolder, job):
    """Nur eindeutig veröffentlichte Vorschau aus dem eigenen Vorschauordner."""
    meta = job.get("vorschau") or {}
    path = Path(meta.get("pfad", ""))
    if (path.parent != Path(workfolder) / "VORSCHAU"
            or not re.fullmatch(r"[0-9a-f]{32}\.mp4", path.name)
            or any(p.is_symlink() for p in (path, *path.parents))
            or not regulaer(path) or pruefsumme(path) != meta.get("sha256")):
        raise RuntimeError("Vorschau fehlt oder ist verändert. Erneut erzeugen.")
    return path


def senden(handler, path):
    """Lokale Videowiedergabe mit begrenzten Einzelbereichsanfragen."""
    size = path.stat().st_size
    start, end = 0, size - 1
    range_header = handler.headers.get("Range")
    if range_header:
        match = re.fullmatch(r"bytes=(\d+)-(\d*)", range_header)
        if not match:
            handler.antwort({"fehler": "Ungültiger Videobereich"}, 416)
            return
        start = int(match[1]); end = min(end, int(match[2]) if match[2] else end)
        if start > end:
            handler.antwort({"fehler": "Videobereich außerhalb der Datei"}, 416)
            return
    handler.send_response(206 if range_header else 200)
    handler.send_header("Content-Type", "video/mp4")
    handler.send_header("Content-Length", str(end-start+1))
    handler.send_header("Accept-Ranges", "bytes")
    handler.send_header("Cache-Control", "no-store")
    handler.send_header("X-Content-Type-Options", "nosniff")
    handler.send_header("Content-Security-Policy", "default-src 'none'")
    if range_header:
        handler.send_header("Content-Range", f"bytes {start}-{end}/{size}")
    handler.end_headers()
    handler.connection.settimeout(20)
    try:
        with path.open("rb") as stream:
            stream.seek(start)
            left = end-start+1
            while left:
                block = stream.read(min(65536, left))
                if not block:
                    break
                handler.wfile.write(block)
                left -= len(block)
    except (BrokenPipeError, ConnectionResetError, TimeoutError):
        pass  # Browserabbruch stoppt keine Produktion.
