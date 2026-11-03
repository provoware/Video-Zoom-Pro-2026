"""Regressionen fuer Absturzgrenzen: kein Doppelrender, kein ungesichertes Loeschen."""
from __future__ import annotations

import hashlib
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from videozoom.core import Workflow, pruefsumme, teil_sichern


def probe(_path):
    return {
        "streams": [{"codec_type": "video"}, {"codec_type": "audio"}],
        "format": {"duration": "5.0"},
    }


class Wiederanlauf(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        downloads = self.root / "Downloads"
        downloads.mkdir()
        self.workflow = Workflow({
            "downloads": str(downloads),
            "arbeitsordner": str(self.root / "Arbeit"),
            "format": "KLAS",
        }, testmodus=True)
        self.final = self.workflow.ordner / "FERTIG" / "song_KLAS.mp4"
        self.part = self.final.with_name(self.final.stem + ".teil.mp4")

    def laufender_auftrag(self, hashwert=None):
        job = {
            "status": "LAEUFT",
            "titel": "Song",
            "dateien": [],
            "laenge": 5.0,
            "versuche": 1,
            "video_ziel": str(self.final),
        }
        if hashwert:
            job["render_hash"] = hashwert
        self.workflow.zustand["auftraege"]["song"] = job
        self.workflow.speichern()
        return job

    @patch("videozoom.core.video_gueltig", return_value=True)  # Zustandsprobe; echte Medien separat
    def test_absturz_nach_veroeffentlichung_verhindert_doppelrender(self, _):
        self.final.write_bytes(b"geprueftes-video")
        job = self.laufender_auftrag(pruefsumme(self.final))
        with patch.object(self.workflow, "_render", side_effect=AssertionError("Doppelrender")) as render:
            self.assertEqual(self.workflow.stapel(), (0, 0))
            render.assert_not_called()
        self.assertEqual(job["status"], "ARCHIVIERT")
        self.assertEqual(list(self.final.parent.glob("*.mp4")), [self.final])

    @patch("videozoom.core.video_gueltig", return_value=True)  # Zustandsprobe; echte Medien separat
    def test_absturz_vor_veroeffentlichung_nutzt_validierten_teil(self, _):
        self.part.write_bytes(b"vollstaendiges-video")
        job = self.laufender_auftrag(pruefsumme(self.part))
        with patch.object(self.workflow, "_render", side_effect=AssertionError("Doppelrender")):
            self.workflow.stapel()
        self.assertEqual(job["status"], "ARCHIVIERT")
        self.assertEqual(self.final.read_bytes(), b"vollstaendiges-video")
        self.assertFalse(self.part.exists())

    def test_absturz_waehrend_rendern_sichert_teil_und_setzt_bereit(self):
        self.part.write_bytes(b"noch-nicht-fertig")
        job = self.laufender_auftrag()
        self.workflow._recover_inflight()
        self.assertEqual(job["status"], "BEREIT")
        self.assertFalse(self.part.exists())
        self.assertEqual(
            self.part.with_name(self.part.name + ".abbruch-1").read_bytes(),
            b"noch-nicht-fertig",
        )

    @patch("videozoom.core.video_gueltig", return_value=True)  # Zustandsprobe; echte Medien separat
    def test_pausiertes_video_trotz_nicht_abgelaufener_wartezeit_wiederfinden(self, _):
        self.final.write_bytes(b"bereits-publiziert")
        job = self.laufender_auftrag(pruefsumme(self.final))
        job["status"] = "PAUSIERT"
        job["retry_after"] = 9999999999
        with patch.object(self.workflow, "_render", side_effect=AssertionError("Doppelrender")):
            self.workflow.stapel()
        self.assertEqual(job["status"], "ARCHIVIERT")

    def test_bestaetigte_teil_datei_mit_falschem_hash_bleibt_gesperrt(self):
        self.part.write_bytes(b"manipuliert")
        job = self.laufender_auftrag(hashlib.sha256(b"urspruenglich").hexdigest())
        self.workflow._recover_inflight()
        self.assertEqual(job["status"], "PRUEFEN")
        self.assertTrue(self.part.exists())

    def test_altes_journal_ohne_ziel_bleibt_zur_pruefung(self):
        self.workflow.zustand["auftraege"]["alt"] = {
            "status": "LAEUFT", "titel": "Alt", "versuche": 1,
        }
        self.workflow._recover_inflight()
        self.assertEqual(self.workflow.zustand["auftraege"]["alt"]["status"], "PRUEFEN")

    @patch("videozoom.core.video_gueltig", return_value=True)  # Zustandsprobe; echte Medien separat
    def test_falscher_hash_keine_fremde_mp4_uebernehmen(self, _):
        self.final.write_bytes(b"fremde-datei")
        job = self.laufender_auftrag(hashlib.sha256(b"richtig").hexdigest())
        self.workflow._recover_inflight()
        self.assertEqual(job["status"], "PRUEFEN")
        self.assertEqual(self.final.read_bytes(), b"fremde-datei")

    def test_temporarname_nie_ueberschreiben(self):
        self.part.write_bytes(b"erste")
        erste = teil_sichern(self.part)
        self.part.write_bytes(b"zweite")
        zweite = teil_sichern(self.part)
        self.assertNotEqual(erste, zweite)
        self.assertEqual(erste.read_bytes(), b"erste")
        self.assertEqual(zweite.read_bytes(), b"zweite")

    def test_symlink_als_teil_wird_nicht_veraendert(self):
        fremd = self.root / "fremde-daten"
        fremd.write_bytes(b"unantastbar")
        self.part.symlink_to(fremd)
        with self.assertRaisesRegex(RuntimeError, "Unsichere"):
            teil_sichern(self.part)
        self.assertEqual(fremd.read_bytes(), b"unantastbar")

    def test_laufenden_auftrag_nicht_durch_vorbereitung_ueberschreiben(self):
        import os
        import time
        wav = self.root / "Downloads" / "Song.wav"
        wav.write_bytes(b"RIFF" + b"0" * 1024)
        alt = time.time() - 30
        os.utime(wav, (alt, alt))
        key = hashlib.sha256(str(wav).encode()).hexdigest()[:24]
        self.workflow.zustand["auftraege"][key] = {
            "status": "LAEUFT",
            "titel": "Song",
            "video_ziel": str(self.final),
        }
        self.workflow.vorbereiten()
        self.assertEqual(self.workflow.zustand["auftraege"][key]["status"], "LAEUFT")
        self.assertEqual(self.workflow.zustand["auftraege"][key]["video_ziel"], str(self.final))


if __name__ == "__main__":
    unittest.main()
