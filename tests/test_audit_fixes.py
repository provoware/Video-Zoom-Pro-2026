"""Dauerhafte Gegenproben zu NI-20261103-01, ausschließlich isolierte Testdaten."""
import os
import time
import tempfile
from unittest.mock import patch
from tests.fixtures.generieren import wav, png
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

    def medien(self):
        audio = wav(self.root / "Downloads" / "Song.wav")
        image = png(self.root / "Work/EINGANG/song/BILDER/1.png", breite=128, hoehe=96)
        for p in (audio, image):
            os.utime(p, (time.time()-20,)*2)
        return audio, image

    def test_a02_pruefsperre_ueberlebt_automatikrunden(self):
        self.medien()
        w = Workflow(self.cfg, testmodus=True)
        w.vorbereiten()
        job = next(iter(w.zustand["auftraege"].values()))
        with patch.object(w, "_render", side_effect=OSError("defekt")) as render:
            for _ in range(8):
                for current in w.zustand["auftraege"].values():
                    current["retry_after"] = 0
                w.vorbereiten()
                w.stapel()
        self.assertEqual(render.call_count, 3)
        job = next(iter(w.zustand["auftraege"].values()))
        self.assertEqual(job["versuche"], 3)
        self.assertEqual(job["status"], "PRUEFEN")

    def test_a02_bereit_mit_erschoepften_versuchen_startet_nicht(self):
        w = Workflow(self.cfg, testmodus=True)
        job = {"status": "BEREIT", "titel": "Alt", "versuche": 3}
        w.zustand["auftraege"]["alt"] = job
        with patch.object(w, "_render") as render:
            w.stapel()
            render.assert_not_called()
        self.assertEqual(job["status"], "PRUEFEN")
