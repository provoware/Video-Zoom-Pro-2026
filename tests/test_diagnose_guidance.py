"""Einrichtung prüfen ohne Verzeichnisse anzulegen oder Originale zu schreiben."""
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from videozoom.diagnose import pruefen
from videozoom.webui import Bedienung


class Einrichtungsfuehrung(unittest.TestCase):
    def checks(self,cfg):
        with patch('videozoom.diagnose.shutil.which',return_value=None):
            return {p['name']:p for p in pruefen(real_scope=False,cfg=cfg)['pruefungen']}

    def test_fehlender_download_erklaert_naechsten_schritt(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);cfg={'downloads':str(root/'fehlt'),'arbeitsordner':str(root/'Arbeit')}
            checks=self.checks(cfg)
            self.assertFalse(checks['Downloads']['ok'])
            self.assertIn('Ordner wählen',checks['Downloads']['handlung'])
            self.assertTrue(checks['Arbeitsordner']['ok'])
            self.assertEqual(list(root.iterdir()),[])

    def test_arbeitsordner_im_eingang_und_symlink_blockieren(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);downloads=root/'Downloads';downloads.mkdir()
            checks=self.checks({'downloads':str(downloads),'arbeitsordner':str(downloads/'Arbeit')})
            self.assertFalse(checks['Arbeitsordner']['ok'])
            link=root/'Link';link.symlink_to(downloads,target_is_directory=True)
            self.assertFalse(self.checks({'downloads':str(link),'arbeitsordner':str(root/'Arbeit')})['Downloads']['ok'])

    def test_fehlende_schreibrechte_sichtbar(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);downloads=root/'Downloads';downloads.mkdir()
            with patch('videozoom.diagnose.os.access',return_value=False):
                checks=self.checks({'downloads':str(downloads),'arbeitsordner':str(root/'Arbeit')})
            self.assertFalse(checks['Downloads']['ok']);self.assertFalse(checks['Arbeitsordner']['ok'])

    def test_unbekannter_fortschritt_ist_keine_erfundene_null(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);bed=Bedienung({'arbeitsordner':str(root/'Arbeit')},root/'cfg.json')
            status=bed.status()
            for name in ('vorbereitung','stapel','video'):self.assertIsNone(status[name]['prozent'])
            bed._fortschritt({'phase':'video_start','prozent':0})
            self.assertEqual(bed.status()['video']['prozent'],0)
