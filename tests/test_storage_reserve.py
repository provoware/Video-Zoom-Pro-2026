"""Künstlich knapper Datenträger: keine falsche Fertigmeldung oder Quelllöschung."""
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import patch
from videozoom.core import Workflow, speicher_pruefen, SpeicherWartet, pruefsumme, kopieren_und_archivieren


class SpeicherReserve(unittest.TestCase):
    def test_reserve_grenze(self):
        with patch('videozoom.core.shutil.disk_usage',return_value=SimpleNamespace(free=300)):
            speicher_pruefen(Path('.'),200,reserve=100)
            with self.assertRaises(SpeicherWartet):speicher_pruefen(Path('.'),201,reserve=100)

    def test_kopie_bei_platzmangel_original_unveraendert(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);src=root/'src.wav';src.write_bytes(b'ORIGINAL'*500)
            dest=root/'archiv'/'ziel.wav';digest=pruefsumme(src)
            with patch('videozoom.core.shutil.disk_usage',return_value=SimpleNamespace(free=0)):
                with self.assertRaises(SpeicherWartet):kopieren_und_archivieren(src,dest,digest)
            self.assertEqual(pruefsumme(src),digest);self.assertFalse(dest.exists())
            kopieren_und_archivieren(src,dest,digest)
            self.assertFalse(src.exists());self.assertEqual(pruefsumme(dest),digest)

    def workflow(self,root):
        downloads=root/'Downloads';downloads.mkdir()
        return Workflow({'downloads':str(downloads),'arbeitsordner':str(root/'Arbeit'),'format':'KLAS'},testmodus=True)

    def test_render_startet_bei_platzmangel_nicht_kein_fehlversuch(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);svc=self.workflow(root)
            audio=svc.downloads/'a.wav';audio.write_bytes(b'a'*200)
            image=svc.ordner/'EINGANG'/'a'/'BILDER'/'a.png';image.parent.mkdir(parents=True);image.write_bytes(b'b'*200)
            job={'titel':'a','status':'BEREIT','versuche':2,'laenge':4,
                 'dateien':[{'pfad':str(p),'sha256':pruefsumme(p)} for p in (audio,image)]}
            svc.zustand['auftraege']['a']=job
            with patch('videozoom.core.shutil.disk_usage',return_value=SimpleNamespace(free=1)), patch('videozoom.core.rendern') as renderer:
                self.assertEqual(svc.stapel(),(0,1));renderer.assert_not_called()
            self.assertEqual(job['status'],'PAUSIERT');self.assertEqual(job['versuche'],2)
            self.assertIn('Speicher',job['hinweis']);self.assertTrue(audio.exists());self.assertTrue(image.exists())
            self.assertEqual(list((svc.ordner/'FERTIG').iterdir()),[])

    def test_archiv_gesamtreserve_vor_erster_quellbewegung(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);svc=self.workflow(root)
            audio=svc.downloads/'a.wav';audio.write_bytes(b'a'*200)
            image=svc.ordner/'EINGANG'/'a'/'BILDER'/'a.png';image.parent.mkdir(parents=True);image.write_bytes(b'b'*200)
            output=svc.ordner/'FERTIG'/'a.mp4';output.write_bytes(b'video')
            job={'titel':'a','status':'ARCHIV_WARTET','archiv_versuche':2,'video':str(output),'video_hash':pruefsumme(output),
                 'dateien':[{'pfad':str(p),'sha256':pruefsumme(p)} for p in (audio,image)]}
            svc.zustand['auftraege']['a']=job
            with patch('videozoom.core.shutil.disk_usage',return_value=SimpleNamespace(free=1)):
                svc.stapel()
            self.assertEqual(job['status'],'ARCHIV_WARTET');self.assertEqual(job['archiv_versuche'],2)
            self.assertTrue(audio.exists());self.assertTrue(image.exists());self.assertTrue(output.exists())
            self.assertEqual(list((svc.ordner/'VERWENDET').iterdir()),[])

    def test_unabhaengiger_auftrag_wird_trotz_platzwartefall_bearbeitet(self):
        with tempfile.TemporaryDirectory() as tmp:
            svc=self.workflow(Path(tmp))
            for key in ('gross','klein'):
                svc.zustand['auftraege'][key]={'titel':key,'status':'BEREIT','dateien':[],'versuche':0,'laenge':4}
            def render(job):
                if job['titel']=='gross':raise SpeicherWartet('Platz freigeben')
                output=svc.ordner/'FERTIG'/'klein.mp4';output.write_bytes(b'video');return output
            with patch.object(svc,'_render',side_effect=render):
                self.assertEqual(svc.stapel(),(1,1))
            self.assertEqual(svc.zustand['auftraege']['gross']['versuche'],0)
            self.assertEqual(svc.zustand['auftraege']['klein']['status'],'ARCHIVIERT')
