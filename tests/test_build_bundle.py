"""Paketabnahme ohne GUI: unveränderliches ZIP mit Prüfsummen und Startskript."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import build_bundle


class Paketvertrag(unittest.TestCase):
    def test_entwicklungskandidat_verifiziert_ohne_persoenliche_dateien(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "candidate.zip"
            result = build_bundle.bundle(target)
            self.assertFalse(result["stable"])
            self.assertEqual(result["sha256"], hashlib.sha256(target.read_bytes()).hexdigest())
            with zipfile.ZipFile(target) as z:
                names = z.namelist()
                self.assertEqual(len(names), len(set(names)))
                self.assertTrue(all(name.startswith("Video-Zoom-Pro-2026/") for name in names))
                self.assertFalse(any("/tests/" in n or "PROTOKOLLE" in n
                                     or "__pycache__" in n or ".venv" in n for n in names))
                self.assertIn("Video-Zoom-Pro-2026/STARTEN.sh", names)
                self.assertIn("Video-Zoom-Pro-2026/videozoom/core.py", names)
                start = z.getinfo("Video-Zoom-Pro-2026/STARTEN.sh")
                self.assertTrue(((start.external_attr >> 16) & 0o111) != 0)
                manifest = json.loads(z.read("Video-Zoom-Pro-2026/MANIFEST.json"))
                self.assertFalse(manifest["stable"])
                self.assertEqual(manifest["kanal"], "ENTWICKLUNGSKANDIDAT")
                self.assertEqual(len(manifest["dateien"]), len(names) - 1)
                for rel, entry in manifest["dateien"].items():
                    content = z.read("Video-Zoom-Pro-2026/" + rel)
                    self.assertEqual(hashlib.sha256(content).hexdigest(), entry["sha256"])

    def test_gleiche_quellen_erzeugen_identische_zip_bytes(self):
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder)
            build_bundle.bundle(p / "a.zip")
            build_bundle.bundle(p / "b.zip")
            self.assertEqual((p / "a.zip").read_bytes(), (p / "b.zip").read_bytes())

    def test_niemals_vorhandenes_paket_ueberschreiben(self):
        with tempfile.TemporaryDirectory() as folder:
            file = Path(folder) / "existing.zip"
            file.write_bytes(b"NICHT VERAENDERN")
            with self.assertRaises(FileExistsError):
                build_bundle.bundle(file)
            self.assertEqual(file.read_bytes(), b"NICHT VERAENDERN")

    def test_manifest_weder_stable_noch_fremde_dateien(self):
        data = {"STARTEN.sh": b"echo OK"}
        manifest = json.loads(build_bundle.manifest(data))
        self.assertEqual(set(manifest["dateien"]), {"STARTEN.sh"})
        self.assertFalse(manifest["stable"])
        self.assertIn("Kubuntu", manifest["hinweis"])


if __name__ == "__main__":
    unittest.main()
