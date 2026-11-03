"""Beenden mit echten HTTP-/Signalszenarien und begrenzter Fensterüberwachung."""
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import Mock,patch
from urllib.request import Request,urlopen
from videozoom.webui import Bedienung,starten
from videozoom.lebenszyklus import Lebenszyklus
from videozoom.core import json_sicher


class Lifecycle(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name);(self.root/'Downloads').mkdir()
        self.cfg={'downloads':str(self.root/'Downloads'),'arbeitsordner':str(self.root/'Work'),
                  'audio_auto':False,'bilder_auto':False}
        self.ui=Bedienung(self.cfg,self.root/'settings.json')
        self.clock=[0.0];self.server=Mock();self.life=Lebenszyklus(self.ui,self.server,uhr=lambda:self.clock[0])

    def test_zwei_fenster_reload_und_ungeordnete_beacons(self):
        self.life.fenster('a','da',seq=1);self.life.fenster('b','da',seq=1)
        self.life.fenster('a','weg',seq=3);self.life.fenster('a','da',seq=2)
        self.assertEqual(set(self.life.clients),{'b'})
        self.clock[0]=9;self.assertFalse(self.life.fenster_verlassen())
        self.life.fenster('b','weg',seq=2);self.clock[0]=16
        self.assertFalse(self.life.fenster_verlassen())
        self.life.fenster('neu','da',seq=1);self.assertFalse(self.life.fenster_verlassen())
        self.life.fenster('neu','weg',seq=2);self.clock[0]=25
        self.assertTrue(self.life.fenster_verlassen())

    def test_hintergrundfenster_wird_nicht_wie_absturz_behandelt(self):
        self.life.fenster('bg','da',hidden=True)
        self.clock[0]=500;self.assertFalse(self.life.fenster_verlassen())
        self.clock[0]=601;self.assertTrue(self.life.fenster_verlassen())
        for key in ('', '../../x', None):
            with self.assertRaises(ValueError):self.life.fenster(key,'da')

    def test_alte_fenstereinstellung_ueberschreibt_keinen_neuen_stand(self):
        old=dict(self.ui.cfg);self.ui.cfg={**self.ui.cfg,'theme':'orange'}
        self.life.fenster('a','da');self.life.fenster('a','weg',cfg={**old,'theme':'gruen'},base=old)
        self.assertIsNone(self.life.pending_cfg)

    def test_letztes_fenster_sichert_nur_aktuellen_gueltigen_stand(self):
        base=dict(self.ui.cfg)
        self.life.fenster('a','da')
        self.life.fenster('a','weg',cfg={**base,'theme':'orange'},base=base)
        self.life.sichern()
        self.assertEqual(self.ui.cfg['theme'],'orange')
        self.life.fenster('b','da')
        self.assertIsNone(self.life.pending_cfg)
        base=dict(self.ui.cfg)
        self.life.fenster('b','weg',cfg={**base,'theme':'gruen'},base=base)
        self.ui.cfg={**base,'theme':'violett'}
        self.life.sichern()
        self.assertEqual(self.ui.cfg['theme'],'violett')
        self.life.pending_base=dict(self.ui.cfg)
        with patch.object(self.ui,'einstellungen',side_effect=OSError('Datenträger voll')):
            with self.assertRaises(OSError):self.life.sichern()

    def test_speicherfehler_verhindert_scheinbeendigung(self):
        service=Mock();service.stop=threading.Event();service.speichern.side_effect=OSError('Datenträger voll')
        self.ui.service=service
        self.life.starten();self.life.anfordern()
        deadline=time.monotonic()+3
        while self.ui.beenden_fehler is None and time.monotonic()<deadline:time.sleep(.02)
        try:
            self.assertIn('Datenträger',self.ui.beenden_fehler)
            self.assertFalse(self.ui.schliesst);self.server.shutdown.assert_not_called()
            service.freigeben.assert_called_once()
        finally:
            self.life.fertig.set();self.life.thread.join(2)

    def test_http_beenden_stoppt_eigene_automatik_und_sichert(self):
        journal=self.root/'Work/PROTOKOLLE/auftraege.json'
        json_sicher(journal,{'schema':1,'auftraege':{'alt':{'status':'WARTET','titel':'Alter Song'}}})
        refs={};ready=threading.Event()
        def callback(server,url):refs.update(server=server,url=url);ready.set()
        with patch('videozoom.webui.Bedienung',return_value=self.ui):
            thread=threading.Thread(target=starten,args=(self.cfg,self.root/'settings.json'),
                                    kwargs={'browser':False,'bereit':callback},daemon=True)
            thread.start();self.assertTrue(ready.wait(5))
        root,token=refs['url'].split('/?')
        def post(path,data):
            with urlopen(Request(root+path+'?'+token,data=json.dumps(data).encode(),
                                 headers={'Content-Type':'application/json'},method='POST'),timeout=5) as r:
                return json.loads(r.read())
        try:
            post('/aktion',{'mode':'watch'})
            post('/beenden',{})
            thread.join(8);self.assertFalse(thread.is_alive())
            self.assertTrue(refs['server'].lebenszyklus.fertig.is_set())
            self.assertIn('alt',json.loads(journal.read_text())['auftraege'])
            self.assertFalse(self.ui.thread.is_alive())
            with self.assertRaisesRegex(RuntimeError,'beendet'):self.ui.aktion('prepare')
        finally:
            if thread.is_alive():refs['server'].shutdown();thread.join(8)

    def test_sigterm_beendet_echten_server_mit_journal(self):
        from tests.fixtures.generieren import wav
        source=wav(self.root/'Downloads/Song.wav');os.utime(source,(time.time()-20,)*2)
        cfg={**self.cfg,'audio_auto':True}
        code='from videozoom.webui import starten;import json,sys;starten(json.loads(sys.argv[1]),sys.argv[2],browser=False)'
        proc=subprocess.Popen([sys.executable,'-u','-c',code,json.dumps(cfg),str(self.root/'cfg.json')],
                              stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        try:
            import selectors
            with selectors.DefaultSelector() as sel:
                sel.register(proc.stdout,selectors.EVENT_READ)
                self.assertTrue(sel.select(8),'Server nicht bereit')
                line=proc.stdout.readline()
            url=line.split('Lokale Bedienoberfläche: ',1)[1].strip();root,token=url.split('/?')
            with urlopen(Request(root+'/aktion?'+token,data=b'{"mode":"watch"}',
                                 headers={'Content-Type':'application/json'},method='POST'),timeout=5):pass
            deadline=time.monotonic()+5;journal=self.root/'Work/PROTOKOLLE/auftraege.json'
            while not journal.exists() and time.monotonic()<deadline:time.sleep(.02)
            proc.send_signal(signal.SIGTERM)
            _,err=proc.communicate(timeout=8)
            self.assertEqual(proc.returncode,0,err)
            data=json.loads(journal.read_text());self.assertTrue(data['auftraege'])
            self.assertTrue(source.exists())
        finally:
            if proc.poll() is None:proc.kill();proc.communicate(timeout=3)
