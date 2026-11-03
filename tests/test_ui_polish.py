"""UI-Aufwertung ohne Einfluss auf WAV, FFmpeg, Archive oder Benutzerdaten."""
from __future__ import annotations
from html.parser import HTMLParser
import re
import unittest

from videozoom.webui import HTML


class OberflaechenElemente(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.details = []
        self.summary_count = 0
        self.outputs = []
        self.labels = set()
    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if attrs.get("id"):
            self.ids.add(attrs["id"])
        if tag == "details":
            self.details.append(attrs)
        elif tag == "summary":
            self.summary_count += 1
        elif tag == "output":
            self.outputs.append(attrs)
        elif tag == "label" and attrs.get("for"):
            self.labels.add(attrs["for"])


class BedienungUndStatus(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.page = OberflaechenElemente()
        cls.page.feed(HTML)

    def test_auftragsuebersicht_enthaelt_echte_backend_zustaende(self):
        for key in ("kpi-bereit", "kpi-wartet", "kpi-laeuft",
                    "kpi-fertig", "kpi-pruefen"):
            self.assertIn(key, self.page.ids)
        for state in ("BEREIT", "WARTET", "LAEUFT", "ARCHIVIERT",
                      "PRUEFEN", "ARCHIV_WARTET"):
            self.assertIn("wert('" + state + "')", HTML)
        self.assertIn("auftragszahlen(r.jobs)", HTML)
        self.assertIn("textContent=wert(", HTML)
        # Die Zahlen kommen aus den echten vorhandenen Statusinformationen;
        # keine neuen API-Endpunkte und keine Ausgabe scheinbar fertiger Jobs.
        self.assertNotIn("innerHTML=r.jobs", HTML)

    def test_alle_fuenf_formatcodes_anzeigen(self):
        self.assertIn('onchange="formatHinweis()"', HTML)
        self.assertIn("formatHinweis();", HTML)
        for value in ("BREI", "HOCH", "QUAD", "KLAS", "'4K'"):
            self.assertIn(value + ":", HTML)

    def test_technische_details_ueber_native_elemente_zugaenglich(self):
        self.assertEqual(len(self.page.details), 5)
        self.assertEqual(self.page.summary_count, 5)
        self.assertTrue(all("open" not in d for d in self.page.details if d.get("id") != "einrichtung"))
        for element in ("diagnose", "sensoren", "jobs", "log"):
            self.assertIn(element, self.page.ids)

    def test_fortschritt_text_und_balken_konsistent(self):
        for p, output in (("vorbereitungsbar", "vorbereitung-wert"),
                          ("stapelbar", "stapel-wert"),
                          ("videobar", "video-wert")):
            self.assertIn(p, self.page.labels)
            self.assertIn(output, self.page.ids)
            self.assertIn("fortschrittAnzeigen('"+p+"','"+output+"'", HTML)
        self.assertIn("Number.isFinite(n)", HTML)
        self.assertIn("Math.min(100,Math.max(0,", HTML)

    def test_ausreichende_tastenflaechen_und_fokus(self):
        self.assertIn("min-height:46px", HTML)
        self.assertIn("min-height:44px", HTML)
        self.assertIn(":focus-visible", HTML)
        self.assertIn("prefers-reduced-motion:reduce", HTML)

    def test_keine_cloud_oder_zusaetzliche_laufzeit(self):
        for unsafe in ("import tkinter", "src-tauri", "https://cdn.",
                       "npm install", "<script src=", "new Function(", "eval("):
            self.assertNotIn(unsafe, HTML)
        self.assertIn("textContent", HTML)


if __name__ == "__main__":
    unittest.main()
