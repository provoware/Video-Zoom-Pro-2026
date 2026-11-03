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


def quellen(workflow, key, job=None):
    """Keine freien Pfade aus Browserdaten; nur Manifest im erlaubten Songbereich."""
    from .core import regulaer, pruefsumme
    job = workflow.zustand["auftraege"].get(key) if job is None else job
    if not job or not job.get("dateien"):
        raise ValueError("Auftrag hat noch keine bestätigten Medien. Zuerst vorbereiten.")
    paths = []
    for index, entry in enumerate(job["dateien"]):
        p = Path(entry["pfad"])
        if not p.is_absolute() or any(x.is_symlink() for x in (p, *p.parents)):
            raise RuntimeError("Unsichere Quelle; keine Datei verändert.")
        if index == 0:
            from .eingang import audio_erlaubt
            erlaubt = audio_erlaubt(p, workflow.downloads, workflow.ordner)
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


def erneut_vorbereiten(workflow, key, job):
    """Nur bewusst gewählten Altauftrag ohne Manifest erneut vorbereiten."""
    import hashlib
    from .core import (titel, slug, stabil, pruefsumme, vollstaendig, dauer,
                       zeitplan, BILDTYPEN)
    candidates = []
    from .eingang import audio_dateien
    for audio in audio_dateien(workflow,alle=True):
        if titel(audio.name) != job.get("titel") or not stabil(audio):
            continue
        pathkey = hashlib.sha256(str(audio).encode()).hexdigest()[:24]
        if pathkey == key:
            candidates.append(audio)
        else:
            try:
                vollstaendig(audio)
                revision = hashlib.sha256((str(audio) + "\0" + pruefsumme(audio)).encode()).hexdigest()[:24]
            except (OSError, ValueError):
                continue  # Fremder unvollständiger Titelzwilling blockiert keine Einzelprüfung.
            if revision == key:
                candidates.append(audio)
    if len(candidates) != 1:
        raise RuntimeError("Keine eindeutige vollständige WAV für diesen Auftrag. Originaldatei prüfen.")
    audio = candidates[0]
    folder = workflow.ordner / "EINGANG" / slug(titel(audio.name)) / "BILDER"
    if any(p.is_symlink() for p in (folder, *folder.parents)) or not folder.is_dir():
        raise RuntimeError("Bilderordner fehlt oder ist unsicher. Keine Freigabe.")
    images = sorted(p for p in folder.iterdir() if p.suffix.lower() in BILDTYPEN and stabil(p))
    vollstaendig(audio)
    length = dauer(audio)
    zeitplan(length, len(images), workflow.cfg["fps"], workflow.cfg["uebergang"])
    manifest = [{"pfad": str(p), "sha256": pruefsumme(p), "groesse": p.stat().st_size,
                 "mtime_ns": p.stat().st_mtime_ns} for p in [audio, *images]]
    candidate = {**job, "dateien": manifest, "laenge": length}
    candidate.pop("vorschau", None)
    quellen(workflow, key, candidate)
    return candidate


def freigeben(workflow, key):
    """Bewusste Einzelaktion; fertige Videos niemals erneut rendern."""
    from .core import regulaer, pruefsumme, vollstaendig, dauer, video_gueltig
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
        if not video_gueltig(video, job["laenge"], job.get("render_cfg", workflow.cfg),
                              stop=workflow.stop, testmodus=workflow.testmodus):
            raise RuntimeError("Videoprüfung fehlgeschlagen; Auftrag bleibt gesperrt und Quellen geschützt.")
        job["video"] = str(video)
        job["video_hash"] = job.get("video_hash") or job["render_hash"]
        job["status"] = "ARCHIV_WARTET"
        job["archiv_versuche"] = 0
        job["archiv_retry_after"] = 0
    else:
        candidate = job if job.get("dateien") else erneut_vorbereiten(workflow, key, job)
        _, paths = quellen(workflow, key, candidate)
        vollstaendig(paths[0])
        if abs(dauer(paths[0]) - candidate["laenge"]) > .01:
            raise RuntimeError("Songlänge stimmt nicht mehr. Keine Freigabe.")
        job.update(candidate)
        job["status"] = "BEREIT"
        job["versuche"] = 0
        job.pop("retry_after", None)
    job["hinweis"] = "Nach bewusster Einzelprüfung erneut freigegeben."
    workflow.speichern()
    workflow.melden(job["titel"] + ": erneut freigegeben; Originale unverändert.")
