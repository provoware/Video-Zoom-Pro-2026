"""Offline-ZIP in frischem Tempverzeichnis ohne Nutzer-/Systemdaten testen."""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from build_bundle import bundle


class EntpackterStart(unittest.TestCase):
    def test_bash_start_und_doctor_aus_frischem_zip(self):
        with tempfile.TemporaryDirectory() as root:
            base=Path(root)
            package=base/"dev.zip"
            bundle(package)
            target=base/"entpackt"
            target.mkdir()
            with zipfile.ZipFile(package) as archive:
                for item in archive.infolist():
                    # Keine traversal-Eintraege und keine fremden Dateipfade.
                    member=Path(item.filename)
                    self.assertTrue(member.parts)
                    self.assertEqual(member.parts[0],"Video-Zoom-Pro-2026")
                    self.assertFalse(member.is_absolute())
                    self.assertNotIn("..",member.parts)
                archive.extractall(target)
            app=target/"Video-Zoom-Pro-2026"
            env=dict(os.environ)
            env["HOME"]=str(base/"user")
            env["XDG_CONFIG_HOME"]=str(base/"user"/".config")
            env.pop("PYTHONPATH",None)
            (base/"user").mkdir()
            for args in (["--help"],["--doctor"]):
                cmd=["bash",str(app/"STARTEN.sh"),*args]
                result=subprocess.run(cmd,env=env,cwd=base,capture_output=True,
                                      text=True,timeout=50,check=False)
                self.assertEqual(result.returncode,0,
                                 "Frisch entpackter Start fehlgeschlagen: "+result.stderr[-800:])
                if args==["--doctor"]:
                    raw=json.loads(result.stdout)
                    self.assertIn("pruefungen",raw)
                    self.assertIsInstance(raw["startbereit"],bool)
                else:
                    self.assertIn("--vorbereiten",result.stdout)
            self.assertFalse((app/"PROTOKOLLE").exists())
            self.assertFalse((app/"Downloads").exists())

    def test_entpacktes_zip_enthaelt_keine_ausfuehrbaren_tests(self):
        with tempfile.TemporaryDirectory() as root:
            output=Path(root)/"bundle.zip"
            bundle(output)
            with zipfile.ZipFile(output) as archive:
                names=archive.namelist()
                self.assertFalse(any("/tests/" in item for item in names))
                self.assertFalse(any(item.endswith(".pyc") for item in names))
                self.assertFalse(any("/.git/" in item for item in names))


if __name__=="__main__":
    unittest.main()
