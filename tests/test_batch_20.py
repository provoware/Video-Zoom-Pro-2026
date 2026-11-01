"""Langlauf vor der echten Kubuntu-Abnahme: 20 synthetische Songs, mehrere Neustarts."""
from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import tempfile
import time
import unittest

from tests.fixtures.generieren import wav, png
from videozoom.core import Workflow, pruefsumme


@unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"),
                     "Echter Medien-Test erfordert FFmpeg und FFprobe.")
class ZwanzigSongs(unittest.TestCase):
    def test_20_medien_ueber_fuenf_stapel_und_wiederanlauf(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            down = root / "Downloads"
            down.mkdir()
            work = root / "Arbeit"
            cfg = {
                "downloads": str(down),
                "arbeitsordner": str(work),
                "format": "KLAS",
                "stapelgroesse": 4,
            }
            original_hashes = {}
            for nummer in range(1, 21):
                label = f"Batch{nummer:02d}"
                audio = wav(down / f"{label}_suno-com-123_20261101.wav", sekunden=3)
                bildordner = work / "EINGANG" / label.lower() / "BILDER"
                bild1 = png(bildordner / "bild1.png", (200, 40, 75))
                bild2 = png(bildordner / "bild2.png", (50, 160, 220))
                for path in (audio, bild1, bild2):
                    old = time.time() - 45
                    os.utime(path, (old, old))
                    original_hashes[str(path)] = pruefsumme(path)

            first = Workflow(cfg, testmodus=True)
            self.assertEqual(first.vorbereiten(), (20, 0))
            self.assertEqual(len(first.zustand["auftraege"]), 20)
            seen = []
            for stapel in range(5):
                # Programm wird fuer jeden Teilstapel neu gestartet; keine
                # Daten der alten Python-Instanz duerfen benoetigt werden.
                lauf = Workflow(cfg, testmodus=True)
                done, remaining = lauf.stapel()
                self.assertEqual(done, 4, f"Stapel {stapel + 1}")
                self.assertEqual(remaining, 20 - (stapel + 1) * 4)
                current = sorted((work / "FERTIG").glob("*.mp4"))
                self.assertEqual(len(current), (stapel + 1) * 4)
                seen.extend(p.name for p in current if p.name not in seen)
            last = Workflow(cfg, testmodus=True)
            self.assertEqual(last.stapel(), (0, 0))
            self.assertEqual(last.vorbereiten(), (0, 0))
            self.assertEqual(last.stapel(), (0, 0))
            self.assertEqual(len(list((work / "FERTIG").glob("*.mp4"))), 20)
            self.assertEqual(len(set(seen)), 20)
            self.assertEqual(
                set(j["status"] for j in last.zustand["auftraege"].values()),
                {"ARCHIVIERT"},
            )
            for source in original_hashes:
                self.assertFalse(Path(source).exists(), source)

            logs = (work / "PROTOKOLLE" / "archiv.jsonl").read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(logs), 60)
            receipts = [json.loads(line) for line in logs]
            self.assertEqual(len({(r["auftrag"], r["quelle"]) for r in receipts}), 60)
            self.assertEqual({r["quelle"] for r in receipts}, set(original_hashes))
            for receipt in receipts:
                self.assertEqual(receipt["sha256"], original_hashes[receipt["quelle"]])
                self.assertEqual(pruefsumme(Path(receipt["ziel"])), receipt["sha256"])
                self.assertIn("_verwendet_", Path(receipt["ziel"]).name)
            # 20 unterschiedliche WAV + 2 gemeinsam verwendete, byte-identische
            # Bilder. Identische Quellen werden nicht 20-mal physisch dupliziert.
            self.assertEqual(
                len([p for p in (work / "VERWENDET").iterdir() if p.suffix in {".wav",".png"}]),
                22,
            )


if __name__ == "__main__":
    unittest.main()
