"""Statusvertrag: 100 Prozent nur nach nachweislicher Archivierung."""
from __future__ import annotations

from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from videozoom.core import Workflow
from videozoom.webui import Bedienung


class FortschrittOhneScheinerfolg(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "Downloads").mkdir()
        self.events = []
        self.svc = Workflow({
            "downloads": str(self.root / "Downloads"),
            "arbeitsordner": str(self.root / "Arbeit"),
            "format": "KLAS",
            "stapelgroesse": 2,
        }, fortschritt=self.events.append, testmodus=True)

    def job(self, key):
        job = {"titel": key, "status": "BEREIT", "versuche": 0,
               "dateien": [], "laenge": 5.0}
        self.svc.zustand["auftraege"][key] = job
        return job

    def test_temporarer_renderfehler_zeigt_niemals_hundert(self):
        job = self.job("problem")
        with patch.object(self.svc, "_render", side_effect=OSError("Dateisperre")):
            self.assertEqual(self.svc.stapel(), (0, 1))
        self.assertEqual(job["status"], "PAUSIERT")
        self.assertEqual(self.events[-1]["phase"], "stapel")
        self.assertLess(self.events[-1]["prozent"], 100)
        self.assertIn("video_pausiert", [e["phase"] for e in self.events])
        self.assertFalse(any(e["prozent"] == 100 for e in self.events))

    def test_erfolgreich_100_erst_nach_archiv(self):
        self.job("song")
        ziel = self.svc.ordner / "FERTIG" / "song_KLAS.mp4"

        def render(_):
            ziel.write_bytes(b"TEST_VIDEO" * 20)
            return ziel

        with patch.object(self.svc, "_render", side_effect=render):
            self.assertEqual(self.svc.stapel(), (1, 0))
        self.assertEqual(self.svc.zustand["auftraege"]["song"]["status"], "ARCHIVIERT")
        self.assertEqual(self.events[-1]["phase"], "stapel")
        self.assertEqual(self.events[-1]["prozent"], 100)
        self.assertIn("video_fertig", [e["phase"] for e in self.events])

    def test_archivfehler_video_ist_nicht_fertig(self):
        self.job("song")
        ziel = self.svc.ordner / "FERTIG" / "song_KLAS.mp4"

        def render(_):
            ziel.write_bytes(b"TEST_VIDEO" * 20)
            return ziel

        with patch.object(self.svc, "_render", side_effect=render), \
             patch.object(self.svc, "_archive", side_effect=OSError("Datentraeger voll")):
            self.assertEqual(self.svc.stapel(), (1, 0))
        self.assertEqual(self.svc.zustand["auftraege"]["song"]["status"], "ARCHIV_WARTET")
        self.assertLess(self.events[-1]["prozent"], 100)

    def test_begrenzter_stapel_nicht_voreilig_hundert(self):
        self.svc.cfg["stapelgroesse"] = 1
        self.job("song1")
        self.job("song2")
        outputs = iter(["song1.mp4", "song2.mp4"])

        def render(_):
            ziel = self.svc.ordner / "FERTIG" / next(outputs)
            ziel.write_bytes(b"VIDEO"*100)
            return ziel

        with patch.object(self.svc, "_render", side_effect=render):
            self.assertEqual(self.svc.stapel(), (1, 1))
        self.assertLess(self.events[-1]["prozent"], 100)
        self.assertEqual(self.svc.zustand["auftraege"]["song2"]["status"], "BEREIT")

    def test_bedienung_hat_drei_unabhaengige_prozentwerte(self):
        bedienung = Bedienung({}, self.root / "settings.json")
        bedienung._fortschritt({"phase": "vorbereiten", "prozent": 64})
        bedienung._fortschritt({"phase": "stapel", "prozent": 18})
        bedienung._fortschritt({"phase": "rendern", "prozent": 52})
        s = bedienung.status()
        self.assertEqual(s["vorbereitung"]["prozent"], 64)
        self.assertEqual(s["stapel"]["prozent"], 18)
        self.assertEqual(s["video"]["prozent"], 52)
        bedienung._fortschritt({"phase": "video_pausiert", "prozent": 52})
        self.assertEqual(bedienung.status()["video"]["phase"], "video_pausiert")


if __name__ == "__main__":
    unittest.main()
