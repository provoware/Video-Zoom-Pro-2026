"""Linux-Start: Browseroberfläche oder getrennte Arbeitsphasen."""
from __future__ import annotations
import argparse
import json
import os
import shutil
import subprocess
from pathlib import Path
import sys
from .core import Workflow, konfiguration, konfigurieren, lesen
from .diagnose import pruefen, reparatur

SETTINGS = Path(os.environ.get("XDG_CONFIG_HOME",str(Path.home()/".config"))) / "video-zoom-pro"/"settings.json"


def main(argv=None):
    p = argparse.ArgumentParser(description="PROVOWARE Video Zoom Pro – ohne Tk")
    g = p.add_mutually_exclusive_group()
    for flag in ("vorbereiten","stapel","einmal","beobachten","doctor"):
        g.add_argument("--"+flag,action="store_true")
    p.add_argument("--reparatur",action="store_true",help="Installation nur nach Zustimmung")
    p.add_argument("--downloads",type=Path)
    p.add_argument("--arbeitsordner",type=Path)
    p.add_argument("--format",choices=["BREI","HOCH","QUAD","KLAS","4K"])
    args = p.parse_args(argv)
    # Dieselbe Konfiguration fuer Diagnose, grafischen Start und Stapel.
    cfg = konfigurieren(lesen(SETTINGS, konfiguration()))
    for key in ("downloads", "arbeitsordner", "format"):
        val = getattr(args, key)
        if val is not None:
            cfg[key] = str(val)
    cfg = konfigurieren(cfg)
    if args.doctor:
        bericht = pruefen(cfg=cfg)
        print(json.dumps(bericht, ensure_ascii=False, indent=2))
        return 0 if bericht.get("startbereit") is True else 1
    def fragen(prompt):
        if sys.stdin.isatty():
            return input(prompt+" [j/N] ").lower().strip() in ("j","ja")
        if os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"):
            for name, command in (
                ("kdialog", ["kdialog", "--yesno", prompt]),
                ("zenity", ["zenity", "--question", "--text", prompt]),
            ):
                if shutil.which(name):
                    try:
                        return subprocess.run(command, check=False, timeout=120).returncode == 0
                    except (OSError, subprocess.TimeoutExpired):
                        return False  # Ohne eindeutige Zustimmung nie installieren.
        return False

    # Fehlende Komponenten beim Start erkennen; niemals ohne Zustimmung installieren.
    if args.reparatur or not (shutil.which("ffmpeg") and shutil.which("ffprobe")):
        print(reparatur(fragen))
    if not any((args.vorbereiten,args.stapel,args.einmal,args.beobachten)):
        from .webui import starten
        starten(cfg,SETTINGS)
        return 0
    service = Workflow(cfg,print)
    from .lebenszyklus import abbruchsignale
    with abbruchsignale(service.stop):
        if args.beobachten:
            service.beobachten()
        else:
            service.sperren()
            try:
                if args.vorbereiten or args.einmal: print("Bereit/Wartend:",service.vorbereiten())
                if args.stapel or args.einmal: print("Fertig/Offen:",service.stapel())
            finally:
                try:service.speichern()
                finally:service.freigeben()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
