# 🎬 PROVOWARE Video Zoom Pro 2026

![Entwicklung](https://img.shields.io/badge/Stand-Entwicklung-orange) ![Offline](https://img.shields.io/badge/Betrieb-lokal-brightgreen) ![Tk-frei](https://img.shields.io/badge/Oberfl%C3%A4che-ohne_Tk-blue)

Eigenständige Linux-Anwendung zur automatischen Erstellung von Musikvideos aus WAV-Dateien und Bildern. **VideoBatch bleibt ein anderes Projekt.** Die Oberfläche läuft ausschließlich lokal im Browser, ohne Tk und ohne Cloud.

## Einfacher Start

1. Repository als ZIP herunterladen und vollständig entpacken.
2. Im Ordner STARTEN.sh ausführen; alternativ im Terminal: bash STARTEN.sh.
3. Lokale Browseroberfläche öffnet sich. Downloads- und Arbeitsordner sowie Format auswählen.
4. WAV-Datei in Downloads ablegen, z. B. Mein Song_suno-com-123_20261101.wav.
5. Die Songvorbereitung erstellt EINGANG/mein-song/BILDER. Dort passende Bilder ablegen.
6. Songs vorbereiten oder Stapel starten wählen. Alternativ Automatik einschalten.

**Videoablauf:** Zuerst alle Bilder rückwärts mit kurzem Standbild ohne Zoom, anschließend vorwärts mit sanften Zoombewegungen und wechselnden Übergängen. Musik- und Videodauer werden abgeglichen.

**Nach Erfolg:** MP4 in FERTIG; verwendete WAV/Bilder erst nach Prüfung und gesicherter Archivkopie in VERWENDET mit _verwendet_ im Namen. Logs und Journal unter PROTOKOLLE.

## Fünf Formatcodes

| Code | Bildgröße | Typische Verwendung |
|---|---|---|
| HOCH | 1080 × 1920 | Shorts, TikTok, Reels |
| BREI | 1920 × 1080 | YouTube, Breitbild |
| QUAD | 1080 × 1080 | Quadrat |
| KLAS | 800 × 600 | klassisches 4:3 |
| 4K | 3840 × 2160 | hochaufgelöstes Breitbild |

ChatGPT ist bei Dateinamen nur ein Herkunftsmarker, die drei Kategorien sind CODING, PROVOWARE und THEMA. Bei unbekanntem Songbezug keine automatische Bildzuordnung.

## Diagnose und Sicherheit

Zum Nachsehen: bash STARTEN.sh --doctor. Nur vorbereiten: bash STARTEN.sh --vorbereiten. Nur Stapel: bash STARTEN.sh --stapel. Einmal: bash STARTEN.sh --einmal. Dauerüberwachung: bash STARTEN.sh --beobachten.

FFmpeg/FFprobe und funktionsfähiger systemd-Benutzerscope sind für Videoberechnung erforderlich. 30 % bezieht sich auf die zugängliche CPU-Kapazität; RAM wird getrennt begrenzt. Fehlt der Scope, werden Jobs vorbereitet, aber nicht unkontrolliert berechnet. Systempakete nur nach sicherer Simulation und ausdrücklicher Zustimmung installieren.

**Noch keine Stable-Freigabe:** Desktopprüfung unter Kubuntu, echte Quotenmessung und vollständige Absturztests stehen aus. Vor Produktivnutzung Dateien sichern und nur mit Testkopien probieren.

## Dokumentation und Tests

- AGENTS.md: verbindliche Entwicklungs- und Sicherheitsregeln.
- docs/ARCHITEKTUR.md: fachlicher Datenfluss.
- docs/ANFORDERUNGEN.md: vollständige Funktionen.
- docs/TODO.md: nach Priorität geordnete Aufgaben.
- docs/TESTPLAN.md: Testdateien und Negativtests.
- docs/SICHERHEIT.md: Abhängigkeiten und Grenzen.
- docs/STATUS.md: reale Nachweise und offene Risiken.

Testdateien erzeugen: python3 tests/fixtures/generieren.py.
Tests starten: python3 -m unittest discover -s tests -v.

Für das öffentliche Repository wurde bewusst noch keine zusätzliche Veröffentlichungslizenz festgelegt; diese Entscheidung steht aus.
