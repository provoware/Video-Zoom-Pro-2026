"""Lesbare Auftragsübersicht und kontrollierter Zugriff auf gespeicherte Quellen."""
from pathlib import Path


def uebersicht(auftraege, cfg):
    result = []
    for key, job in list(auftraege.items()):
        if not isinstance(job, dict):
            raise RuntimeError("Ungültiger gespeicherter Auftrag.")
        result.append({"id": key, "titel": job.get("titel", "Unbenannter Song"),
                       "status": job["status"], "hinweis": job.get("hinweis", ""),
                       "format": job.get("render_cfg", cfg).get("format", cfg["format"]),
                       "bilder": max(0, len(job.get("dateien", [])) - 1),
                       "versuche": job.get("versuche", 0),
                       "vorschau": bool(job.get("vorschau")),
                       "vorschau_id": job.get("vorschau", {}).get("sha256", "")})
    return result


def quellen(workflow, key):
    """Keine freien Pfade aus Browserdaten; nur Manifest im erlaubten Songbereich."""
    from .core import regulaer, pruefsumme
    job = workflow.zustand["auftraege"].get(key)
    if not job or not job.get("dateien"):
        raise ValueError("Auftrag hat noch keine bestätigten Medien. Zuerst vorbereiten.")
    paths = []
    for index, entry in enumerate(job["dateien"]):
        p = Path(entry["pfad"])
        if not p.is_absolute() or any(x.is_symlink() for x in (p, *p.parents)):
            raise RuntimeError("Unsichere Quelle; keine Datei verändert.")
        if index == 0:
            erlaubt = p.parent == workflow.downloads and p.suffix.lower() == ".wav"
        else:
            from .core import BILDTYPEN
            erlaubt = (p.suffix.lower() in BILDTYPEN and p.parent.name == "BILDER"
                       and p.parent.parent.parent == workflow.ordner / "EINGANG")
        if not erlaubt or not regulaer(p) or pruefsumme(p) != entry["sha256"]:
            raise RuntimeError("Quelle fehlt, liegt außerhalb des Songbereichs oder wurde verändert. Original prüfen.")
        paths.append(p)
    if len(paths) < 2:
        raise ValueError("Mindestens ein bestätigtes Bild erforderlich.")
    return job, paths


def freigeben(workflow, key):
    """Bewusste Einzelaktion; fertige Videos niemals erneut rendern."""
    from .core import regulaer, pruefsumme, vollstaendig, dauer
    job = workflow.zustand["auftraege"].get(key)
    if not job or job.get("status") not in {"PRUEFEN", "PAUSIERT"}:
        raise ValueError("Nur einen pausierten oder zu prüfenden Auftrag erneut freigeben.")
    if job.get("video") or job.get("render_hash"):
        # Quellteile dürfen nach einem Archivabbruch bereits sicher verschoben sein.
        video = Path(job.get("video") or job.get("video_ziel", ""))
        if (video.parent != workflow.ordner / "FERTIG" or not regulaer(video)
                or any(p.is_symlink() for p in video.parents)
                or pruefsumme(video) != (job.get("video_hash") or job.get("render_hash"))):
            raise RuntimeError("Bestätigtes Video fehlt oder wurde verändert; keine neue Berechnung freigegeben.")
        job["video"] = str(video)
        job["video_hash"] = job.get("video_hash") or job["render_hash"]
        job["status"] = "ARCHIV_WARTET"
        job["archiv_versuche"] = 0
        job["archiv_retry_after"] = 0
    else:
        job, paths = quellen(workflow, key)
        vollstaendig(paths[0])
        if abs(dauer(paths[0]) - job["laenge"]) > .01:
            raise RuntimeError("Songlänge stimmt nicht mehr. Keine Freigabe.")
        job["status"] = "BEREIT"
        job["versuche"] = 0
        job.pop("retry_after", None)
    job["hinweis"] = "Nach bewusster Einzelprüfung erneut freigegeben."
    workflow.speichern()
    workflow.melden(job["titel"] + ": erneut freigegeben; Originale unverändert.")
