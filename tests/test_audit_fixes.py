"""Dauerhafte Gegenproben zu NI-20261103-01, ausschließlich isolierte Testdaten."""
import subprocess
import os
import time
import tempfile
from unittest.mock import patch
from tests.fixtures.generieren import wav, png
from pathlib import Path
import unittest

from videozoom.core import Workflow, lesen, video_gueltig, konfigurieren, FORMATE


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

    def test_a03_neuer_inhalt_gleicher_pfad_bewahrt_historie(self):
        audio, _ = self.medien()
        w = Workflow(self.cfg, testmodus=True)
        w.vorbereiten()
        key, old = next(iter(w.zustand["auftraege"].items()))
        old["status"] = "ARCHIVIERT"
        w.vorbereiten()
        self.assertEqual(len(w.zustand["auftraege"]), 1)
        wav(audio, sekunden=6)
        os.utime(audio, (time.time()-20,)*2)
        w.vorbereiten()
        self.assertEqual(len(w.zustand["auftraege"]), 2)
        self.assertIs(w.zustand["auftraege"][key], old)
        self.assertEqual(old["status"], "ARCHIVIERT")
        newkey = next(k for k in w.zustand["auftraege"] if k != key)
        self.assertEqual(w.zustand["auftraege"][newkey]["status"], "BEREIT")
        w.zustand["auftraege"][newkey]["status"] = "ARCHIVIERT"
        w.vorbereiten()
        self.assertEqual(len(w.zustand["auftraege"]), 2)

    def test_a03_unvollstaendige_revision_ersetzt_keine_historie(self):
        audio, _ = self.medien()
        w = Workflow(self.cfg, testmodus=True)
        w.vorbereiten()
        old = next(iter(w.zustand["auftraege"].values()))
        old["status"] = "ARCHIVIERT"
        audio.write_bytes(audio.read_bytes()[:-100])
        os.utime(audio, (time.time()-20,)*2)
        w.vorbereiten()
        self.assertEqual(len(w.zustand["auftraege"]), 1)
        self.assertEqual(old["status"], "ARCHIVIERT")

    def mp4(self, name, size="800x600", fps=25, ton=2):
        target = self.root / (name + ".mp4")
        subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i",
                        "color=c=blue:s="+size+":r="+str(fps)+":d=2",
                        "-f", "lavfi", "-i", "sine=frequency=220:duration="+str(ton),
                        "-c:v", "libx264", "-threads", "1", "-c:a", "aac",
                        "-pix_fmt", "yuv420p", str(target)], check=True, timeout=30)
        return target

    def test_a04_echte_mp4_falsches_format_bildrate_oder_ton(self):
        cfg = konfigurieren(self.cfg)
        self.assertTrue(video_gueltig(self.mp4("gut"), 2, cfg, testmodus=True))
        for name, kwargs in (("klein", {"size": "128x96"}),
                             ("fps", {"fps": 15}), ("ton", {"ton": 1})):
            with self.subTest(name=name):
                self.assertFalse(video_gueltig(self.mp4(name, **kwargs), 2, cfg, testmodus=True))

    def test_a04_vollstaendiger_lesefehler_wird_nicht_freigegeben(self):
        target = self.mp4("dekodierung")
        cfg = konfigurieren(self.cfg)
        with patch("videozoom.core.rendern", side_effect=RuntimeError("defektes Paket")):
            with self.assertRaisesRegex(RuntimeError, "defektes Paket"):
                video_gueltig(target, 2, cfg, testmodus=True)
        target.write_bytes(target.read_bytes()[:100])
        self.assertFalse(video_gueltig(target, 2, cfg, testmodus=True))

    def test_a04_alle_fuenf_erwarteten_abmessungen(self):
        for name, (width, height) in FORMATE.items():
            with self.subTest(format=name):
                cfg = konfigurieren({**self.cfg, "format": name})
                target = self.mp4(name, size=f"{width}x{height}")
                self.assertTrue(video_gueltig(target, 2, cfg, testmodus=True))
