"""Pruefung der deterministischen Offline-Layoutsonde."""
from __future__ import annotations

from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import layout_check


class BrowserFixture(unittest.TestCase):
    def test_vier_themes_und_vergroesserung_ohne_live_api(self):
        for theme in ("cyan", "violett", "gruen", "orange"):
            for zoom in (100, 125, 150, 200):
                with self.subTest(theme=theme, zoom=zoom):
                    content = layout_check.html_fixture(theme, zoom)
                    self.assertIn("layout-check", content)
                    self.assertIn(f'document.body.dataset.theme = "{theme}"', content)
                    self.assertIn("document.documentElement.style.zoom = " + str(zoom/100), content)
                    self.assertNotIn("setInterval(status", content)

    def test_ungueltiger_stil_wird_abgewiesen(self):
        with self.assertRaises(ValueError):
            layout_check.html_fixture("<script>", 100)
        with self.assertRaises(ValueError):
            layout_check.html_fixture("cyan", 999)

    def test_messung_erkennt_fehlende_ueberlaufprobleme(self):
        document = ('<output id="layout-check" hidden="">'
                    '{"horizontalScroll":false,"horizontalOverflows":[],'
                    '"controls":10,"viewport":{"width":800,"height":600}}'
                    '</output>')
        result = layout_check.auswertung(document)
        self.assertEqual(result["viewport"]["width"], 800)

    def test_horizontaler_ueberlauf_niemals_pass(self):
        for body in (
            '{"horizontalScroll":true,"horizontalOverflows":[],"controls":10}',
            '{"horizontalScroll":false,"horizontalOverflows":["Stop"],"controls":10}',
            '{"horizontalScroll":false,"horizontalOverflows":[],"controls":2}',
        ):
            with self.subTest(body=body), self.assertRaises(RuntimeError):
                layout_check.auswertung('<output id="layout-check">' + body + '</output>')

    def test_browser_nicht_verfuegbar_ist_keine_erfolgsmeldung(self):
        from unittest.mock import patch
        with patch.object(layout_check.shutil, "which", return_value=None):
            with self.assertRaisesRegex(RuntimeError, "NICHT bestanden"):
                layout_check.browser_finden()


if __name__ == "__main__":
    unittest.main()
