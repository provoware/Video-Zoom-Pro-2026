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

    def test_http_videobereich_token_und_einzelfreigabe(self):
        import json
        import threading
        from urllib.request import Request, urlopen
        from urllib.error import HTTPError
        from videozoom.webui import Bedienung, starten
        target = erzeugen(self.w, self.key)
        self.job.update(status="PRUEFEN", versuche=3)
        self.w.speichern()
        ui = Bedienung(self.w.cfg, self.root/"settings.json")
        refs = {}; ready = threading.Event()
        def callback(server, url):
            refs.update(server=server, url=url); ready.set()
        with patch("videozoom.webui.Bedienung", return_value=ui):
            thread = threading.Thread(target=starten, args=(self.w.cfg, self.root/"settings.json"),
                                      kwargs={"browser": False, "bereit": callback}, daemon=True)
            thread.start()
            self.assertTrue(ready.wait(5))
        root, token = refs["url"].split('/?')
        url = root+'/vorschau?'+token+'&auftrag='+self.key
        try:
            with urlopen(Request(url, headers={"Range":"bytes=0-31"}), timeout=5) as response:
                self.assertEqual(response.status, 206)
                self.assertEqual(response.read(), target.read_bytes()[:32])
                self.assertTrue(response.headers["Content-Range"].startswith("bytes 0-31/"))
            for link, headers, expected in ((root+'/vorschau?auftrag='+self.key, {},403),
                                             (url, {"Range":"bytes=9999999999-"},416),
                                             (url, {"Host":"fremd.example"},403)):
                with self.assertRaises(HTTPError) as exc:
                    urlopen(Request(link, headers=headers), timeout=5)
                self.assertEqual(exc.exception.code, expected)
            req = Request(root+'/auftrag?'+token, method='POST',
                          headers={"Content-Type":"application/json"},
                          data=json.dumps({"auftrag":self.key,"aktion":"freigeben"}).encode())
            with urlopen(req, timeout=5) as response:
                self.assertEqual(response.status, 200)
            ui.thread.join(5)
            self.assertFalse(ui.thread.is_alive())
            self.assertEqual(ui.status()["liste"][0]["status"], "BEREIT")
            self.assertEqual(ui.status()["liste"][0]["versuche"], 0)
            self.assertIn("erfolgreich", ui.einzelmeldung["text"])
            self.w.sperren()
            try:
                with self.assertRaisesRegex(RuntimeError, "Verarbeitung"):
                    ui.auftrag(self.key, "vorschau")
            finally:
                self.w.freigeben()
        finally:
            refs["server"].shutdown(); thread.join(5)
        self.assertTrue(all(p.exists() for p in self.paths))

    def test_archiv_einzelfreigabe_berechnet_video_nicht_erneut(self):
        self.w.stapel()
        self.assertEqual(self.job["status"], "ARCHIVIERT")
        self.job.update(status="PRUEFEN", archiv_versuche=3)
        freigeben(self.w, self.key)
        self.assertEqual(self.job["status"], "ARCHIV_WARTET")
        with patch.object(self.w, "_render", side_effect=AssertionError("Doppelrender")):
            self.w.stapel()
        self.assertEqual(self.job["status"], "ARCHIVIERT")
        self.assertEqual(len(list((self.w.ordner/"FERTIG").glob('*.mp4'))), 1)

    def test_manipulierte_veroeffentlichte_vorschau_nicht_ausliefern(self):
        target = erzeugen(self.w, self.key)
        target.write_bytes(b'ersetzte Vorschau')
        with self.assertRaisesRegex(RuntimeError, "verändert"):
            datei(self.w.ordner, self.job)
