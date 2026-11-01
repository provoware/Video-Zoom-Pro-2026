"""Fehlerinjektion fuer die transaktionale Archivkopie."""
from __future__ import annotations

from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from videozoom.core import kopieren_und_archivieren, pruefsumme


class ArchivRecovery(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.source = self.root / "song.wav"
        self.source.write_bytes(b"PROVOWARE-ORIGINAL" * 300)
        self.dest = self.root / "VERWENDET" / "song_verwendet_.wav"
        self.hash = pruefsumme(self.source)
        self.partial = self.dest.with_name(
            "." + self.dest.name + "." + self.hash[:12] + ".teil"
        )
        self.dest.parent.mkdir()

    def test_nach_abbruch_der_kopie_bleibt_original_und_folgelauf_funktioniert(self):
        def unterbrochen(src, dest, _buffer):
            dest.write(src.read(33))
            raise OSError("Datentraeger voruebergehend nicht erreichbar")

        with patch("videozoom.core.shutil.copyfileobj", side_effect=unterbrochen):
            with self.assertRaises(OSError):
                kopieren_und_archivieren(self.source, self.dest, self.hash)
        self.assertTrue(self.source.exists())
        self.assertFalse(self.dest.exists())
        self.assertTrue(self.partial.exists())
        kopieren_und_archivieren(self.source, self.dest, self.hash)
        self.assertFalse(self.source.exists())
        self.assertEqual(pruefsumme(self.dest), self.hash)
        self.assertTrue(self.partial.with_name(self.partial.name + ".abbruch-1").exists())

    def test_bestaetigte_teilkopie_ohne_erneutes_kopieren_fertigstellen(self):
        self.partial.write_bytes(self.source.read_bytes())
        with patch("videozoom.core.shutil.copyfileobj",
                   side_effect=AssertionError("Doppelte Kopie")):
            kopieren_und_archivieren(self.source, self.dest, self.hash)
        self.assertTrue(self.dest.is_file())
        self.assertFalse(self.partial.exists())

    def test_crash_nach_veroeffentlichung_raeuemt_teil_auf(self):
        self.partial.write_bytes(self.source.read_bytes())
        self.dest.write_bytes(self.source.read_bytes())
        kopieren_und_archivieren(self.source, self.dest, self.hash)
        self.assertFalse(self.source.exists())
        self.assertFalse(self.partial.exists())

    def test_symbollink_auf_teilkopie_wird_nicht_verwendet(self):
        original = self.root / "geheim"
        original.write_bytes(b"UNVERAENDERT")
        self.partial.symlink_to(original)
        with self.assertRaisesRegex(RuntimeError, "Unsichere"):
            kopieren_und_archivieren(self.source, self.dest, self.hash)
        self.assertEqual(original.read_bytes(), b"UNVERAENDERT")
        self.assertTrue(self.source.exists())

    def test_zielkonflikt_ueberschreibt_nicht(self):
        self.dest.write_bytes(b"FREMDE DATEN")
        with self.assertRaisesRegex(RuntimeError, "Zielkonflikt"):
            kopieren_und_archivieren(self.source, self.dest, self.hash)
        self.assertTrue(self.source.exists())
        self.assertEqual(self.dest.read_bytes(), b"FREMDE DATEN")

    def test_fsync_fehler_darf_kein_original_entfernen(self):
        with patch("videozoom.core.os.fsync", side_effect=OSError("fsync Fehler")):
            with self.assertRaises(OSError):
                kopieren_und_archivieren(self.source, self.dest, self.hash)
        self.assertTrue(self.source.exists())
        self.assertFalse(self.dest.exists())
        # Die vollstaendige Teilkopie kann bei erneutem Aufruf geprueft werden.
        kopieren_und_archivieren(self.source, self.dest, self.hash)
        self.assertEqual(pruefsumme(self.dest), self.hash)

    def test_idempotenter_erneuter_aufruf(self):
        kopieren_und_archivieren(self.source, self.dest, self.hash)
        kopieren_und_archivieren(self.source, self.dest, self.hash)
        self.assertEqual(pruefsumme(self.dest), self.hash)


if __name__ == "__main__":
    unittest.main()
