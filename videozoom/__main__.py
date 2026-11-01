"""Linux-Start: Browseroberfläche oder getrennte Arbeitsphasen."""
from __future__ import annotations
import argparse
import json
import os
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
    if args.doctor:
        print(json.dumps(pruefen(),ensure_ascii=False,indent=2))
        return 0
    if args.reparatur:
        def fragen(prompt):
            return sys.stdin.isatty() and input(prompt+" [j/N] ").lower().strip() in ("j","ja")
        print(reparatur(fragen))
    cfg = konfigurieren(lesen(SETTINGS,konfiguration()))
    for key in ("downloads","arbeitsordner","format"):
        val = getattr(args,key)
        if val is not None: cfg[key] = str(val)
    if not any((args.vorbereiten,args.stapel,args.einmal,args.beobachten)):
        from .webui import starten
        starten(cfg,SETTINGS)
        return 0
    service = Workflow(cfg,print)
    if args.beobachten:
        service.beobachten()
    else:
        service.sperren()
        try:
            if args.vorbereiten or args.einmal: print("Bereit/Wartend:",service.vorbereiten())
            if args.stapel or args.einmal: print("Fertig/Offen:",service.stapel())
        finally:
            service.freigeben()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
