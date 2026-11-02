# 🎬 PROVOWARE Video Zoom Pro 2026

![Entwicklung](https://img.shields.io/badge/Stand-Entwicklung-orange) ![Offline](https://img.shields.io/badge/Betrieb-lokal-brightgreen) ![Tk-frei](https://img.shields.io/badge/Oberfl%C3%A4che-ohne_Tk-blue)

Eigenständige Linux-Anwendung zur automatischen Erstellung von Musikvideos aus WAV-Dateien und Bildern. **VideoBatch bleibt ein anderes Projekt.** Die Oberfläche läuft ausschließlich lokal im Browser, ohne Tk und ohne Cloud.

## Aktueller Entwicklungsstand (02.11.2026)

Die Folgepakete #34 → #35 → #36 → #37 wurden geordnet mit jeweils erfolgreicher Hauptzweigprüfung integriert. Anschließend folgten sichere Einstellungsrücksetzung/Farbwahl (#38), echte Tastatur-/Kontrastprüfung (#39) und der Nur-Lese-Schutz für zweite Fenster (#40).

Der geprüfte Produktstand umfasst **151 Python-/Medientests, 13 ausgeführte Chromium-Verträge, 20 echte Tastatur-/Kontrastfälle und 20 Layoutfälle**. Prüfnachweise, Quell-HEAD und GitHub-Test-Merge bleiben in [STATUS](docs/STATUS.md) getrennt. Die [führende TODO](docs/TODO.md) hält die verbleibenden Pixel-/Zielsystem- und Architektur-/Sicherheitsaufgaben offen. Kein Stable-Release.

## 🧭 Funktionsgrafiken und Designreferenz

Die zwei Abläufe sind als **versionierte, direkt in GitHub sichtbare Diagramme** dokumentiert:

- [🔄 Einfacher Ablauf: vom WAV bis zum geprüften Video](docs/diagramme/01_einfacher_prozess.md).
- [🔧 Technischer Funktionsfluss: Python, FFmpeg, Parameter und Fehlerwege](docs/diagramme/02_funktionsfluss_technik.md).
- [🎨 DateiFinder-Designanalyse und Transfermatrix](docs/DESIGN_TRANSFER_DATEIFINDER.md).

Der aktuelle Bildschirm hat vier Bereiche: **Songs vorbereiten, Stapelverarbeitung, Diagnose und Protokoll**. Die DateiFinder-Referenz dient für klare Farben, Arbeitsbereiche, Status, Fokusringe und reproduzierbare Bildprüfungen. **Nicht** kopiert werden DateiFinder-Technik (Tauri/Rust), Mini-Schriften oder die feste Seitenleiste. Ziel bleibt eine gut lesbare Tk-freie Oberfläche ohne horizontales Scrollen, auch bei **800×600/200 %**. Der eigentliche Dateifluss und seine Sicherheitsregeln bleiben unabhängig.

**Entwicklungsstand:** Die beiden Diagramme und die Designanalyse sind versioniert. Vier Farbschemata (Cyan, Violett, Grün, Orange) mit gespeicherter Auswahl, kompakter Kopf und Sprungnavigation sind implementiert (PRs #23/#25). Der isolierte Chromium-Gate prüft 20 Layoutfälle, Screenshots und auch abgeschnittenen Navigationstext (PRs #24/#25). Die Bilder verwenden eine **CSS-Zoomsimulation**; echter KDE-/Browser-Zoom, Tastaturbedienung und die menschliche Sichtprüfung bleiben ausdrücklich offen. Weitergehende Bedien- und Pixelreferenz-Verbesserungen stehen in der TODO; die echte Kubuntu-Endabnahme ist der letzte Schritt.

### Farben und Bedienung

Über „**Farbschema**“ im Kopf lässt sich zwischen vier kontrastreichen Varianten wechseln; über **Einstellungen speichern** wird die Wahl dauerhaft in der bestehenden lokalen Konfiguration gespeichert. Die Sprungknöpfe „Vorbereiten“, „Stapel“, „Diagnose“ und „Protokoll“ scrollen direkt zum jeweiligen Bereich. Die vier Arbeitsbereiche und alle Medienfunktionen bleiben unabhängig von der Farbauswahl.

**Automatischer Bildschirm-Vortest:** `python3 scripts/layout_check.py --ziel dist/ui-nachweis` benötigt lokal Chrome/Chromium **nur zur Entwicklung**, nicht im ausgelieferten Tool. Die Prüfergebnisse und Screenshots entstehen ohne echte WAVs/Benutzerdateien; GitHub legt sie als `videozoom-layout-nachweise` ab. Das ist keine persönliche Kubuntu-Abnahme.

## ✨ Moderne, übersichtliche Medienoberfläche

Fünf kompakte Statuskacheln zeigen die **tatsächlichen** Aufträge: bereit, auf Bilder wartend, Video läuft, archiviert und noch zu prüfen. Diese Zahlen stammen aus dem vorhandenen Auftragsjournal. Neben dem gewählten Videoformat stehen Bildgröße und typischer Verwendungszweck.

**Diagnose, Sensordaten und Protokolle** lassen sich über große, per Tastatur erreichbare Aufklappzeilen öffnen. Die drei vorhandenen Fortschrittsbalken zeigen zusätzlich ihre Prozentzahl als Text; der Kern entscheidet weiterhin, wann 100 % tatsächlich erreicht sind. Alle vier vorhandenen Farbschemata bleiben erhalten. Es gibt **keinen neuen Dienst und keine Internetverbindung**.

Die Gestaltungsentscheidung beruht auf einer [Recherche zu Shutter Encoder, HandBrake, Adobe Media Encoder, LosslessCut und CapCut](docs/DESIGN_RECHERCHE_MEDIEN_UI_2026-11-02.md). Nur die Bedienprinzipien wurden eigenständig umgesetzt; keine fremde Oberfläche oder Software übernommen.

**Status:** Die Erweiterungen sind über [PR #28](https://github.com/provoware/Video-Zoom-Pro-2026/pull/28) implementiert und in `main` integriert. Auf dem geprüften Entwicklungsstand bestanden 108 Python-/Medien-/Sicherheitstests und 20 Chromium-Layoutergebnisse. Der automatisierte Browser-Test misst Fenster und CSS-Vergrößerung, nicht den echten KDE-Browser-Zoom. Die abschließende Kubuntu-Sicht- und CPU-Abnahme bleibt gesperrt, bis der eingefrorene Releasekandidat bereitsteht.

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

**Noch keine Stable-Freigabe:** Die automatisierten Crash-/Wiederanlauf-/Stapeltests sind nachweisbar vorhanden. Die echte Desktopprüfung unter Kubuntu, reale Quotenmessung und Stromausfall-/Langzeittests auf dem Zielsystem bleiben zuletzt offen. Vor Produktivnutzung Dateien sichern und nur mit Testkopien probieren.

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

## Bedienung ohne Texteingabe – grafische Ordnerauswahl

Neben den Feldern für Downloads und Arbeitsordner gibt es eine Schaltfläche **„📁 Ordner wählen“**. Unter KDE wird ein vorhandenes `kdialog` verwendet, andernfalls `zenity`. Beide werden ausschließlich lokal und ohne Shell-Auswertung gestartet. Es wird **kein Tk** installiert oder geladen. Falls kein Desktop-Dialog vorhanden ist, bleibt die bisherige Eingabemöglichkeit erhalten; ein abgebrochener Dialog verändert nichts. Die Auswahl muss anschließend mit **Einstellungen speichern** bestätigt werden.

Vorbereitung und Stapel besitzen getrennte Fortschrittsbalken. Die Darstellung berücksichtigt Tastaturfokus und kleine Fenster; die echte visuelle Prüfung auf Kubuntu bei 800×600 und hoher Schriftgröße bleibt offen.

**Hinweis:** Die Ordnerauswahl ist keine Bestätigung zum Löschen oder Archivieren. Die vorhandenen Datenintegritätsregeln bleiben unverändert.

## Zuverlässige Fortschrittsanzeigen

Vorbereitung, Stapel und das aktuelle Video werden getrennt angezeigt. Das Video zeigt erst nach erfolgreicher Quellarchivierung 100 %, der Stapel nur bei vollständig archivierten vorbereiteten Aufträgen. Fehlgeschlagene oder pausierte Vorgänge bekommen keinen künstlichen Abschluss. Die technische Qualität der Anzeige ist automatisiert geprüft; die visuelle Gesamt-Kubuntu-Abnahme folgt erst am fertigen Kandidaten.

## Prüffähiges Linux-Entwicklungspaket (noch kein Stable-Release)

Ein ZIP mit Startskript, Anleitung und den benötigten Programmdateien erstellen:

```bash
python3 scripts/build_bundle.py
```

Das ZIP wird unter `dist/` abgelegt und besitzt ein internes `MANIFEST.json` mit SHA-256-Prüfsummen. Bestehende ZIPs werden nie überschrieben. **Die Stable-Freigabe ist ausdrücklich gesperrt**, bis die Lizenzentscheidung und die abschließende Kubuntu-Abnahme vorliegen. ZIP-Erzeugung und Dateiverifikation sind automatisiert geprüft; ein endgültiger Zielsystem-Installationstest folgt zuletzt.

## ⏱️ Zeitlimits und offene Qualitätsarbeiten

Die neue [verbindliche PROVOWARE-Zeitlimitregel](docs/PROVOWARE_TIMEOUT_STANDARD.md) schützt den Entwicklungsprozess vor endlosen Prüfungen. Im [20-Punkte-Qualitätsbericht](docs/QUALITY_AUDIT_2026-11-02.md) sind konkret nachgewiesene oder noch zu prüfende Schwachstellen der Start-, Browser- und Videologik priorisiert. **Die technische Runtime-Umsetzung der offenen Befunde ist noch nicht abgeschlossen.** Originalschutz und die letzte Kubuntu-Nutzer-Endabnahme bleiben verbindlich.

## Renderüberwachung (Issue #31)
Stumme FFmpeg-Prozesse blockieren die Stopptaste nicht mehr. Nach 120 Sekunden ohne steigende Medienzeit erscheint eine Warnung; nach 300 Sekunden ohne Medienfortschritt und nachweisbare CPU-Arbeit wird der eigene Renderprozess beendet. Aktive Berechnung hat keine pauschale Fünf-Minuten-Grenze. Teilvideo und Originale bleiben geschützt. Bewusster Stopp zählt nicht als technischer Fehlversuch. Entwicklungszweig `fix/issue-31-render-watchdog`; CI-/Zielsystemfreigabe getrennt prüfen.

## Start- und Verbindungsdiagnose
`--doctor` liefert bei fehlender Startbereitschaft Exitcode 1, bei bestätigter Startbereitschaft 0. Gespeicherte Auftragszahlen erscheinen beim Öffnen ohne schreibenden Programmstart. Beschädigte oder verknüpfte Journale bleiben unverändert und melden einen Fehler. Browserstatus: 10 s Zeitbudget, nächste Abfrage erst nach Abschluss; bei Ausfall steht „Anzeige veraltet“. Manuelle Ordnerwahl hat separat 125 s, ausführliche Systemdiagnose 60 s. Abbruch eines Browseraufrufs beendet keinen gespeicherten Auftrag.

## WAV-Downloadprüfung
Vor der Vorbereitung wird zusätzlich zum Dateialter geprüft, ob die im WAV-Kopf angegebenen RIFF/RIFX/RF64-Blöcke vollständig vorhanden sind. Eine alte, aber abgeschnittene Datei wartet weiter und verbraucht keinen technischen Fehlversuch; nach vollständiger Kopie kann sie erneut vorbereitet werden. Originaldateien werden nicht repariert oder verändert. Grenze: Eine bereits komplett vorreservierte Datei mit formal gültigem Kopf ist ohne Abschlusssignal des Downloadprogramms nicht sicher von einem fertigen Download unterscheidbar; Ton-/Längenprüfung bleibt zusätzlich bestehen.

## Platzbedarf vor großen Schreibvorgängen
Vor dem Rendern wird ein konservativer Bedarf aus Bildgröße, Bildrate und Songlänge geschätzt: 1 Bit je Pixel und Bild plus AAC-Ton, 25 % Zuschlag und zweite MP4-Kopie für `faststart`, dazu Archivquellen und 256 MiB freie Reserve. Vor Archivierung wird der gesamte noch zu kopierende Umfang geprüft; vorhandene bestätigte Archive/Teilkopien werden berücksichtigt. Bei Platzmangel wartet der betroffene Auftrag ohne Verbrauch eines technischen Render-/Archivversuchs. Nach Freigabe von Speicher kann er fortgesetzt werden. Die Schätzung ist keine garantierte Obergrenze und reserviert keinen Platz gegen andere Programme.

## Verständliche Einrichtung und Diagnose
Die Vorbereitung zeigt die Einrichtungsfolge: Ordner wählen, speichern, System prüfen und fertige Medien vorbereiten. Die Systemprüfung kontrolliert Ordnerlage/Zugriff, FFmpeg-/FFprobe-Versionen, Filter/Kodierer und Ressourcenbegrenzung ohne neue Ordner oder Originaldateien zu schreiben. Offene Punkte nennen Ursache und nächste Handlung; vollständige technische Einzelheiten bleiben erreichbar. Solange kein bestätigter Fortschrittswert vorliegt, erscheint „Noch unbekannt“; echte 0 % bleiben als 0 % sichtbar.

## Einstellungen sicher ändern und zurücksetzen
Während der Verarbeitung kann das Farbschema über „Einstellungen speichern“ dauerhaft geändert werden. Medienparameter bleiben bis zum Ende des Auftrags gesperrt. Die Konfiguration des laufenden Renderprozesses wird nicht geändert.

Im Vorbereitungsbereich kann wahlweise nur das Farbschema, nur Format/Kategorie oder beides auf die Standardwerte zurückgesetzt werden. Vorher wird der exakte bisherige Einstellungsinhalt als eigene geschützte Sicherungsdatei gespeichert. „Letzte Rücksetzung zurücknehmen“ stellt nur die damals gewählten Werte wieder her, auch nach einem Neustart. Ordner, Medien, CPU-/RAM-Grenzen und später geänderte andere Einstellungen bleiben erhalten. Rücksetzen/Rücknahme sind bei laufender Verarbeitung gesperrt. Extern geänderte Einstellungen und beschädigte Sicherungen werden nicht still überschrieben.

## Tastatur- und Kontrastprüfung in der Entwicklung
Zusätzlich zur Layoutmatrix führt `python3 scripts/browser_bedienung.py --ziel dist/bedienung` im isolierten Chromium echte Tab- und Leertasten aus. Geprüft werden die natürliche Tabfolge aller erreichbaren Bedienelemente, aufklappbare Details, Textkontrast (mindestens 4,5:1), Fokuskontrast (mindestens 3:1) und deaktivierte/Hover-Zustände. Vier Farbschemata und fünf Größen-/CSS-Zoomkombinationen ergeben 20 Fälle. Standardbibliothek und vorhandenes Chromium reichen; kein neues Produktpaket. Der JSON-Bericht enthält die CI-SHA. Diese Prüfung ersetzt keine freigegebene Pixelreferenz, keine komplette Prüfung von Verlaufspixeln oder Farbsehschwächen und keinen echten Kubuntu-Browser-Zoom.

## Zweites Fenster desselben Arbeitsordners
Wenn ein anderes Fenster bereits verarbeitet, zeigt diese Oberfläche „Arbeitet im anderen Fenster“. Sie liest den aktuellen Journalstand; fremde Fortschrittswerte werden nicht erfunden. Starten, Stoppen, Einstellungsänderung und Rücksetzen werden hier abgewiesen: Den aktiven Auftrag im ursprünglichen Fenster steuern. Die bestehende Kern-Sperre wird nur geprüft, niemals wegen ihres Alters gelöscht. Sobald sie freigegeben ist, erkennt die nächste Statusabfrage den freien Ordner. Unlesbare oder verknüpfte Sperrpfade melden einen Fehler und erlauben keine Verarbeitung.
