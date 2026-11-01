#!/usr/bin/env python3
"""Deterministische Browser-Layoutprüfung: kein Tk, Node oder Nutzerdaten."""
from __future__ import annotations

import argparse
import html as html_lib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from videozoom.webui import HTML


def browser_finden() -> str:
    for name in ("google-chrome", "chromium", "chromium-browser"):
        location = shutil.which(name)
        if location:
            return location
    raise RuntimeError("Kein Chromium/Chrome gefunden: visueller Prüflauf NICHT bestanden.")


def html_fixture(theme: str, zoom: int) -> str:
    if theme not in {"cyan", "violett", "gruen", "orange"}:
        raise ValueError("Unbekanntes Theme")
    if zoom not in (100, 125, 150, 200):
        raise ValueError("Unbekannte Vergrößerung")
    base = HTML.split("<script>", 1)[0]
    if not base.endswith("</div>\n"):
        raise RuntimeError("Oberfläche hat eine neue Struktur; Fixture aktualisieren.")
    # Der Screenshot enthält nur statisches HTML. Es werden KEINE lokalen
    # Web-API-Aufrufe oder Daten aus einem echten Songprojekt ausgeführt.
    fixture = r"""<script>
document.body.dataset.theme = __THEME__;
document.documentElement.style.zoom = __ZOOM__;
window.addEventListener('load', () => {
  const width = innerWidth;
  const elems = [...document.querySelectorAll(
    'button,input,select,.phase-nav a,#status')];
  const invalid = elems.filter(el => {
    const r = el.getBoundingClientRect();
    return r.width > 0 && (r.left < -1 || r.right > width + 1);
  }).map(el => (el.id || el.textContent || el.tagName).trim().slice(0, 65));
  const report = {
    theme: document.body.dataset.theme,
    zoom: __ZOOM_NUM__,
    viewport: {width: innerWidth, height: innerHeight},
    horizontalScroll: document.documentElement.scrollWidth > innerWidth + 1,
    horizontalOverflows: invalid,
    controls: elems.filter(el => el.tagName === 'BUTTON').length
  };
  const out = document.createElement('output');
  out.id = 'layout-check';
  out.hidden = true;
  out.textContent = JSON.stringify(report);
  document.body.appendChild(out);
});
</script></body></html>"""
    return (base + fixture.replace("__THEME__", json.dumps(theme))
            .replace("__ZOOM__", str(zoom / 100))
            .replace("__ZOOM_NUM__", str(zoom)))


def browser_aufruf(browser: str, url: str, profile: Path,
                   groesse: tuple[int, int], screenshot: Path | None = None) -> str:
    command = [
        browser, "--headless=new", "--no-sandbox", "--disable-gpu",
        "--disable-background-networking", "--disable-dev-shm-usage",
        "--no-first-run", "--disable-default-apps", "--no-default-browser-check",
        "--force-prefers-reduced-motion", f"--user-data-dir={profile}",
        f"--window-size={groesse[0]},{groesse[1]}",
        "--virtual-time-budget=700",
    ]
    command.append(f"--screenshot={screenshot}" if screenshot else "--dump-dom")
    command.append(url)
    finished = subprocess.run(command, capture_output=True, text=True,
                              check=False, timeout=35)
    if finished.returncode:
        raise RuntimeError("Browserprüfung fehlgeschlagen: " +
                           finished.stderr[-600:])
    return finished.stdout


def auswertung(dom: str) -> dict:
    found = re.search(r'<output[^>]*id="layout-check"[^>]*>(.*?)</output>', dom, re.S)
    if not found:
        raise RuntimeError("Browser hat keine Layoutmessung geliefert.")
    parsed = json.loads(html_lib.unescape(found.group(1)))
    if parsed["horizontalScroll"] or parsed["horizontalOverflows"]:
        raise RuntimeError("Unzulässiger horizontaler Überlauf: " +
                           json.dumps(parsed, ensure_ascii=False))
    if parsed["controls"] < 6:
        raise RuntimeError("Pflichtschaltflächen nicht sichtbar in der Testoberfläche.")
    return parsed


def pruefen(ziel: Path) -> dict:
    browser = browser_finden()
    ziel.mkdir(parents=True, exist_ok=True)
    messungen = []
    with tempfile.TemporaryDirectory(prefix="videozoom-visual-") as temp:
        root = Path(temp)
        for width, height, zoom in ((800, 600, 100), (800, 600, 200), (1280, 720, 100)):
            for theme in ("cyan", "violett", "gruen", "orange"):
                htmlfile = root / f"fixture_{width}_{height}_{zoom}_{theme}.html"
                htmlfile.write_text(html_fixture(theme, zoom), encoding="utf-8")
                url = htmlfile.as_uri()
                result = browser_aufruf(browser, url,
                                         root / f"profile_{width}_{zoom}_{theme}",
                                         (width, height))
                measured = auswertung(result)
                measured["angefordert"] = {"breite": width, "hoehe": height}
                messungen.append(measured)
                if theme == "cyan":
                    shot = ziel / f"videozoom_{width}x{height}_{zoom}prozent.png"
                    browser_aufruf(browser, url, root / f"shot_{width}_{zoom}",
                                   (width, height), screenshot=shot)
                    if not shot.is_file() or shot.stat().st_size < 1000:
                        raise RuntimeError("Screenshot wurde nicht erzeugt: " + str(shot))
    report = {"schema": 1, "browser": Path(browser).name,
              "pruefungen": len(messungen), "werte": messungen,
              "visuelle_nutzerabnahme": "OFFEN", "stable": False}
    (ziel / "layout_bericht.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Offline-Chromium-Layoutprüfung")
    parser.add_argument("--ziel", type=Path, default=Path("dist/ui-nachweis"))
    args = parser.parse_args()
    result = pruefen(args.ziel)
    print(json.dumps({"pruefungen": result["pruefungen"],
                      "visuelle_nutzerabnahme": result["visuelle_nutzerabnahme"],
                      "stable": False}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
