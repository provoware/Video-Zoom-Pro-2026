"""Echte localhost-HTTP-Prüfungen für den Tk-freien Browserzugriff."""
from __future__ import annotations
import json
from pathlib import Path
import sys
import tempfile
import threading
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from videozoom.core import konfiguration
from videozoom.webui import starten


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
                req=Request(root+"/aktion?"+token,data=b'{"mode":"stop"}',
                            headers={"Content-Type":"application/json"},method="POST")
                with urlopen(req,timeout=4) as response:
                    self.assertEqual(response.status,200)
            finally:
                refs["server"].shutdown()
                thread.join(timeout=6)
                self.assertFalse(thread.is_alive())


if __name__=="__main__":
    unittest.main()
