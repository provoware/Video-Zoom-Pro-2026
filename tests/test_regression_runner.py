"""Testet die Testauswahl selbst: keine falschen Sicherheitsfreigaben."""
from __future__ import annotations

from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import regression


class RegressionAuswahl(unittest.TestCase):
    def test_core_loest_medien_und_recovery_aus(self):
        alles, module, grund = regression.betroffene(["videozoom/core.py"])
        self.assertFalse(alles)
        self.assertIn("tests.test_workflow", module)
        self.assertIn("tests.test_recovery", module)

    def test_webui_loest_browser_und_workflow_aus(self):
        alles, module, _ = regression.betroffene(["videozoom/webui.py"])
        self.assertFalse(alles)
        self.assertIn("tests.test_webui", module)
        self.assertIn("tests.test_workflow", module)

    def test_unbekannte_datei_erfordert_gesamtpruefung(self):
        alles, _, grund = regression.betroffene(["videozoom/unbekannt.py"])
        self.assertTrue(alles)
        self.assertIn("Unbekannter", grund)

    def test_pruefinfrastruktur_erfordert_gesamtpruefung(self):
        self.assertTrue(regression.betroffene(["scripts/regression.py"])[0])
        self.assertTrue(regression.betroffene([".github/workflows/ci.yml"])[0])

    def test_dokumentation_bewahrt_schutztests(self):
        alles, module, _ = regression.betroffene(["docs/TODO.md"])
        self.assertFalse(alles)
        suite = regression.laden(alles, module)
        self.assertEqual(suite.countTestCases(), len(regression.SAFETY_CASES))

    def test_git_fehler_ist_keine_leere_aenderungsliste(self):
        with patch("regression.subprocess.run", side_effect=OSError("git fehlt")):
            self.assertIsNone(regression.aenderungen("origin/main"))

    def test_keine_aenderungsliste_erfordert_gesamtpruefung(self):
        self.assertTrue(regression.betroffene([])[0])

    def test_pfadmischung_behandelt_testdateien_richtig(self):
        alles, module, _ = regression.betroffene(["tests/test_workflow.py"])
        self.assertFalse(alles)
        self.assertIn("tests.test_workflow", module)


if __name__ == "__main__":
    unittest.main()
