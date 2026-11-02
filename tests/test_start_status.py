"""Startanzeige liest Journal ausschließlich, ohne schreibenden Workflow."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from videozoom.webui import Bedienung


class StartStatus(unittest.TestCase):
    def test_gespeicherte_auftraege_sofort_ohne_dateiaenderung(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);journal=root/'Arbeit'/'PROTOKOLLE'/'auftraege.json'
            journal.parent.mkdir(parents=True)
            journal.write_text(json.dumps({'schema':1,'auftraege':{'a':{'status':'BEREIT'},'b':{'status':'PAUSIERT'}}}))
            before=journal.read_bytes(),journal.stat().st_mtime_ns
            bed=Bedienung({'arbeitsordner':str(root/'Arbeit')},root/'cfg.json')
            with patch('videozoom.webui.Workflow',side_effect=AssertionError('Darf nicht schreiben')):
                self.assertEqual(bed.status()['jobs'],{'BEREIT':1,'PAUSIERT':1})
            self.assertEqual((journal.read_bytes(),journal.stat().st_mtime_ns),before)
            self.assertEqual([p.name for p in journal.parent.iterdir()],['auftraege.json'])

    def test_erststart_legt_keine_ordner_an(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);bed=Bedienung({'arbeitsordner':str(root/'fehlt')},root/'cfg.json')
            self.assertEqual(bed.status()['jobs'],{})
            self.assertFalse((root/'fehlt').exists())

    def test_beschaedigtes_journal_bleibt_erhalten_und_sichtbar(self):
        for content in ('{kaputt','{"schema":9,"auftraege":{}}','{"schema":1,"auftraege":{"x":null}}'):
            with self.subTest(content=content), tempfile.TemporaryDirectory() as tmp:
                root=Path(tmp);journal=root/'PROTOKOLLE'/'auftraege.json';journal.parent.mkdir()
                journal.write_text(content)
                bed=Bedienung({'arbeitsordner':str(root)},root/'cfg.json')
                self.assertTrue(bed.status()['fehler'])
                self.assertEqual(journal.read_text(),content)

    def test_symlink_auch_in_uebergeordnetem_ordner_abgewiesen(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);outside=root/'fremd';outside.mkdir()
            link=root/'Arbeit';link.symlink_to(outside,target_is_directory=True)
            bed=Bedienung({'arbeitsordner':str(link)},root/'cfg.json')
            self.assertIn('symbolische',bed.status()['fehler'])
            self.assertEqual(list(outside.iterdir()),[])
