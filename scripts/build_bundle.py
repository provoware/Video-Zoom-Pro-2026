#!/usr/bin/env python3
"""Reproduzierbarer Offline-Entwicklungskandidat, keine Stable-Veröffentlichung."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from videozoom import __version__

PROGRAMM = (
    "STARTEN.sh",
    "README.md",
    "config/formate.json",
    "docs/KUBUNTU_ABNAHME.md",
    "docs/SICHERHEIT.md",
    "videozoom/__init__.py",
    "videozoom/__main__.py",
    "videozoom/core.py",
    "videozoom/eingang.py",
    "videozoom/lebenszyklus.py",
    "videozoom/auftraege.py",
    "videozoom/vorschau.py",
    "videozoom/einstellungen_sicher.py",
    "videozoom/render_watchdog.py",
    "videozoom/wav_eingang.py",
    "videozoom/diagnose.py",
    "videozoom/sensoren.py",
    "videozoom/webui.py",
    "scripts/kubuntu_abnahme.py",
)
ROOT_NAME = "Video-Zoom-Pro-2026"


def inhalt() -> dict[str, bytes]:
    """Nur einzeln zugelassene Dateien, keine Nutzerdaten oder Entwicklerreste."""
    result = {}
    for name in PROGRAMM:
        source = ROOT / name
        if source.is_symlink() or not source.is_file():
            raise RuntimeError("Benötigte Programmdatei fehlt oder ist unsicher: " + name)
        if source.resolve().parent != (ROOT / name).parent.resolve():
            raise RuntimeError("Unerwarteter Paketpfad: " + name)
        result[name] = source.read_bytes()
    return result


def manifest(dateien: dict[str, bytes]) -> bytes:
    eintraege = {
        name: {"sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}
        for name, data in sorted(dateien.items())
    }
    info = {
        "schema": 1,
        "produkt": "PROVOWARE Video Zoom Pro",
        "version": __version__,
        "kanal": "ENTWICKLUNGSKANDIDAT",
        "stable": False,
        "dateien": eintraege,
        "hinweis": "Kubuntu-Endabnahme und Lizenzentscheidung noch offen.",
    }
    return (json.dumps(info, indent=2, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8")


def bundle(ziel: Path) -> dict:
    dateien = inhalt()
    dateien["MANIFEST.json"] = manifest(dateien)
    ziel = ziel.expanduser().absolute()
    ziel.parent.mkdir(parents=True, exist_ok=True)
    if ziel.exists() or ziel.is_symlink():
        raise FileExistsError("Vorhandenes ZIP bleibt unverändert: " + str(ziel))
    tmp = None
    try:
        fd, name = tempfile.mkstemp(prefix=".provoware-kandidat-", suffix=".tmp",
                                    dir=str(ziel.parent))
        tmp = Path(name)
        with os.fdopen(fd, "wb") as stream:
            with zipfile.ZipFile(stream, mode="w", compression=zipfile.ZIP_DEFLATED,
                                 compresslevel=6) as archive:
                for rel, data in sorted(dateien.items()):
                    item = zipfile.ZipInfo(ROOT_NAME + "/" + rel, (1980, 1, 1, 0, 0, 0))
                    item.compress_type = zipfile.ZIP_DEFLATED
                    item.external_attr = ((0o100755 if rel == "STARTEN.sh" else 0o100644) << 16)
                    archive.writestr(item, data, compress_type=zipfile.ZIP_DEFLATED)
            stream.flush()
            os.fsync(stream.fileno())
        with zipfile.ZipFile(tmp) as check:
            if len(check.namelist()) != len(dateien) or check.testzip() is not None:
                raise RuntimeError("ZIP-Prüfung fehlgeschlagen.")
            for rel, data in dateien.items():
                if check.read(ROOT_NAME + "/" + rel) != data:
                    raise RuntimeError("Dateiprüfung fehlgeschlagen: " + rel)
        os.link(tmp, ziel)
        digest = hashlib.sha256(ziel.read_bytes()).hexdigest()
        return {"datei": str(ziel), "sha256": digest,
                "dateien": len(dateien), "stable": False,
                "version": __version__}
    finally:
        if tmp is not None:
            tmp.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Offline-Entwicklungspaket erstellen")
    parser.add_argument("--ziel", type=Path,
                        default=ROOT / "dist" / f"Video-Zoom-Pro_{__version__}_KANDIDAT.zip")
    args = parser.parse_args()
    print(json.dumps(bundle(args.ziel), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
