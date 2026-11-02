"""Pausierte synthetische Downloads dürfen keine Produktion auslösen."""
import os
from pathlib import Path
import struct
import tempfile
import unittest
from unittest.mock import patch
from videozoom.wav_eingang import vollstaendig, DownloadWartet
from videozoom.core import Workflow
from tests.fixtures.generieren import wav, png


class WAVVollstaendigkeit(unittest.TestCase):
    def test_gueltige_wav_und_abgeschnittener_alter_download(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=wav(Path(tmp)/'Song.wav');raw=p.read_bytes()
            vollstaendig(p)
            p.write_bytes(raw[:-50]);os.utime(p,(1,1))
            with self.assertRaises(DownloadWartet):vollstaendig(p)
            self.assertEqual(p.read_bytes(),raw[:-50])
            p.write_bytes(raw);vollstaendig(p)

    def test_header_platzhalter_und_beschaedigter_inhalt(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'Song.wav'
            p.write_bytes(b'RIFF'+struct.pack('<I',0)+b'WAVE')
            with self.assertRaises(DownloadWartet):vollstaendig(p)
            p.write_bytes(b'kaputt'*30)
            with self.assertRaisesRegex(ValueError,'Ungültiger WAV'):vollstaendig(p)

    def test_rf64_groessen_werden_beruecksichtigt(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'RF.wav'
            fmt=b'fmt '+struct.pack('<IHHIIHH',16,1,1,8000,16000,2,16)
            body=fmt+b'data'+struct.pack('<I',0xffffffff)+b'\0'*200
            length=12+36+len(body)
            p.write_bytes(b'RF64'+struct.pack('<I',0xffffffff)+b'WAVEds64'+struct.pack('<IQQQI',28,length-8,200,100,0)+body)
            vollstaendig(p)
            p.write_bytes(p.read_bytes()[:-10])
            with self.assertRaises(DownloadWartet):vollstaendig(p)

    def test_aenderung_waehrend_pruefung_ist_warten(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=wav(Path(tmp)/'Song.wav')
            real=os.fstat;calls=0
            def changing(fd):
                nonlocal calls
                calls+=1
                if calls==2:os.utime(p,ns=(1,2))
                return real(fd)
            with patch('videozoom.wav_eingang.os.fstat',side_effect=changing):
                with self.assertRaises(DownloadWartet):vollstaendig(p)

    def test_teil_wav_wartet_und_wiederanlauf_ist_bereit(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);downloads=root/'Downloads';downloads.mkdir()
            p=wav(downloads/'Song.wav');raw=p.read_bytes();p.write_bytes(raw[:-100]);os.utime(p,(1,1))
            svc=Workflow({'downloads':str(downloads),'arbeitsordner':str(root/'Arbeit')},testmodus=True)
            image=png(svc.ordner/'EINGANG'/'song'/'BILDER'/'1.png');os.utime(image,(1,1))
            self.assertEqual(svc.vorbereiten(),(0,1))
            job=next(iter(svc.zustand['auftraege'].values()))
            self.assertEqual(job['status'],'WARTET');self.assertEqual(job['versuche'],0)
            self.assertEqual(p.read_bytes(),raw[:-100])
            p.write_bytes(raw);os.utime(p,(1,1))
            self.assertEqual(svc.vorbereiten(),(1,0))
            self.assertEqual(next(iter(svc.zustand['auftraege'].values()))['status'],'BEREIT')
