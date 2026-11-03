"""Belegte Integrationsnegative: Archivfreigabe, Erstvorbereitung, Vorschauerhalt."""
import os
import subprocess
import tempfile
import time
from pathlib import Path
import unittest
from unittest.mock import patch
from tests.fixtures.generieren import wav, png
from videozoom.core import Workflow, pruefsumme
from videozoom.auftraege import freigeben
from videozoom.vorschau import erzeugen, datei


class IntegrationCloseout(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name); downloads = root/'Downloads'; downloads.mkdir()
        self.w = Workflow({'downloads':str(downloads),'arbeitsordner':str(root/'Work'),
                           'format':'KLAS'},testmodus=True)
        self.audio = wav(downloads/'Song.wav')
        self.image = png(self.w.ordner/'EINGANG/song/BILDER/1.png',breite=128,hoehe=96)
        for p in (self.audio,self.image):
            os.utime(p,(time.time()-20,)*2)

    def test_erstfehler_ohne_manifest_bewusst_erneut_vorbereiten(self):
        with patch('videozoom.core.dauer',side_effect=ValueError('FFprobe vorübergehend fehlgeschlagen')):
            self.w.vorbereiten()
        key, job = next(iter(self.w.zustand['auftraege'].items()))
        self.assertEqual(job['status'],'PRUEFEN');self.assertNotIn('dateien',job)
        self.w.vorbereiten()
        self.assertEqual(job['status'],'PRUEFEN')  # Keine automatische Umgehung der Sperre.
        freigeben(self.w,key)
        self.assertEqual(job['status'],'BEREIT');self.assertEqual(len(job['dateien']),2)
        self.assertTrue(self.audio.exists());self.assertTrue(self.image.exists())

    def test_erneute_erstvorbereitung_bleibt_bei_fehlendem_bild_gesperrt(self):
        with patch('videozoom.core.dauer',side_effect=ValueError('Fehler')):
            self.w.vorbereiten()
        key,job=next(iter(self.w.zustand['auftraege'].items()))
        self.image.unlink()
        with self.assertRaises(ValueError):
            freigeben(self.w,key)
        self.assertEqual(job['status'],'PRUEFEN');self.assertNotIn('dateien',job)

    def test_unveraenderte_vorschau_bleibt_neue_bilder_invalidieren(self):
        self.w.vorbereiten();key=next(iter(self.w.zustand['auftraege']))
        target=erzeugen(self.w,key);meta=dict(self.w.zustand['auftraege'][key]['vorschau'])
        for _ in range(2):
            self.w.vorbereiten()
            current=self.w.zustand['auftraege'][key]
            self.assertEqual(current['vorschau'],meta)
            self.assertEqual(datei(self.w.ordner,current),target)
        png(self.image,(20,140,200),breite=128,hoehe=96)
        os.utime(self.image,(time.time()-20,)*2)
        self.w.vorbereiten()
        self.assertNotIn('vorschau',self.w.zustand['auftraege'][key])
        self.assertTrue(target.exists())  # Keine ungeprüfte Löschung eigener alter Vorschauen.

    def test_hashallein_erlaubt_keine_archivierung_eines_ungueltigen_altvideos(self):
        self.w.vorbereiten();key,job=next(iter(self.w.zustand['auftraege'].items()))
        video=self.w.ordner/'FERTIG/song_KLAS.mp4'
        subprocess.run(['ffmpeg','-v','error','-f','lavfi','-i','color=s=128x96:r=25:d=4',
                        '-i',str(self.audio),'-c:v','libx264','-threads','1','-c:a','aac',
                        '-t','4',str(video)],check=True,timeout=20)
        job.update(status='LAEUFT',video_ziel=str(video),render_hash=pruefsumme(video))
        self.w._recover_inflight();self.assertEqual(job['status'],'PRUEFEN')
        with self.assertRaisesRegex(RuntimeError,'Videoprüfung'):
            freigeben(self.w,key)
        self.assertEqual(job['status'],'PRUEFEN')
        with patch.object(self.w,'_archive',side_effect=AssertionError('Ungültiges Archiv')):
            self.w.stapel()
        self.assertTrue(self.audio.exists());self.assertTrue(self.image.exists())
        self.assertFalse(list((self.w.ordner/'VERWENDET').iterdir()))
