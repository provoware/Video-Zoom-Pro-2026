"""DateiFinder-inspirierte, aber eigenstaendige UI-Themes und Navigation."""
from __future__ import annotations

from html.parser import HTMLParser
import json
from pathlib import Path
import tempfile
import unittest

from videozoom.core import konfiguration, konfigurieren
from videozoom.webui import HTML, Bedienung


class Elemente(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids=set()
        self.anchors=[]
        self.select_ids=[]
    def handle_starttag(self, tag, attributes):
        attrs=dict(attributes)
        if "id" in attrs:
            self.ids.add(attrs["id"])
        if tag=="a":
            self.anchors.append(attrs.get("href", ""))
        if tag=="select":
            self.select_ids.append(attrs.get("id"))


class OberflaechenVertrag(unittest.TestCase):
    def test_vier_themes_und_default_festgelegt(self):
        self.assertEqual(konfiguration()["theme"],"cyan")
        for theme in ("cyan","violett","gruen","orange"):
            self.assertEqual(konfigurieren({"theme":theme})["theme"],theme)

    def test_unbekanntes_theme_wird_abweisen(self):
        for value in ("",None, "javascript:alert(1)", "<script>", "blau"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                konfigurieren({"theme":value})

    def test_theme_bleibt_in_einstellungen_erhalten(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            (root/"Downloads").mkdir()
            cfg=konfigurieren({"downloads":str(root/"Downloads"),
                              "arbeitsordner":str(root/"Arbeit")})
            settings=root/"user"/"settings.json"
            ui=Bedienung(cfg,settings)
            ui.einstellungen({"theme":"gruen"})
            self.assertEqual(json.loads(settings.read_text())["theme"],"gruen")
            self.assertEqual(ui.status()["cfg"]["theme"],"gruen")

    def test_navigationsziele_und_status_erreichbar(self):
        page=Elemente()
        page.feed(HTML)
        for target in ("vorbereitung","stapel-karte","diagnose-karte",
                       "protokoll-karte","status","hinweis","theme",
                       "vorbereitungsbar","stapelbar","videobar"):
            self.assertIn(target,page.ids)
        for href in ("#vorbereitung","#stapel-karte","#diagnose-karte",
                     "#protokoll-karte"):
            self.assertIn(href,page.anchors)
        self.assertIn("theme",page.select_ids)
        self.assertIn('aria-label="Arbeitsbereiche"',HTML)
        self.assertIn('role="alert"',HTML)

    def test_grosse_bedienung_und_responsive_karten(self):
        for key in ('min-height:46px','@media(max-width:520px)',
                    'grid-template-columns:repeat(auto-fit',
                    'body[data-theme="violett"]','body[data-theme="gruen"]',
                    'body[data-theme="orange"]',
                    "prefers-reduced-motion","overflow-x:hidden"):
            self.assertIn(key,HTML)

    def test_keine_fremde_runtimes_oder_cloud(self):
        for forbidden in ("import tkinter", "import tauri", "src-tauri",
                          "https://cdn.", "http://cdn."):
            self.assertNotIn(forbidden,HTML)


if __name__=="__main__":
    unittest.main()
