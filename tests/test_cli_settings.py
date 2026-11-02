"""Startdiagnose muss dieselben Benutzereinstellungen wie der echte Renderpfad nutzen."""
from __future__ import annotations

from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from videozoom import __main__


class DiagnoseEinstellungen(unittest.TestCase):
    def test_doctor_laesst_benutzerwerte_nicht_unbeachtet(self):
        with tempfile.TemporaryDirectory() as folder:
            config=Path(folder)/"settings.json"
            config.write_text(json.dumps({
                "cpu_prozent": 17, "ram_mb": 768, "format": "HOCH"
            }), encoding="utf-8")
            output=io.StringIO()
            with patch.object(__main__, "SETTINGS", config), \
                 patch.object(__main__, "pruefen",
                              return_value={"startbereit":True,"pruefungen":[]}) as check, \
                 redirect_stdout(output):
                result=__main__.main(["--doctor"])
            self.assertEqual(result, 0)
            sent=check.call_args.kwargs["cfg"]
            self.assertEqual(sent["cpu_prozent"],17)
            self.assertEqual(sent["ram_mb"],768)
            self.assertEqual(sent["format"],"HOCH")
            self.assertTrue(json.loads(output.getvalue())["startbereit"])

    def test_doctor_beachtet_cli_format_uerschreibung(self):
        with tempfile.TemporaryDirectory() as folder:
            config=Path(folder)/"settings.json"
            config.write_text(json.dumps({"format":"BREI"}),encoding="utf-8")
            with patch.object(__main__, "SETTINGS", config), \
                 patch.object(__main__, "pruefen",
                              return_value={"startbereit":True}) as check, \
                 redirect_stdout(io.StringIO()):
                __main__.main(["--doctor","--format","QUAD"])
            self.assertEqual(check.call_args.kwargs["cfg"]["format"],"QUAD")

    def test_doctor_fehlende_voraussetzungen_sind_kein_erfolg(self):
        for bericht in ({"startbereit":False,"pruefungen":[]}, {}):
            with self.subTest(bericht=bericht), tempfile.TemporaryDirectory() as tmp:
                with patch.object(__main__, "SETTINGS", Path(tmp)/"missing.json"), \
                     patch.object(__main__, "pruefen", return_value=bericht), \
                     redirect_stdout(io.StringIO()):
                    self.assertEqual(__main__.main(["--doctor"]),1)


if __name__=="__main__":
    unittest.main()
