# DateiFinder → Video Zoom Pro: Design- und Transfervertrag

**Stand:** 01.11.2026 · **Quelle:** `provoware/PROVOWARE_DATEIFINDER`, `main` `9cc035240ece8a32ffd0b53774754e77ade6d422` · **Ziel:** `provoware/Video-Zoom-Pro-2026`, `main` `56162cc6a1b3e1e00d61c77c78518cd7e372a17d`.

**Zweck:** Das erprobte Erscheinungsbild und die Prüfkultur von DateiFinder gezielt auf das **eigenständige** Tk-freie Browser-Werkzeug übertragen. Keine direkte CSS-/Quellcodekopie, keine Tauri-/Rust-Abhängigkeit, keine Funktionsausweitung auf fremde Dateisuche.

## Beobachtete DateiFinder-Referenz

Die versionierte Referenz liegt dort unter `tests/visual/dateifinder.spec.ts-snapshots/dateifinder-768x512-chromium-linux.png`; die Quellstruktur ist `src/styles.css` und `index.html`.

- **Geometrie:** dunkel gerahmte 768×512-Ansicht, ca. 159 px schmale Navigation links, Inhaltskopf oben, Hauptfläche mit Ergebnis-/Detailbereich, Statusleiste unten.
- **Farbwirkung:** tiefes Blau/Schwarz, Cyan-Glühen und klare Panelgrenzen; alternativ Violett, Grün, Orange durch Akzentvariablen.
- **Bedienhierarchie:** eine dominierende Hauptaktion, sekundäre Aktionen deutlich ruhiger; aktiver Navigationspunkt und klare Leerzustände.
- **Qualität:** versionierte Screenshot-Referenz, Tastaturfokus, kleine Fenster, hohe Zoomstufen, reduzierte Bewegungen, textliche Meldungen ergänzen Farben.
- **Wichtige Einschränkung:** DateiFinder nutzt teils 10–13 px Schrift und ein sehr enges 768×512-Raster; diese Werte sind **nicht** auf Video Zoom Pro mit mindestens 18 px, großen Knöpfen und 200%-Zoom zu übertragen.

## Konfliktmatrix – was übernehmen, was nicht?

| DateiFinder-Muster | Video Zoom Pro | Entscheidung | Bedingung / Test |
|---|---|---|---|
| Design-Tokens für Farbe, Hintergrund, Rand, Erfolg, Warnung, Fehler | bestehende Dunkeloberfläche | **Übernehmen** | neue eigene Tokens, WCAG-AA-Kontrast, kein CSS-Import |
| Cyan/Violett/Grün/Orange | bisher Blau | **Übernehmen** | vier Themen als nachvollziehbare Auswahl; Einstellungen persistent, Standard Cyan |
| Kontrast/Fokus/Status immer mit Text | vorhandene Basis vorhanden | **Verbessern** | Focus-visible, Tastatur, ARIA, Status nicht nur farbig |
| Kopfzeile mit zentralem Status und kompaktem Bedienzugang | derzeit Titel+Status | **Übernehmen, angepasst** | lesbare Zeilenumbrüche bei 800×600/200% |
| Feste Seitenleiste 159 px | 4 Karten / 2 Workflows | **Nicht 1:1** | stattdessen responsive Phasennavigation oder Sprunganker, kein horizontaler Scroll |
| Zweispaltige Aufgaben- und Detailfläche | Songvorbereitung/Batch | **Angepasst übernehmen** | 2 Spalten ab ausreichender Breite, darunter eine Spalte |
| Erklärende Leerzustände | leere Auftragsprotokolle | **Übernehmen** | nächster sinnvoller Klick als verständlicher Text |
| Kompakte Ergebnislisten/virtuelle Suche | Aufträge/Logs | **Nicht übernehmen** | nur begrenzte Protokollhöhe und scrollbar; keine Such-/Rust-Architektur |
| Vier Themes + Zoomregeln | Chrome-Browser lokal | **Gezielt** | keine Übernahme von Tauri-Fensterknöpfen; Browser-Zoom respektieren |
| Referenzscreenshots/Negativtests | bisher Python-Unittests | **Übernehmen als Gate** | 800×600 bei 100/125/150/200 %, 1280×720, je Theme |
| Neonanimation | Renderprozess mit Fortschritt | **Optional, zurückhaltend** | `prefers-reduced-motion` und keine blinkende Warnung |
| Node.js/Tauri/Rust/tauri capabilities | Python Standardbibliothek + FFmpeg | **Nicht übernehmen** | keine neue Laufzeitabhängigkeit |
| DateiFinder-Schnellspeicher, Suche, Dateifilter | WAV/Bilder/MP4-Produktion | **Nicht übernehmen** | andere Produktaufgabe; keinen zweiten Kern schaffen |

## Verbindlicher Oberflächenplan (kein ungeprüfter Großumbau)

**D1 – Design-Basis:** eigene `--color-*`-Tokens und 4 Themes mit hohem Kontrast, sichtbarer Tastaturfokus, textlicher Status. Einträge ausschließlich mit dokumentiertem Nutzen.

**D2 – Phasenführung:** dauerhaft unterscheidbar: „Songs vorbereiten“ (Quellen/Zuordnung) und „Stapel“ (Berechnung/Archivierung). Die Diagnose und das Protokoll bleiben eigene, erreichbare Details. Sicherheitskritische Stopptasten bleiben deutlich, aber nicht mit Hauptaktionen verwechselt.

**D3 – Kleines Fenster & Zoom:** 800×600/100–200 %: keine horizontale Scrollleiste, kein verdeckter Start-/Stoppknopf, Eingabefelder dürfen umbrechen; Panelbereiche vertikal scrollbar, niemals starr abgeschnitten. Große Schaltflächen (min. 44 px), lesbare Schrift.

**D4 – Reale, korrekte Anzeigen:** drei getrennte Prozentwerte; 100 % erst nach bestätigter Archivierung, unbekannter Fortschritt ohne erfundene Zahl. Pausen, Fehler und Folgeaktionen verständlich.

**D5 – Prüfsystem:** deterministischer Browser-Referenzzustand, feste Daten/Viewport/Schrift/Theme, Screenshots und strukturierte Prüfungen. Referenz nur nach begründeter Designänderung aktualisieren; für CSS keine Abhängigkeit von GitHub-Wärme oder realen Downloads. Automatische Layoutregression = Entwicklungsprüfung; **abschließende echte Kubuntu-Prüfung bleibt der letzte Schritt.**

## Entwicklungsdisziplin und Nachweise

- Vor Änderung: main-HEAD, laufende PRs, `docs/TODO.md`, betroffene UI-Schnittstellen und Referenzansichten prüfen.
- Ein Hauptziel je Patch; neue Farbe/Navigation niemals zusammen mit Rendering/Archiv mischen.
- Kein blindes Kopieren aus DateiFinder. DateiFinder-CSS/Icons, Rust und Tauri-Ports werden nicht importiert. Rechtliche Lizenzentscheidung bleibt offen.
- Pro UI-Änderung: HTML/CSS/JS auf Auswirkungen gegen lokale HTTP-API, Tokensicherheit, Fokus, 800×600/200% und 4 Themes untersuchen.
- Vergleiche zuerst Positionen, Größen, Abstände, Schrift, Farben, Ränder; bei Änderungen aktuelle Screenshots dokumentieren.
- Keine „grüne“ Visual-Prüfung ohne reproduzierbaren Browser-Screenshot zum selben Commit.
- Vor Release: vollständige Python-Regression, FFmpeg-Testmedien, ZIP/Starttest, Quotenvertrag und **erst ganz zuletzt** Kubuntu-Endabnahme.

## Übertragungsreihenfolge

1. **Versionierte Funktionen & Designvertrag** – diese Datei und zwei Funktionsdiagramme.
2. **Kleiner UI-Patch** – Farbtokens, sichtbare Auswahl, besserer Kopf und Textstatus; API-/Layouttests.
3. **Weitere UI-Pakete** – Phasensprünge, optionale einklappbare Diagnose, visualisierte Auftragsliste; jeweils geprüft, keine Änderung der Medienlogik.
4. **Screenshot-Vertrag** – unveränderte Referenz für 800×600/200 % und Desktop, dokumentierte Bildprüfungen.
5. **Danach** verbliebene Rechte-/Lizenzentscheidung und Releasekandidat, **zuletzt** Kubuntu.

### Gesonderte Beobachtung (kein unbestätigter Pass)

Die bisherige Oberflächendarstellung aus dem Quellcode zeigt bei 800 px Breite zwei hohe Karten plus Diagnose/Protokoll unterhalb. Bedienbar per vertikalem Scrollen, aber wenig Übersicht beim Wechseln zwischen Phasen; deswegen sind kompakte Kopfzeile, Sprunganker und Log-Detailansichten zuerst nutzbringend. Genau dies muss nach der Änderung im Browser geprüft werden.
