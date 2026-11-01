"""Echte Prozessabbrueche und mehrteilige Stapel mit synthetischen Medien.

Nur temporaere Testordner; VideoBatch und echte Downloads bleiben unberuehrt.
FFmpeg wird real ausgefuehrt, jedoch im ausdruecklichen Testmodus ohne systemd.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import unittest

from tests.fixtures.generieren import png, wav
from videozoom.core import Workflow

REPO = Path(__file__).resolve().parents[1]
MEDIA_OK = bool(shutil.which("ffmpeg") and shutil.which("ffprobe"))


@unittest.skipUnless(MEDIA_OK, "FFmpeg/FFprobe fehlen; Medien-Haertetests nicht ausgefuehrt.")
class RealeAbbruchpruefungen(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        self.downloads = root / "Downloads"
        self.downloads.mkdir()
        self.work = root / "Arbeit"
        self.cfg = {
            "downloads": str(self.downloads),
            "arbeitsordner": str(self.work),
            "format": "KLAS",
            "stapelgroesse": 2,
        }

    def song(self, nummer: int, dauer: int = 5):
        name = f"Song-{nummer}"
        audio = wav(self.downloads / f"{name}_suno-com-123_20261101.wav", sekunden=dauer)
        bilder = self.work / "EINGANG" / name.lower() / "BILDER"
        first = png(bilder / "bild01.png")
        second = png(bilder / "bild02.png", (21, 117, 190))
        for pfad in (audio, first, second):
            old = time.time() - 30
            os.utime(pfad, (old, old))
        return audio, first, second

    def laufender_code(self, text: str):
        result = subprocess.run(
            [sys.executable, "-c", text, json.dumps(self.cfg)],
            cwd=REPO, capture_output=True, text=True, timeout=100, check=False,
        )
        return result

    def test_drei_songs_zwei_stapel_ohne_doppelverarbeitung(self):
        for number in range(3):
            self.song(number)
        workflow = Workflow(self.cfg, testmodus=True)
        self.assertEqual(workflow.vorbereiten(), (3, 0))
        self.assertEqual(workflow.stapel(), (2, 1))
        self.assertEqual(workflow.stapel(), (1, 0))
        self.assertEqual(workflow.stapel(), (0, 0))
        self.assertEqual(len(list((self.work / "FERTIG").glob("*.mp4"))), 3)
        self.assertEqual(len(list((self.work / "VERWENDET").iterdir())), 9)
        self.assertEqual(
            [x["status"] for x in workflow.zustand["auftraege"].values()],
            ["ARCHIVIERT"] * 3,
        )

    def test_abbruch_nach_fertig_videodatei_ohne_doppelrender(self):
        sources = self.song(4)
        Workflow(self.cfg, testmodus=True).vorbereiten()
        child = """
import json, os, sys
from videozoom.core import Workflow
class Abbruch(Workflow):
    def _render(self, job):
        result = super()._render(job)
        os._exit(73)  # absichtlich ohne finally, mitten im Journal-Uebergang
w = Abbruch(json.loads(sys.argv[1]), testmodus=True)
w.sperren()
w.stapel()
"""
        result = self.laufender_code(child)
        self.assertEqual(result.returncode, 73, result.stderr[-1000:])
        original = list((self.work / "FERTIG").glob("*.mp4"))
        self.assertEqual(len(original), 1)
        zustand = json.loads((self.work / "PROTOKOLLE" / "auftraege.json").read_text())
        job = next(iter(zustand["auftraege"].values()))
        self.assertEqual(job["status"], "LAEUFT")
        self.assertIn("render_hash", job)
        after = Workflow(self.cfg, testmodus=True)
        self.assertEqual(after.stapel(), (0, 0))
        self.assertEqual(len(list((self.work / "FERTIG").glob("*.mp4"))), 1)
        self.assertEqual(next(iter(after.zustand["auftraege"].values()))["status"], "ARCHIVIERT")
        self.assertFalse(any(path.exists() for path in sources))

    def test_abbruch_waehrend_archivkopie_wird_fortgesetzt(self):
        sources = self.song(5)
        Workflow(self.cfg, testmodus=True).vorbereiten()
        child = """
import json, os, sys, shutil
from videozoom.core import Workflow
def unterbrechen(src, dest, _buffer):
    dest.write(src.read(47))
    dest.flush()
    os.fsync(dest.fileno())
    os._exit(74)  # absichtlich nach nachweisbar unvollstaendiger Teilkopie
shutil.copyfileobj = unterbrechen
w = Workflow(json.loads(sys.argv[1]), testmodus=True)
w.sperren()
w.stapel()
"""
        result = self.laufender_code(child)
        self.assertEqual(result.returncode, 74, result.stderr[-1000:])
        self.assertTrue(all(path.exists() for path in sources))
        self.assertEqual(len(list((self.work / "FERTIG").glob("*.mp4"))), 1)
        after = Workflow(self.cfg, testmodus=True)
        self.assertEqual(after.stapel(), (0, 0))
        self.assertEqual(len(list((self.work / "VERWENDET").iterdir())), 3)
        self.assertEqual(next(iter(after.zustand["auftraege"].values()))["status"], "ARCHIVIERT")
        self.assertFalse(any(path.exists() for path in sources))

    def test_beschaedigte_wav_blockiert_nicht_gesunden_song(self):
        self.song(6)
        bad = self.downloads / "Song-7_suno-com-123_20261101.wav"
        bad.write_bytes(b"KEINE-WAV-DATEI" * 100)
        bad_image = png(self.work / "EINGANG" / "song-7" / "BILDER" / "bild01.png")
        old = time.time() - 30
        for item in (bad, bad_image):
            os.utime(item, (old, old))
        workflow = Workflow(self.cfg, testmodus=True)
        self.assertEqual(workflow.vorbereiten(), (1, 1))
        self.assertEqual(workflow.stapel(), (1, 0))
        status = sorted(x["status"] for x in workflow.zustand["auftraege"].values())
        self.assertEqual(status, ["ARCHIVIERT", "PRUEFEN"])
        self.assertTrue(bad.exists())

    def test_sigkill_nach_vorbereitung_erhaelt_auftrag(self):
        self.song(8)
        child = """
import json, sys, time
from videozoom.core import Workflow
w = Workflow(json.loads(sys.argv[1]), testmodus=True)
w.sperren()
w.vorbereiten()
print("BEREIT", flush=True)
time.sleep(90)
"""
        proc = subprocess.Popen(
            [sys.executable, "-u", "-c", child, json.dumps(self.cfg)],
            cwd=REPO, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        )
        try:
            self.assertEqual(proc.stdout.readline().strip(), "BEREIT")
            proc.kill()  # SIGKILL: aehnlich Strom-/Prozessausfall ohne Aufraeumen
            proc.wait(timeout=10)
            self.assertEqual(proc.returncode, -signal.SIGKILL)
        finally:
            if proc.poll() is None:
                proc.kill()
                proc.wait(timeout=5)
            proc.stdout.close()
            proc.stderr.close()
        after = Workflow(self.cfg, testmodus=True)
        self.assertEqual(after.stapel(), (1, 0))
        self.assertEqual(next(iter(after.zustand["auftraege"].values()))["status"], "ARCHIVIERT")


if __name__ == "__main__":
    unittest.main()
