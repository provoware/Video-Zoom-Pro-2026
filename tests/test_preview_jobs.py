"""Vorschau- und Einzelauftragsverträge mit echten synthetischen Medien."""
import os
import tempfile
import time
from pathlib import Path
import unittest
from unittest.mock import patch
from tests.fixtures.generieren import wav, png
from videozoom.core import Workflow, pruefsumme
from videozoom.auftraege import freigeben, uebersicht
from videozoom.vorschau import erzeugen, datei
from videozoom.render_watchdog import ProduktionGestoppt


class PreviewJobs(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        downloads = self.root / "Downloads"; downloads.mkdir()
        self.w = Workflow({"downloads": str(downloads), "arbeitsordner": str(self.root/"Work"),
                           "format": "KLAS"}, testmodus=True)
        audio = wav(downloads/"Song.wav", sekunden=4)
        image = png(self.w.ordner/"EINGANG/song/BILDER/1.png", breite=128, hoehe=96)
        self.paths = [audio, image]
        for p in self.paths:
            os.utime(p, (time.time()-20,)*2)
        self.w.vorbereiten()
        self.key, self.job = next(iter(self.w.zustand["auftraege"].items()))

    def test_echte_vorschau_archiviert_keine_quellen(self):
        hashes = [pruefsumme(p) for p in self.paths]
        target = erzeugen(self.w, self.key)
        self.assertTrue(target.is_file())
        self.assertEqual(datei(self.w.ordner, self.job), target)
        self.assertEqual([pruefsumme(p) for p in self.paths], hashes)
        self.assertEqual(self.job["status"], "BEREIT")
        self.assertEqual(self.job["versuche"], 0)
        self.assertFalse(list((self.w.ordner/"FERTIG").iterdir()))
        self.assertFalse(list((self.w.ordner/"VERWENDET").iterdir()))

    def test_stop_und_fehlende_quote_starten_keine_vorschau(self):
        self.w.testmodus = False
        with patch("videozoom.diagnose.scope_verfuegbar", return_value=False), \
             patch("videozoom.vorschau.rendern") as render:
            with self.assertRaisesRegex(RuntimeError, "Begrenzung"):
                erzeugen(self.w, self.key)
            render.assert_not_called()
        self.w.testmodus = True
        self.w.stop.set()
        with self.assertRaises(ProduktionGestoppt):
            erzeugen(self.w, self.key)
        self.assertNotIn("vorschau", self.job)
        self.assertTrue(all(p.exists() for p in self.paths))
        self.assertEqual(self.job["versuche"], 0)

    def test_geaenderte_quelle_und_fremde_vorschau_gesperrt(self):
        self.paths[1].write_bytes(b"geaendert")
        with self.assertRaisesRegex(RuntimeError, "Quelle"):
            erzeugen(self.w, self.key)
        self.job["vorschau"] = {"pfad": str(self.paths[0]), "sha256": pruefsumme(self.paths[0])}
        with self.assertRaisesRegex(RuntimeError, "Vorschau"):
            datei(self.w.ordner, self.job)

    def test_einzelfreigabe_bewusst_und_nur_unveraenderte_quellen(self):
        self.job.update(status="PRUEFEN", versuche=3)
        freigeben(self.w, self.key)
        self.assertEqual((self.job["status"], self.job["versuche"]), ("BEREIT", 0))
        with self.assertRaises(ValueError):
            freigeben(self.w, self.key)
        self.job["status"] = "PRUEFEN"
        self.paths[1].write_bytes(b"anderes Bild")
        with self.assertRaises(RuntimeError):
            freigeben(self.w, self.key)
        self.assertEqual(self.job["status"], "PRUEFEN")

    def test_uebersicht_zeigt_echten_status_ohne_quellpfade(self):
        rows = uebersicht(self.w.zustand["auftraege"], self.w.cfg)
        self.assertEqual(rows[0]["id"], self.key)
        self.assertEqual(rows[0]["bilder"], 1)
        self.assertNotIn("dateien", rows[0])
        self.assertEqual(self.w.status()["liste"], rows)
