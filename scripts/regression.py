#!/usr/bin/env python3
"""Auswirkungsbasierter Regressionstest: unklare Aenderungen -> kompletter Lauf."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

SAFETY_CASES = (
    "tests.test_workflow.Regeln.test_journal_sicher",
    "tests.test_workflow.Regeln.test_archiv_kollision_und_wiederaufnahme",
    "tests.test_workflow.Regeln.test_paket_aenderungen_verhindern",
)
AUSWIRKUNGEN = {
    "videozoom/core.py": (
        "tests.test_workflow", "tests.test_recovery", "tests.test_archive_recovery",
        "tests.test_progress", "tests.test_category_quota", "tests.test_archive_evidence",
    ),
    "videozoom/diagnose.py": ("tests.test_workflow", "tests.test_category_quota"),
    "videozoom/sensoren.py": ("tests.test_workflow",),
    "videozoom/webui.py": (
        "tests.test_webui", "tests.test_workflow", "tests.test_progress",
        "tests.test_start_status", "tests.test_ui_theme", "tests.test_ui_polish",
        "tests.test_visual_layout",
    ),
    "videozoom/__main__.py": ("tests.test_cli_settings", "tests.test_zip_smoke", "tests.test_workflow", "tests.test_webui"),
    "videozoom/__init__.py": ("tests.test_workflow", "tests.test_webui"),
    "tests/fixtures/generieren.py": ("tests.test_workflow",),
    "config/formate.json": ("tests.test_workflow",),
    "STARTEN.sh": ("tests.test_workflow", "tests.test_webui"),
}
DOKU = ("docs/", "README.md", "AGENTS.md", ".gitignore")
QUALITAET = ("scripts/regression.py", ".github/workflows/ci.yml")


def betroffene(dateien: list[str]) -> tuple[bool, tuple[str, ...], str]:
    """True bedeutet kompletter Lauf: niemals sicherheitsblind selektieren."""
    if not dateien:
        return True, (), "Keine Aenderungsliste: sicherheitshalber Gesamtpruefung."
    if any(p in {"videozoom/core.py", "videozoom/render_watchdog.py"} for p in dateien):
        return True, (), "Medien-/Archiv-/Prozessgrenze geaendert: Gesamtpruefung."
    module: set[str] = set()
    for pfad in dateien:
        pfad = pfad.replace("\\", "/").lstrip("./")
        if pfad in AUSWIRKUNGEN:
            module.update(AUSWIRKUNGEN[pfad])
        elif pfad.startswith("tests/") and pfad.endswith(".py"):
            module.add(pfad[:-3].replace("/", "."))
        elif pfad.startswith("docs/") or pfad in DOKU:
            continue
        elif pfad in QUALITAET:
            return True, (), "Pruef-Infrastruktur geaendert: Gesamtpruefung."
        else:
            return True, (), "Unbekannter Einfluss (" + pfad + "): Gesamtpruefung."
    return False, tuple(sorted(module)), "Betroffene Module + verpflichtende Schutztests."


def aenderungen(base: str) -> list[str] | None:
    try:
        prozess = subprocess.run(
            ["git", "diff", "--name-only", "--no-ext-diff", base + "...HEAD"],
            cwd=ROOT, capture_output=True, text=True, timeout=15, check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if prozess.returncode:
        return None
    return [line for line in prozess.stdout.splitlines() if line]


def laden(alle: bool, module: tuple[str, ...]) -> unittest.TestSuite:
    loader = unittest.TestLoader()
    if alle:
        return loader.discover(str(ROOT / "tests"), pattern="test_*.py", top_level_dir=str(ROOT))
    suite = unittest.TestSuite()
    for name in (*SAFETY_CASES, *module):
        if name == "tests.test_recovery" and not (ROOT / "tests" / "test_recovery.py").is_file():
            continue
        suite.addTests(loader.loadTestsFromName(name))
    return suite


def durchlauf(*, alles: bool = False, pfade: list[str] | None = None,
              base: str | None = None) -> tuple[int, dict]:
    files = pfade if pfade is not None else (aenderungen(base) if base else None)
    if alles or files is None:
        total, module, grund = True, (), "Gesamtpruefung verlangt oder Aenderungsliste unbekannt."
    else:
        total, module, grund = betroffene(files)
    suite = laden(total, module)
    lauf = unittest.TextTestRunner(verbosity=2, stream=sys.stderr).run(suite)
    info = {
        "schema": 1,
        "umfang": "Python-/Medientests; Chromium-Nachweis separat",
        "stable": False,
        "zeit_utc": datetime.now(timezone.utc).isoformat(),
        "commit": os.environ.get("GITHUB_SHA") or git_head(),
        "aenderungen": files,
        "strategie": "vollstaendig" if total else "gezielt_mit_schutztests",
        "grund": grund,
        "ausgewaehlte_module": list(module),
        "tests_ausgefuehrt": lauf.testsRun,
        "fehler": [str(test) for test, _ in lauf.failures + lauf.errors],
        "uebersprungen": [str(test) for test, _ in lauf.skipped],
        "bestanden": lauf.wasSuccessful() and lauf.testsRun > 0,
    }
    return (0 if info["bestanden"] else 1), info


def git_head() -> str | None:
    try:
        p = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                           capture_output=True, text=True, timeout=5, check=False)
        return p.stdout.strip() if p.returncode == 0 else None
    except (OSError, subprocess.TimeoutExpired):
        return None


def main() -> int:
    parser = argparse.ArgumentParser(description="PROVOWARE: gezielte und volle Regression")
    gruppe = parser.add_mutually_exclusive_group()
    gruppe.add_argument("--all", action="store_true", help="Vollstaendiger Testlauf (Release/CI)")
    gruppe.add_argument("--base", help="Git-Vergleichsstand, z. B. origin/main")
    gruppe.add_argument("--paths", nargs="+", metavar="DATEI", help="Geaenderte Repository-Dateien")
    parser.add_argument("--bericht", type=Path, help="Lokale JSON-Protokolldatei")
    args = parser.parse_args()
    status, info = durchlauf(alles=args.all, pfade=args.paths, base=args.base)
    if args.bericht:
        from videozoom.core import json_sicher
        json_sicher(args.bericht, info)
    print(json.dumps(info, ensure_ascii=False, indent=2), flush=True)
    return status


if __name__ == "__main__":
    raise SystemExit(main())
