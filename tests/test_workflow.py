"""Fokustests plus echte FFmpeg-Ausgabe und gesicherte Archivierung."""
from __future__ import annotations
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from videozoom.core import (
    Workflow, kategorie, titel, slug, FORMATE, zeitplan, ffmpeg_befehl,
    konfiguration, json_sicher, lesen, kopieren_und_archivieren, quota_befehl,
)
from videozoom.diagnose import installation_simulieren, pruefen
from tests.fixtures.generieren import wav, png


class Regeln(unittest.TestCase):
    def test_titel_und_urls(self):
        self.assertEqual(titel("Mein-neuer-Song_suno-com-123_20261101.wav"),"Mein-neuer-Song")
        self.assertEqual(titel("Schön & laut.wav"),"Schön laut")
        self.assertEqual(slug("Grüße von PPPOPPI"),"grusse-von-pppoppi")

    def test_bildkategorien(self):
        self.assertEqual(kategorie("ChatGPT_Provoware_Cover.png"),"PROVOWARE")
        self.assertEqual(kategorie("ChatGPT_THEMa_Design.webp"),"THEMA")
        self.assertEqual(kategorie("ChatGPT_CODING_Code.png"),"CODING")
        self.assertIsNone(kategorie("ChatGPT_CODING_PROVOWARE.png"))
        self.assertIsNone(kategorie("unbekannt.png"))

    def test_formatcodes(self):
        self.assertEqual(FORMATE["HOCH"],(1080,1920))
        self.assertEqual(FORMATE["KLAS"],(800,600))

    def test_zeitplan(self):
        schnell,langsam,blende=zeitplan(12.0,4)
        self.assertGreater(langsam,schnell)
        self.assertGreaterEqual(blende,0)
        with self.assertRaises(ValueError): zeitplan(1.0,10)

    def test_ffmpeg_reihenfolge_und_zoom(self):
        cfg=konfigurieren({"format":"KLAS"})
        cmd=ffmpeg_befehl(Path("audio.wav"),[Path("1.png"),Path("2.png")],
                          Path("ziel.mp4"),8.0,cfg)
        text=" ".join(cmd)
        self.assertIn("zoompan=",text)
        self.assertIn("xfade=transition=",text)
        self.assertIn("[s1][s0]concat=n=2",text)
        self.assertIn("800x600",text)

    def test_quota_skalierung(self):
        cfg=konfigurieren({})
        command=quota_befehl(["ffmpeg","-version"],cfg)
        self.assertIn("MemoryMax=2048M",command)
        self.assertTrue(any("CPUQuota=" in s for s in command))

    def test_paket_aenderungen_verhindern(self):
        with patch("videozoom.diagnose.shutil.which",return_value="/usr/bin/apt-get"), \
             patch("videozoom.diagnose.run",return_value=(True,"Remv wichtig\nInst ffmpeg\n")):
            self.assertFalse(installation_simulieren(["ffmpeg"])["sicher"])
        self.assertFalse(installation_simulieren(["fremdpaket"])["sicher"])

    def test_diagnose_ohne_tk(self):
        checks=pruefen(real_scope=False)
        self.assertIn("ffmpeg",[x["name"] for x in checks["pruefungen"]])
        self.assertNotIn("tkinter",str(checks))

    def test_journal_sicher(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp); target=folder/"journal.json"
            json_sicher(target,{"schema":1,"auftraege":{}})
            self.assertEqual(lesen(target,{}).get("schema"),1)
            target.write_text("{kaputt",encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError,"Auftragsjournal beschädigt"):
                lesen(target,{})

    def test_archiv_kollision_und_wiederaufnahme(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); src=root/"song.wav"; dst=root/"archiv"/"song_verwendet_.wav"
            src.write_bytes(b"testbytes"*20)
            from videozoom.core import pruefsumme
            digest=pruefsumme(src)
            kopieren_und_archivieren(src,dst,digest)
            self.assertFalse(src.exists())
            kopieren_und_archivieren(src,dst,digest)
            self.assertEqual(pruefsumme(dst),digest)

    def test_chatgpt_bilder_sortieren_und_metadaten(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); down=root/"Downloads"; down.mkdir()
            source=png(down/"ChatGPT_Provovare_Cover.png")
            fremd=png(down/"NichtZuordnen.png",(20,40,90))
            past=time.time()-20
            for file in (source,fremd):
                os.utime(file,(past,past))
            work=root/"Projekt"
            dienst=Workflow({"downloads":str(down),"arbeitsordner":str(work)})
            self.assertEqual(dienst.bilder_einsortieren(),(1,1))
            dest=work/"BILDER"/"PROVOWARE"/source.name
            self.assertTrue(dest.exists())
            self.assertFalse(source.exists())
            self.assertTrue(fremd.exists())
            import json
            meta=json.loads((dest.parent/(dest.name+".json")).read_text())
            self.assertEqual((meta["breite"],meta["hoehe"]),(64,48))
            self.assertEqual(meta["kategorie"],"PROVOWARE")

    def test_zweite_instanz_gesperrt(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); (root/"Downloads").mkdir()
            cfg={"downloads":str(root/"Downloads"),"arbeitsordner":str(root/"Arbeit")}
            first=Workflow(cfg); second=Workflow(cfg)
            first.sperren()
            try:
                with self.assertRaisesRegex(RuntimeError,"Bereits eine Verarbeitung"):
                    second.sperren()
            finally: first.freigeben()


@unittest.skipUnless(__import__("shutil").which("ffmpeg") and __import__("shutil").which("ffprobe"),
                     "FFmpeg fehlt; Medien-Integrationstest übersprungen.")
class Medien(unittest.TestCase):
    def test_vorbereiten_dann_rendern_und_archivieren(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); down=root/"Downloads";down.mkdir()
            audio=wav(down/"TEST Song_suno-com-123_20261101.wav",sekunden=5)
            work=root/"Arbeit"
            imgs=work/"EINGANG"/"test-song"/"BILDER"
            first=png(imgs/"bild_01.png")
            second=png(imgs/"bild_02.png",(25,145,215))
            for path in (audio,first,second):
                past=time.time()-20
                os.utime(path,(past,past))
            cfg={"downloads":str(down),"arbeitsordner":str(work),"format":"KLAS"}
            service=Workflow(cfg,testmodus=True)
            self.assertEqual(service.vorbereiten()[0],1)
            self.assertFalse(list((work/"FERTIG").glob("*.mp4")))
            done,remaining=service.stapel()
            self.assertEqual((done,remaining),(1,0))
            vids=list((work/"FERTIG").glob("*.mp4"))
            self.assertEqual(len(vids),1)
            self.assertEqual(next(iter(service.zustand["auftraege"].values()))["status"],"ARCHIVIERT")
            self.assertFalse(audio.exists())
            self.assertEqual(len(list((work/"VERWENDET").iterdir())),3)
            self.assertEqual(service.stapel()[0],0)


if __name__=="__main__":
    unittest.main()
