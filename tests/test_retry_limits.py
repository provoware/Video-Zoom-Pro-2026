"""Grenzen für automatische Wiederholungen und sichere Archivkorrektur."""
from __future__ import annotations

from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import patch

from videozoom.core import Workflow, MAX_AUTO_VERSUCHE, MAX_ARCHIV_VERSUCHE


class Versuchsgrenzen(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        (root / "Downloads").mkdir()
        self.workflow = Workflow({"downloads": str(root / "Downloads"),
                                  "arbeitsordner": str(root / "Arbeit")}, testmodus=True)

    def test_defekter_renderer_maximal_drei_versuche(self):
        job = {"titel": "Song", "status": "BEREIT",
               "versuche": MAX_AUTO_VERSUCHE - 1, "dateien": [], "laenge": 5.0}
        self.workflow.zustand["auftraege"]["song"] = job
        with patch.object(self.workflow, "_render",
                          side_effect=OSError("temporärer Fehler")) as renderer:
            self.workflow.stapel()
            self.workflow.stapel()
        self.assertEqual(renderer.call_count, 1)
        self.assertEqual(job["status"], "PRUEFEN")
        self.assertIn("erschoepft", job["hinweis"])

    def test_archiv_wiederholung_nur_nach_wartefrist(self):
        job = {"titel":"Song", "status": "ARCHIV_WARTET",
               "archiv_versuche": 1, "archiv_retry_after": time.time() + 500}
        self.workflow.zustand["auftraege"]["song"] = job
        with patch.object(self.workflow, "_archive",
                          side_effect=OSError("Datenträger voll")) as archive:
            self.workflow.stapel()
            archive.assert_not_called()
            self.assertEqual(job["archiv_versuche"], 1)
            job["archiv_retry_after"] = 0
            self.workflow.stapel()
            archive.assert_called_once()
        self.assertEqual(job["status"], "ARCHIV_WARTET")
        self.assertEqual(job["archiv_versuche"], 2)
        self.assertGreater(job["archiv_retry_after"], time.time())

    def test_archiv_versuche_endlich_und_andere_jobs_unberuehrt(self):
        job = {"titel":"Song", "status": "ARCHIV_WARTET",
               "archiv_versuche":MAX_ARCHIV_VERSUCHE, "archiv_retry_after":0}
        other = {"titel":"Anderer", "status":"WARTET"}
        self.workflow.zustand["auftraege"].update({"song":job, "anders":other})
        with patch.object(self.workflow, "_archive") as archive:
            self.workflow.stapel()
            archive.assert_not_called()
        self.assertEqual(job["status"], "PRUEFEN")
        self.assertEqual(other["status"], "WARTET")

    def test_keine_scheinfreigabe_nach_versuchsgrenze(self):
        job = {"titel":"Song", "status":"BEREIT",
               "versuche":MAX_AUTO_VERSUCHE - 1,"dateien":[],"laenge":5.0}
        self.workflow.zustand["auftraege"]["song"] = job
        events=[]
        self.workflow.fortschritt=events.append
        with patch.object(self.workflow,"_render",side_effect=OSError("Fehler")):
            self.workflow.stapel()
        self.assertLess(events[-1]["prozent"],100)


if __name__=="__main__":
    unittest.main()
