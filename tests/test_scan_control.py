"""Getrennte Scanwahl, sichere Arbeitskopien, Reset und sparsamer unveränderter Eingang."""
import os
import tempfile
import time
from pathlib import Path
import unittest
from unittest.mock import patch
from tests.fixtures.generieren import wav,png
from videozoom.core import Workflow,konfigurieren,pruefsumme
from videozoom.eingang import uebernehmen,fundliste_neu,auswahl,kopie,ordner_pruefen


class ScanControl(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name);(self.root/'Downloads').mkdir()
        self.cfg={'downloads':str(self.root/'Downloads'),'arbeitsordner':str(self.root/'Work'),
                  'format':'KLAS','audio_auto':False,'bilder_auto':False}
        self.w=Workflow(self.cfg,testmodus=True)
        self.audio=wav(self.root/'Originale/Song.wav')
        self.image=png(self.root/'Originale/Bild.png',breite=128,hoehe=96)
        for p in (self.audio,self.image):os.utime(p,(time.time()-20,)*2)

    def test_manuelle_auswahl_bis_archivierung_originale_bleiben(self):
        hashes=[pruefsumme(p) for p in (self.audio,self.image)]
        uebernehmen(self.w,'audio',[self.audio])
        key=next(iter(self.w.zustand['auftraege']))
        self.assertEqual(self.w.zustand['auftraege'][key]['status'],'WARTET')
        uebernehmen(self.w,'bilder',[self.image],key)
        self.assertEqual(self.w.zustand['auftraege'][key]['status'],'BEREIT')
        self.assertEqual(self.w.stapel(),(1,0))
        self.assertEqual([pruefsumme(p) for p in (self.audio,self.image)],hashes)
        self.assertEqual(self.w.zustand['auftraege'][key]['status'],'ARCHIVIERT')

    def test_audio_und_bilder_auto_unabhaengig(self):
        audio=wav(self.root/'Downloads/Auto.wav');os.utime(audio,(time.time()-20,)*2)
        self.w.vorbereiten();self.assertEqual(self.w.zustand['auftraege'],{})
        self.w.cfg['audio_auto']=True;self.w.vorbereiten()
        key=next(iter(self.w.zustand['auftraege']))
        image=png(self.w.ordner/'EINGANG/auto/BILDER/auto.png',breite=128,hoehe=96)
        os.utime(image,(time.time()-20,)*2)
        self.w.vorbereiten();self.assertEqual(self.w.zustand['auftraege'][key]['status'],'WARTET')
        self.w.cfg['bilder_auto']=True;self.w.vorbereiten()
        self.assertEqual(self.w.zustand['auftraege'][key]['status'],'BEREIT')

    def test_reset_sichert_und_erhaelt_schutzstatus_und_auswahl(self):
        uebernehmen(self.w,'audio',[self.audio]);key=next(iter(self.w.zustand['auftraege']))
        uebernehmen(self.w,'bilder',[self.image],key)
        original=self.w.journal.read_bytes()
        for state in ('PRUEFEN','PAUSIERT','LAEUFT','ARCHIVIERT','ARCHIV_WARTET','FERTIG'):
            self.w.zustand['auftraege'][state]={'status':state,'titel':state,'versuche':3}
        self.w.speichern();original=self.w.journal.read_bytes()
        fundliste_neu(self.w)
        self.assertEqual(self.w.zustand['auftraege'][key]['status'],'BEREIT')
        for state in ('PRUEFEN','PAUSIERT','LAEUFT','ARCHIVIERT','ARCHIV_WARTET','FERTIG'):
            self.assertEqual(self.w.zustand['auftraege'][state]['status'],state)
        backups=list((self.w.ordner/'PROTOKOLLE/SICHERUNGEN').glob('fundliste-*.json'))
        self.assertEqual(len(backups),1)
        import json
        self.assertEqual(json.loads(backups[0].read_text()),json.loads(original))
        self.assertTrue(auswahl(self.w)['audio'])

    def test_unveraenderte_eingaenge_vermeiden_medienpruefung_und_hashen(self):
        uebernehmen(self.w,'audio',[self.audio]);key=next(iter(self.w.zustand['auftraege']))
        uebernehmen(self.w,'bilder',[self.image],key)
        with patch('videozoom.core.dauer',side_effect=AssertionError('Unnötige Prüfung')), \
             patch('videozoom.core.pruefsumme',side_effect=AssertionError('Unnötiges Hashen')):
            self.assertEqual(self.w.vorbereiten(),(1,0))
        p=Path(self.w.zustand['auftraege'][key]['dateien'][0]['pfad'])
        raw=p.read_bytes();p.write_bytes(raw[:-1]+bytes([raw[-1]^1]))
        with self.assertRaisesRegex(RuntimeError,'Quellmedium'):
            self.w._render(self.w.zustand['auftraege'][key])

    def test_ungueltige_auswahl_symlink_und_beschaedigtes_audio(self):
        link=self.root/'Link.wav';link.symlink_to(self.audio)
        with self.assertRaisesRegex(RuntimeError,'Verknüpfte'):
            uebernehmen(self.w,'audio',[link])
        bad=self.root/'defekt.wav';bad.write_bytes(b'X'*1000);os.utime(bad,(time.time()-20,)*2)
        with self.assertRaises(ValueError):uebernehmen(self.w,'audio',[bad])
        self.assertEqual(self.w.zustand['auftraege'],{})
        for value in ('false',0,None):
            with self.assertRaises(ValueError):konfigurieren({'audio_auto':value})

    def test_importstopp_behaelt_original_und_keine_teilkopie(self):
        self.w.stop.set()
        with self.assertRaises(RuntimeError):kopie(self.audio,self.w.ordner/'Kopie',self.w.stop)
        self.assertTrue(self.audio.exists());self.assertFalse(list((self.w.ordner/'Kopie').glob('*.teil')))

    def test_ordner_nur_bewusst_anlegen_und_status_wahrheitsgetreu(self):
        cfg={**self.cfg,'downloads':str(self.root/'Neu/Eingang'),'arbeitsordner':str(self.root/'Neu/Arbeit')}
        self.assertFalse(ordner_pruefen(cfg)['bereit'])
        self.assertFalse((self.root/'Neu').exists())
        self.assertTrue(ordner_pruefen(cfg,anlegen=True)['bereit'])
        self.assertTrue(Path(cfg['downloads']).is_dir())
        self.assertTrue(Path(cfg['arbeitsordner']).is_dir())

    def test_ordner_datei_verknuepfung_und_verschachtelung_blockieren(self):
        blocked=self.root/'Datei';blocked.write_text('behalten')
        with self.assertRaises(ValueError):ordner_pruefen({**self.cfg,'downloads':str(blocked)},True)
        link=self.root/'Link';link.symlink_to(self.root/'Downloads',target_is_directory=True)
        with self.assertRaises(RuntimeError):ordner_pruefen({**self.cfg,'downloads':str(link)},True)
        with self.assertRaises(ValueError):ordner_pruefen({**self.cfg,'arbeitsordner':str(self.root/'Downloads/Work')},True)
        (self.w.ordner/'AUSWAHL').mkdir(exist_ok=True)
        (self.w.ordner/'AUSWAHL').rmdir();(self.w.ordner/'AUSWAHL').write_text('behalten')
        with self.assertRaises(ValueError):ordner_pruefen(self.cfg,True)
        self.assertEqual(blocked.read_text(),'behalten')

    def test_hauptoberflaeche_ordnerstatus_und_bewusstes_speichern(self):
        from videozoom.webui import Bedienung
        cfg={**self.cfg,'downloads':str(self.root/'EingangNeu'),'arbeitsordner':str(self.root/'WorkNeu')}
        ui=Bedienung(cfg,self.root/'cfg.json')
        self.assertFalse(ui.status()['ordner']['bereit'])
        self.assertFalse(Path(cfg['arbeitsordner']).exists())
        ui.einstellungen(cfg)
        self.assertTrue(ui.status()['ordner']['bereit'])
        self.assertTrue((self.root/'cfg.json').is_file())

    def test_sensor_und_statusbudget_lassen_letzten_fortschritt_sichtbar(self):
        with patch('videozoom.core.time.monotonic',return_value=10), \
             patch.object(self.w.sensoren,'lesen',return_value={}) as sensor:
            self.w._sensor_cache=None
            for _ in range(20):self.w.status()
            self.assertEqual(sensor.call_count,1)
        with patch('videozoom.core.time.monotonic',return_value=10), \
             patch('videozoom.core.json_sicher') as write:
            self.w._status_phase=None
            for i in range(20):self.w.fortschreiben('video',i)
            self.assertEqual(write.call_count,1)
            self.assertEqual(self.w.ereignis['prozent'],19)
            self.w.fortschreiben('video',100)
            self.assertEqual(write.call_count,2)

    def test_leerlauf_bremst_scan_und_aenderung_setzt_pause_zurueck(self):
        pauses=[]
        def warten(value):
            pauses.append(value)
            if len(pauses)==5:self.w.stop.set()
        def vorbereiten():
            if len(pauses)==4:self.w.zustand['neu']='sichtbare Änderung'
        with patch.object(self.w,'stapel'),patch.object(self.w,'vorbereiten',side_effect=vorbereiten), \
             patch.object(self.w.stop,'wait',side_effect=warten):
            self.w.beobachten()
        self.assertLessEqual(max(pauses),max(60,self.w.cfg['intervall']))
        self.assertGreater(pauses[2],self.w.cfg['intervall'])
        self.assertEqual(pauses[-1],self.w.cfg['intervall'])

    def test_uebergeordnete_pfadschritte_umgehen_keine_ordnergrenze(self):
        (self.root/'Anderer').mkdir()
        path=str(self.root/'Anderer/../Downloads/Arbeit')
        with self.assertRaisesRegex(ValueError,'Zielpfad'):
            ordner_pruefen({**self.cfg,'arbeitsordner':path},True)
        with self.assertRaisesRegex(ValueError,'Zielpfad'):
            konfigurieren({**self.cfg,'arbeitsordner':path})
        self.assertFalse((self.root/'Downloads/Arbeit').exists())
