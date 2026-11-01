"""Schutz gegen Quittungsduplikate und unsichere Archiv-Quellpfade."""
from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from videozoom.core import Workflow, pruefsumme


class ArchiveEvidence(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        root = Path(self.folder.name)
        self.downloads = root / "Downloads"
        self.downloads.mkdir()
        self.worker = Workflow({"downloads": str(self.downloads),
                                "arbeitsordner": str(root / "Arbeit")}, testmodus=True)
        self.source = self.downloads / "original.wav"
        self.source.write_bytes(b"Testwellenform" * 40)
        self.video = self.worker.ordner / "FERTIG" / "fertig.mp4"
        self.video.write_bytes(b"MP4_SYNTHETISCH" * 70)
        self.receipt = self.worker.ordner / "PROTOKOLLE" / "archiv.jsonl"

    def job(self, sources=None):
        sources = [self.source] if sources is None else sources
        return {"titel": "Song", "status": "FERTIG",
                "dateien": [{"pfad": str(p), "sha256": pruefsumme(p)}
                            for p in sources],
                "video": str(self.video), "video_hash": pruefsumme(self.video)}

    def test_wiederholung_nach_quittung_ohne_doppeltes_log(self):
        job = self.job()
        self.worker._archive("k1", job)
        self.assertEqual(job["status"], "ARCHIVIERT")
        self.assertFalse(self.source.exists())
        self.assertEqual(len(self.receipt.read_text().splitlines()), 1)
        job["status"] = "ARCHIV_WARTET"  # Crash vor finalem Journalabschluss
        self.worker._archive("k1", job)
        lines = self.receipt.read_text().splitlines()
        self.assertEqual(len(lines), 1)
        log = json.loads(lines[0])
        self.assertEqual(log["auftrag"], "k1")
        self.assertEqual(log["sha256"], job["dateien"][0]["sha256"])

    def test_externe_quelle_wird_nicht_bewegt(self):
        other = Path(self.folder.name) / "FremdeDatei.wav"
        other.write_bytes(b"privates-dokument" * 100)
        job = self.job([other])
        with self.assertRaisesRegex(RuntimeError, "Quellpfad"):
            self.worker._archive("fremd", job)
        self.assertTrue(other.exists())
        self.assertFalse(self.receipt.exists())

    def test_alle_quellen_vor_erster_bewegung_pruefen(self):
        other = Path(self.folder.name) / "fremd.wav"
        other.write_bytes(b"Nicht anfassen" * 100)
        job = self.job([self.source, other])
        with self.assertRaisesRegex(RuntimeError, "Quellpfad"):
            self.worker._archive("mixed", job)
        self.assertTrue(self.source.exists())
        self.assertTrue(other.exists())

    def test_beschaedigtes_protokoll_stoppt_ohne_originaerverlust(self):
        self.receipt.write_text('{"unvollstaendig":', encoding="utf-8")
        job = self.job()
        with self.assertRaisesRegex(RuntimeError, "Archivprotokoll"):
            self.worker._archive("k1", job)
        self.assertTrue(self.source.exists())
        self.assertEqual(self.receipt.read_text(), '{"unvollstaendig":')

    def test_protokoll_symlink_wird_verweigert(self):
        outside = Path(self.folder.name) / "extern.jsonl"
        outside.write_text("unberuehrt", encoding="utf-8")
        self.receipt.symlink_to(outside)
        with self.assertRaisesRegex(RuntimeError, "Archivprotokoll"):
            self.worker._archive("k1", self.job())
        self.assertTrue(self.source.exists())
        self.assertEqual(outside.read_text(), "unberuehrt")


if __name__ == "__main__":
    unittest.main()
