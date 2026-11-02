"""Einstellungsrücksetzung: Sicherung, Wiederanlauf, Fehler und aktive Produktion."""
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from videozoom.core import konfigurieren
from videozoom.webui import Bedienung


class SichereBedienwerte(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name);self.downloads=self.root/'Downloads';self.downloads.mkdir()
        self.path=self.root/'cfg'/'settings.json';self.path.parent.mkdir()
        self.cfg=konfigurieren({'downloads':str(self.downloads),'arbeitsordner':str(self.root/'Arbeit'),
                              'theme':'orange','format':'HOCH','kategorie':'THEMA','cpu_prozent':17,'ram_mb':768})
        self.original=json.dumps(self.cfg,ensure_ascii=False,indent=3).encode()+b'\n'
        self.path.write_bytes(self.original);self.ui=Bedienung(self.cfg,self.path)

    def test_reset_nur_auswahl_exakte_sicherung_und_neustart_restore(self):
        self.ui.ruecksetzen('zuruecksetzen','format')
        self.assertEqual(self.ui.cfg['format'],'BREI');self.assertEqual(self.ui.cfg['kategorie'],'PROVOWARE')
        self.assertEqual(self.ui.cfg['theme'],'orange')
        backups=list(self.path.parent.glob('settings.json.sicherung-*.json'))
        self.assertEqual(len(backups),1);self.assertEqual(backups[0].read_bytes(),self.original)
        self.assertEqual(backups[0].stat().st_mode&0o777,0o600)
        ui=Bedienung(json.loads(self.path.read_text()),self.path)
        ui.ruecksetzen('wiederherstellen',None)
        self.assertEqual(ui.cfg,self.cfg)

    def test_restore_ueberschreibt_keine_seither_geaenderten_anderen_werte(self):
        self.ui.ruecksetzen('zuruecksetzen','ansicht')
        self.ui.einstellungen({'format':'QUAD','cpu_prozent':12})
        self.ui.ruecksetzen('wiederherstellen',None)
        self.assertEqual(self.ui.cfg['theme'],'orange')
        self.assertEqual(self.ui.cfg['format'],'QUAD');self.assertEqual(self.ui.cfg['cpu_prozent'],12)

    def test_aktive_produktion_nur_farbschema_speichern(self):
        self.ui.thread=SimpleNamespace(is_alive=lambda:True)
        worker=SimpleNamespace(cfg=dict(self.cfg));self.ui.service=worker
        self.ui.einstellungen({'theme':'gruen'})
        self.assertEqual(self.ui.cfg['theme'],'gruen');self.assertEqual(worker.cfg,self.cfg)
        for values in ({'format':'QUAD'},{'downloads':str(self.root)},{'ram_mb':512}):
            with self.subTest(values=values),self.assertRaises(RuntimeError):self.ui.einstellungen(values)
        with self.assertRaises(RuntimeError):self.ui.ruecksetzen('zuruecksetzen','ansicht')
        self.assertEqual(list(self.path.parent.glob('*.sicherung-*')),[])

    def test_schreibfehler_erhaelt_original_und_sicherung(self):
        from videozoom import einstellungen_sicher as safe
        real=safe.json_sicher
        def fail(path,value):
            if Path(path)==self.path:raise OSError('Datenträger voll')
            return real(path,value)
        with patch.object(safe,'json_sicher',side_effect=fail),self.assertRaises(OSError):
            self.ui.ruecksetzen('zuruecksetzen','bedienung')
        self.assertEqual(self.path.read_bytes(),self.original);self.assertEqual(self.ui.cfg,self.cfg)
        self.assertEqual(next(self.path.parent.glob('*.sicherung-*')).read_bytes(),self.original)

    def test_fremde_aenderung_wird_nicht_ueberschrieben(self):
        self.path.write_text(json.dumps({**self.cfg,'theme':'violett'}))
        before=self.path.read_bytes()
        with self.assertRaises(RuntimeError):self.ui.ruecksetzen('zuruecksetzen','ansicht')
        self.assertEqual(self.path.read_bytes(),before)

    def test_beschaedigte_sicherung_und_pfadausbruch_verhindert(self):
        self.ui.ruecksetzen('zuruecksetzen','ansicht')
        marker=self.path.with_name(self.path.name+'.ruecksetzung.json');beleg=json.loads(marker.read_text())
        backup=self.path.with_name(beleg['datei']);backup.write_text('{}')
        before=self.path.read_bytes()
        with self.assertRaises(ValueError):self.ui.ruecksetzen('wiederherstellen',None)
        for name in ('../fremd.json','/tmp/fremd.json',[]):
            marker.write_text(json.dumps({**beleg,'datei':name}))
            with self.subTest(name=name),self.assertRaises(ValueError):self.ui.ruecksetzen('wiederherstellen',None)
        self.assertEqual(self.path.read_bytes(),before)

    def test_symlink_und_ungueltige_gruppe_verhindert(self):
        for gruppe in ('alle_dateien',None,[]):
            with self.subTest(gruppe=gruppe),self.assertRaises(ValueError):self.ui.ruecksetzen('zuruecksetzen',gruppe)
        self.path.unlink();target=self.root/'fremd';target.write_bytes(self.original);self.path.symlink_to(target)
        with self.assertRaises(RuntimeError):self.ui.ruecksetzen('zuruecksetzen','ansicht')
        self.assertEqual(target.read_bytes(),self.original)

    def test_ruecksetzen_loescht_keine_medien_oder_ordner(self):
        source=self.downloads/'original.wav';source.write_bytes(b'ORIGINAL')
        self.ui.ruecksetzen('zuruecksetzen','bedienung')
        for key in ('downloads','arbeitsordner','cpu_prozent','ram_mb'):
            self.assertEqual(self.ui.cfg[key],self.cfg[key])
        self.assertEqual(source.read_bytes(),b'ORIGINAL');self.assertFalse((self.root/'Arbeit').exists())

    def test_echte_http_ruecksetzung_und_zugriffsschutz(self):
        import threading
        from urllib.request import Request,urlopen
        from urllib.error import HTTPError
        from videozoom.webui import starten
        refs={};ready=threading.Event()
        def callback(server,url):refs.update(server=server,url=url);ready.set()
        thread=threading.Thread(target=starten,args=(self.cfg,self.path),kwargs={'browser':False,'bereit':callback},daemon=True)
        thread.start();self.assertTrue(ready.wait(5))
        root,token=refs['url'].split('/?')
        body=json.dumps({'modus':'zuruecksetzen','gruppe':'ansicht'}).encode()
        try:
            for suffix,headers in (('',{}),('?'+token,{'Origin':'https://fremd.invalid'})):
                req=Request(root+'/ruecksetzen'+suffix,data=body,headers={'Content-Type':'application/json',**headers})
                with self.assertRaises(HTTPError) as exc:urlopen(req,timeout=4)
                self.assertEqual(exc.exception.code,403)
            self.assertEqual(self.path.read_bytes(),self.original)
            req=Request(root+'/ruecksetzen?'+token,data=body,headers={'Content-Type':'application/json'})
            with urlopen(req,timeout=4) as response:
                self.assertEqual(json.loads(response.read())['cfg']['theme'],'cyan')
            req=Request(root+'/ruecksetzen?'+token,data=b'{"modus":"wiederherstellen"}',headers={'Content-Type':'application/json'})
            with urlopen(req,timeout=4) as response:
                self.assertEqual(json.loads(response.read())['cfg']['theme'],'orange')
        finally:
            refs['server'].shutdown();thread.join(5);self.assertFalse(thread.is_alive())
