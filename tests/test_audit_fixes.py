"""Dauerhafte Gegenproben zu NI-20261103-01, ausschließlich isolierte Testdaten."""
import tempfile
from pathlib import Path
import unittest

from videozoom.core import Workflow, lesen


class AuditFixes(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / "Downloads").mkdir()
        self.cfg = {"downloads": str(self.root / "Downloads"),
                    "arbeitsordner": str(self.root / "Work"), "format": "KLAS"}

    def test_a01_altes_objekt_erhaelt_neuere_auftraege_nach_sperre(self):
        a, b = Workflow(self.cfg), Workflow(self.cfg)
        a.sperren()
        try:
            a.zustand["auftraege"]["neu"] = {"status": "WARTET"}
            a.speichern()
        finally:
            a.freigeben()
        b.sperren()
        try:
            b.speichern()
        finally:
            b.freigeben()
        self.assertIn("neu", lesen(b.journal, {})["auftraege"])

    def test_a01_defektes_nachgeladenes_journal_bleibt_erhalten(self):
        a = Workflow(self.cfg)
        a.journal.write_text("{kaputt")
        with self.assertRaisesRegex(RuntimeError, "beschädigt"):
            a.sperren()
        self.assertIsNone(a.lock_file)
        self.assertEqual(a.journal.read_text(), "{kaputt")
        with self.assertRaises(RuntimeError):
            a.sperren()  # Die erste Fehlerprüfung hat die Sperre freigegeben.
