#!/usr/bin/env python3
"""Kubuntu-Endabnahme vorbereiten und Linux-cgroup-Limits messbar pruefen.

Ohne Tk, Netzwerk, Rootrechte oder Fremddateien. CPU-Lastprobe nur nach
ausdruecklicher CLI-Option --cpu-test. Sichtpruefungen bleiben offen.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from videozoom.core import konfiguration, konfigurieren, lesen, quota_befehl, json_sicher

# Laeuft innerhalb des systemd-Scopes: kontrollierte Last, max. 3 Sekunden.
# Prozesse werden im Scope automatisch gemeinsam begrenzt.
SCOPE_CHILD = r'''
import json, os, pathlib, time
record = next((line.split("::", 1)[1] for line in
               pathlib.Path("/proc/self/cgroup").read_text().splitlines()
               if line.startswith("0::")), None)
if record is None:
    raise SystemExit("Linux cgroup v2 fehlt")
base = pathlib.Path("/sys/fs/cgroup") / record.lstrip("/")
cpu = (base / "cpu.max").read_text().strip()
memory = (base / "memory.max").read_text().strip()
def usage():
    return int(next(line.split()[1] for line in
                    (base / "cpu.stat").read_text().splitlines()
                    if line.startswith("usage_usec ")))
before = usage()
begin = time.monotonic()
deadline = begin + 2.5
# Bei kleiner RAM-Grenze bewusst nur wenige Lastprozesse erzeugen.
ram_bytes = int(memory) if memory != "max" else 256 * 1024 * 1024
count = max(1, min(32, len(os.sched_getaffinity(0)),
                   max(1, ram_bytes // (64 * 1024 * 1024))))
kids = []
for _ in range(max(1, count)):
    pid = os.fork()
    if pid == 0:
        value = 0
        while time.monotonic() < deadline:
            value = (value * 17 + 7) % 999983
        os._exit(0)
    kids.append(pid)
for pid in kids:
    os.waitpid(pid, 0)
elapsed = max(.001, time.monotonic() - begin)
after = usage()
print(json.dumps({
    "cpu_max": cpu, "memory_max": memory, "sekunden": elapsed,
    "gemessene_cpu_kerne": (after - before) / 1000000 / elapsed,
    "lastprozesse": count, "cgroup_pfad": record
}), flush=True)
'''


def desktop_info() -> dict:
    return {
        "system": platform.system(),
        "distribution": _distribution(),
        "desktop": os.environ.get("XDG_CURRENT_DESKTOP", "unbekannt"),
        "session": os.environ.get("XDG_SESSION_TYPE", "unbekannt"),
        "wayland": bool(os.environ.get("WAYLAND_DISPLAY")),
        "logische_cpu_zugaenglich": (
            len(os.sched_getaffinity(0)) if hasattr(os, "sched_getaffinity")
            else os.cpu_count() or 1
        ),
        "python": platform.python_version(),
        "ffmpeg": bool(shutil.which("ffmpeg")),
        "ffprobe": bool(shutil.which("ffprobe")),
        "systemd_run": bool(shutil.which("systemd-run")),
        "kdialog": bool(shutil.which("kdialog")),
        "zenity": bool(shutil.which("zenity")),
    }


def _distribution() -> str:
    try:
        for line in Path("/etc/os-release").read_text(encoding="utf-8").splitlines():
            if line.startswith("PRETTY_NAME="):
                return line.partition("=")[2].strip().strip('"')
    except OSError:
        pass
    return "unbekannt"


def grenzen_auswerten(werte: dict, cfg: dict, cpus: int) -> dict:
    """Messwert und konfigurierte cgroup-Grenze muessen zusammenpassen."""
    try:
        quote, period = werte["cpu_max"].split()
        q = float(quote) / float(period) if quote != "max" else None
        limit = float(werte["memory_max"]) if werte["memory_max"] != "max" else None
        measured = float(werte["gemessene_cpu_kerne"])
        expected = cpus * int(cfg["cpu_prozent"]) / 100
        mem_max = int(cfg["ram_mb"]) * 1024 * 1024
        if q is None or limit is None or q <= 0 or period == "0":
            raise ValueError("Keine aktive CPU- oder RAM-Grenze.")
        # cgroup kann Werte geringfuegig runden.
        exact = abs(q - expected) <= .02 and 0 < limit <= mem_max
        under_limit = 0 <= measured <= q * 1.20 + .10
        return {
            "status": "BESTANDEN" if exact and under_limit else "PRUEFEN",
            "cpu_quote_kerne": q,
            "soll_cpu_kerne": expected,
            "gemessene_cpu_kerne": measured,
            "ram_grenze_bytes": limit,
            "soll_ram_max_bytes": mem_max,
            "regel_aktiv": exact,
            "last_unter_grenze": under_limit,
            "hinweis": ("Die Konfiguration ist nachgewiesen. Die Messung unter Last zeigt "
                        "nur diese Testphase, keinen unbegrenzten Langzeitnachweis."),
        }
    except (KeyError, ValueError, TypeError, ZeroDivisionError) as exc:
        return {"status": "NICHT_BESTANDEN", "grund": str(exc)}


def cpu_scope_pruefen(cfg: dict, cpus: int) -> dict:
    if not shutil.which("systemd-run"):
        return {"status": "NICHT_VERFUEGBAR", "grund": "systemd-run fehlt."}
    command = quota_befehl([sys.executable, "-c", SCOPE_CHILD], cfg)
    try:
        check = subprocess.run(command, capture_output=True, text=True,
                               check=False, timeout=40)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"status": "NICHT_BESTANDEN", "grund": str(exc)}
    if check.returncode:
        return {"status": "NICHT_BESTANDEN",
                "grund": (check.stderr or check.stdout)[-600:]}
    try:
        line = next(item for item in reversed(check.stdout.splitlines())
                    if item.lstrip().startswith("{"))
        report = json.loads(line)
    except (ValueError, StopIteration, json.JSONDecodeError) as exc:
        return {"status": "NICHT_BESTANDEN",
                "grund": "Kein lesbarer cgroup-Messbericht: " + str(exc)}
    return {"messung": report, **grenzen_auswerten(report, cfg, cpus)}


def abnahmebericht(cpu_test: bool = False) -> dict:
    system = desktop_info()
    settings = Path(os.environ.get("XDG_CONFIG_HOME",
                      str(Path.home() / ".config"))) / "video-zoom-pro" / "settings.json"
    cfg = konfigurieren(lesen(settings, konfiguration()))
    cpu = (cpu_scope_pruefen(cfg, system["logische_cpu_zugaenglich"])
           if cpu_test else {"status": "OFFEN", "grund": "Nur mit --cpu-test messen."})
    return {
        "schema": 1,
        "zeit_utc": datetime.now(timezone.utc).isoformat(),
        "system": system,
        "cpu_ram": cpu,
        "sichtpruefung": {
            "auflosung_800x600": "OFFEN",
            "zoom_100_125_150_200_prozent": "OFFEN",
            "tastatur_und_fokus": "OFFEN",
            "echt_KDE_Ordnerdialog": "OFFEN",
            "original_medien_und_langzeitbetrieb": "OFFEN",
        },
        "stable_freigabe": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Kubuntu-Abnahme: Diagnose + optionale echte CPU-Messung")
    parser.add_argument("--cpu-test", action="store_true", help="2,5 Sekunden begrenzte Last im eigenen systemd-Scope")
    parser.add_argument("--bericht", type=Path, help="Lokale JSON-Datei fuer den Diagnosebericht")
    args = parser.parse_args()
    result = abnahmebericht(args.cpu_test)
    if args.bericht:
        json_sicher(args.bericht, result)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if args.cpu_test and result["cpu_ram"]["status"] != "BESTANDEN":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
