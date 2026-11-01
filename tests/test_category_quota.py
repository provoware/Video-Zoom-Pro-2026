"""Negativvertraege: widerspruechliche Herkunftsmarker und echte Quotenwerte."""
from __future__ import annotations

import os
from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import patch

from tests.fixtures.generieren import png
from videozoom.core import Workflow, kategorie
from videozoom.diagnose import pruefen, scope_verfuegbar


class KategorieUndBegrenzung(unittest.TestCase):
    def test_eindeutige_chatgpt_provoware_kategorie(self):
        self.assertEqual(kategorie("ChatGPT_PROVOWARE_Cover.png"), "PROVOWARE")
        self.assertEqual(kategorie("chatgpt_thema_skizze.webp"), "THEMA")
        self.assertEqual(kategorie("ChatGPT_Coding_Projekt.png"), "CODING")

    def test_widerspruch_provoware_thema_wird_nicht_geraten(self):
        self.assertIsNone(kategorie("ChatGPT_PROVOWARE_THEMa.png"))
        self.assertIsNone(kategorie("ChatGPT_CODING_THEMA.png"))
        self.assertIsNone(kategorie("ChatGPT_CODING_PROVOWARE.png"))
        self.assertIsNone(kategorie("ChatGPT_CODING_PROVOWARE_THEMA.png"))

    def test_hintergrund_ohne_chatgpt_ist_keine_automatische_kategorie(self):
        self.assertIsNone(kategorie("PROVOWARE_Cover.png"))
        self.assertIsNone(kategorie("ChatGPT_ohne_zuordnung.jpg"))

    def test_konfliktbild_bleibt_im_downloads_verzeichnis(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            downloads=root/"Downloads"
            downloads.mkdir()
            source=png(downloads/"ChatGPT_PROVOWARE_THEMA.png")
            old=time.time()-30
            os.utime(source,(old,old))
            dienst=Workflow({"downloads":str(downloads),
                              "arbeitsordner":str(root/"Arbeit")},testmodus=True)
            self.assertEqual(dienst.bilder_einsortieren(),(0,1))
            self.assertTrue(source.exists())
            self.assertFalse(list((root/"Arbeit"/"BILDER"/"PROVOWARE").iterdir()))

    def test_quota_test_nutzt_abweichende_einstellungen(self):
        cfg={"cpu_prozent":20, "ram_mb":512}
        with patch("videozoom.diagnose.shutil.which",return_value="/usr/bin/systemd-run"), \
             patch("videozoom.core.os.sched_getaffinity",return_value={0,1,2,3},create=True), \
             patch("videozoom.diagnose.run",return_value=(True,"")) as run:
            self.assertTrue(scope_verfuegbar(cfg))
            args=run.call_args.args[0]
            self.assertIn("CPUQuota=80%",args)
            self.assertIn("MemoryMax=512M",args)

    def test_stapel_prueft_seine_eigenen_limits(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            (root/"Downloads").mkdir()
            dienst=Workflow({"downloads":str(root/"Downloads"),
                              "arbeitsordner":str(root/"Arbeit"),
                              "cpu_prozent":20,"ram_mb":512})
            dienst.zustand["auftraege"]["a"]={"status":"BEREIT","titel":"Test",
                "dateien":[],"laenge":4.0,"versuche":0}
            with patch("videozoom.diagnose.scope_verfuegbar",return_value=False) as scope:
                self.assertEqual(dienst.stapel(),(0,1))
                scope.assert_called_once_with(dienst.cfg)

    def test_diagnose_ruft_scope_mit_benutzerwerten_auf(self):
        cfg={"cpu_prozent":15,"ram_mb":1024}
        with patch("videozoom.diagnose.scope_verfuegbar",return_value=True) as scope, \
             patch("videozoom.diagnose.shutil.which",return_value=None):
            checks=pruefen(real_scope=True,cfg=cfg)
        scope.assert_called_once_with(cfg)
        self.assertIn("Begrenzung",[c["name"] for c in checks["pruefungen"]])


if __name__=="__main__":
    unittest.main()
