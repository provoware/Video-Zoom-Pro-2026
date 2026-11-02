"""Zweite Oberfläche erkennt echte Kern-Sperre und bleibt Nur-Leser."""
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from videozoom.core import Workflow
from videozoom.webui import Bedienung


class ZweitesFenster(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        root=Path(self.tmp.name);(root/'Downloads').mkdir()
        self.cfg={'downloads':str(root/'Downloads'),'arbeitsordner':str(root/'Arbeit')}
        self.service=Workflow(self.cfg,testmodus=True)
        self.service.zustand['auftraege']['a']={'status':'LAEUFT','titel':'Song'}
        self.service.speichern()
        self.ui=Bedienung(self.cfg,root/'cfg.json')

    def test_aktive_fremde_sperre_zeigt_journal_ohne_zweiten_workflow(self):
        self.service.sperren();self.addCleanup(self.service.freigeben)
        before=self.service.journal.read_bytes()
        with patch('videozoom.webui.Workflow',side_effect=AssertionError('Kein zweiter Schreiber')):
            status=self.ui.status()
            self.assertTrue(status['andere_instanz']);self.assertFalse(status['active'])
            self.assertEqual(status['jobs'],{'LAEUFT':1});self.assertIsNone(status['video']['prozent'])
            for mode in ('prepare','batch','once','watch','stop'):
                with self.subTest(mode=mode),self.assertRaisesRegex(RuntimeError,'Anderes Fenster'):
                    self.ui.aktion(mode)
        self.assertEqual(self.service.journal.read_bytes(),before)

    def test_fremde_sperre_blockiert_ruecksetzen_und_einstellungswrite(self):
        self.service.sperren();self.addCleanup(self.service.freigeben)
        with self.assertRaises(RuntimeError):self.ui.ruecksetzen('zuruecksetzen','ansicht')
        with self.assertRaises(RuntimeError):self.ui.einstellungen({'theme':'orange'})
        self.assertFalse(self.ui.config_path.exists())

    def test_nach_freigabe_keine_altersbasierte_sperrloeschung(self):
        self.service.sperren();self.assertTrue(self.ui.status()['andere_instanz'])
        self.service.freigeben()
        self.assertFalse(self.ui.status()['andere_instanz'])
        self.assertTrue((self.service.ordner/'PROTOKOLLE'/'dienst.lock').exists())
        self.ui.einstellungen({'theme':'orange'})
        self.assertTrue(self.ui.config_path.exists())

    def test_eigener_worker_nicht_als_fremd_anzeigen(self):
        self.ui.thread=SimpleNamespace(is_alive=lambda:True);self.ui.service=self.service
        with patch.object(self.ui,'_anderer_schreiber',side_effect=AssertionError('Eigene Sperre')):
            status=self.ui.status()
        self.assertTrue(status['active']);self.assertFalse(status['andere_instanz'])

    def test_alter_service_wird_bei_inaktivitaet_nicht_als_live_journal_genutzt(self):
        self.ui.service=self.service
        self.service.journal.write_text(json.dumps({'schema':1,'auftraege':{'b':{'status':'ARCHIVIERT'}}}))
        self.assertEqual(self.ui.status()['jobs'],{'ARCHIVIERT':1})

    def test_unsichere_sperre_blockiert_ohne_fremde_datei_zu_aendern(self):
        lock=self.service.ordner/'PROTOKOLLE'/'dienst.lock'
        target=self.service.ordner/'original';target.write_bytes(b'ORIGINAL');lock.symlink_to(target)
        self.assertTrue(self.ui.status()['fehler'])
        with self.assertRaises(RuntimeError):self.ui.aktion('batch')
        self.assertEqual(target.read_bytes(),b'ORIGINAL')
