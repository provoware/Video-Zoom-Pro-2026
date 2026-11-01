"""Echte localhost-HTTP-Prüfungen für den Tk-freien Browserzugriff."""
from __future__ import annotations
import json
import os
from pathlib import Path
import sys
import tempfile
import threading
import unittest
from subprocess import CompletedProcess
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import Request, urlopen

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from videozoom.core import konfiguration
from videozoom.webui import starten, ordner_waehlen


class BrowserSicherheit(unittest.TestCase):
    def test_token_host_origin_und_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            base=Path(tmp)
            (base/"Downloads").mkdir()
            cfg=konfiguration()
            cfg["downloads"]=str(base/"Downloads")
            cfg["arbeitsordner"]=str(base/"Arbeit")
            refs={}
            ready=threading.Event()

            def callback(server,url):
                refs.update({"server":server,"url":url})
                ready.set()

            thread=threading.Thread(
                target=starten,
                args=(cfg,base/"settings.json"),
                kwargs={"browser":False,"bereit":callback},
                daemon=True,
            )
            thread.start()
            self.assertTrue(ready.wait(8))
            url=refs["url"]
            root=url.split("/?")[0]
            token=url.split("?")[1]
            try:
                with urlopen(root+"/status?"+token,timeout=4) as response:
                    result=json.loads(response.read())
                    self.assertIn("jobs",result)
                    self.assertIn("sensoren",result)
                for target,headers,body in [
                    (root+"/status",{},None),
                    (root+"/status?"+token,{"Host":"fremd.example"},None),
                    (root+"/aktion?"+token,{"Content-Type":"application/json","Origin":"https://fremd.example"},b'{"mode":"stop"}'),
                ]:
                    req=Request(target,data=body,headers=headers,method="POST" if body else "GET")
                    with self.assertRaises(HTTPError) as context:
                        urlopen(req,timeout=4)
                    self.assertEqual(context.exception.code,403)
                with patch("videozoom.webui.ordner_waehlen", return_value=str(base)) as dialog:
                    req=Request(root+"/ordnerwahl?"+token,data=b'{"feld":"downloads"}',
                                headers={"Content-Type":"application/json"},method="POST")
                    with urlopen(req,timeout=4) as response:
                        selected=json.loads(response.read())
                        self.assertEqual(selected["pfad"],str(base))
                    dialog.assert_called_once()
                req=Request(root+"/aktion?"+token,data=b'{"mode":"stop"}',
                            headers={"Content-Type":"application/json"},method="POST")
                with urlopen(req,timeout=4) as response:
                    self.assertEqual(response.status,200)
            finally:
                refs["server"].shutdown()
                thread.join(timeout=6)
                self.assertFalse(thread.is_alive())


class DialogOhneTk(unittest.TestCase):
    def test_kde_ordnerauswahl_liefert_validierten_pfad(self):
        with tempfile.TemporaryDirectory() as tmp, \
             patch.dict(os.environ, {"DISPLAY": ":0"}), \
             patch("videozoom.webui.shutil.which", side_effect=lambda n: "/usr/bin/kdialog" if n=="kdialog" else None), \
             patch("videozoom.webui.subprocess.run", return_value=CompletedProcess([], 0, tmp+"\n")) as run:
            self.assertEqual(ordner_waehlen("downloads",tmp),tmp)
            self.assertEqual(run.call_args.args[0][0],"kdialog")
            self.assertFalse(run.call_args.kwargs.get("shell", False))

    def test_abbruch_bewahrt_auswahl(self):
        with tempfile.TemporaryDirectory() as tmp, \
             patch.dict(os.environ, {"DISPLAY": ":0"}), \
             patch("videozoom.webui.shutil.which", return_value="/usr/bin/kdialog"), \
             patch("videozoom.webui.subprocess.run", return_value=CompletedProcess([], 1, "")):
            self.assertIsNone(ordner_waehlen("arbeitsordner",tmp))

    def test_unsicherer_symlink_wird_nicht_uebernommen(self):
        with tempfile.TemporaryDirectory() as tmp:
            ziel=Path(tmp)/"ordner"
            ziel.mkdir()
            link=Path(tmp)/"verknuepft"
            link.symlink_to(ziel)
            with patch.dict(os.environ, {"DISPLAY": ":0"}), \
                 patch("videozoom.webui.shutil.which", return_value="/usr/bin/kdialog"), \
                 patch("videozoom.webui.subprocess.run", return_value=CompletedProcess([], 0, str(link)+"\n")):
                with self.assertRaisesRegex(ValueError,"unsicher"):
                    ordner_waehlen("downloads",tmp)

    def test_ungueltiger_dialogbereich_und_fehler_ohne_desktop(self):
        with self.assertRaises(ValueError):
            ordner_waehlen("systembefehl","/")
        with patch.dict(os.environ,{},clear=True):
            with self.assertRaisesRegex(RuntimeError,"Kein grafischer Desktop"):
                ordner_waehlen("downloads","/")


if __name__=="__main__":
    unittest.main()
