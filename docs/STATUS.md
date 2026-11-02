# Status und Wiederaufnahme – 02.11.2026

## Integration vollständig durchgeführt
| Paket | Hauptzweig-Commit | Hauptzweigprüfung |
|---|---|---|
| #34 Strategie | d470ea00d239fc1d57031fcd43808d1ae0e6e353 | #41377347113 erfolgreich |
| #35 WAV | 60b24d9806f346f15f3f6bd645cde1cad7fb5589 | #41377490494 erfolgreich |
| #36 Speicher | 8fca030174d4a00bcf2b4dca7e673a8b93494951 | #41377620159 erfolgreich |
| #37 Einrichtung | e544b711794080be5300158dd6608b964c5b9bea | #41377743071 erfolgreich |
| #38 sichere Bedienwerte | 45ae369e04003ff0e8cef27d87ec7e6123da5835 | #41378432136 erfolgreich |
| #39 echte Tastatur/Kontrast | 83545bc26496a6d723fc4ea5eab723f9a1df1caf | #41378950862 erfolgreich |
| #40 zweites Fenster | 2eec90242b9477c2f41e0af690e0a35f5e287620 | #41379321415 erfolgreich |

Alle Übernahmen regulär, ohne Force-Push und ohne Abschwächung einer Pflichtprüfung. Originalauftrag #34 → #35 → #36 → #37 eingehalten, danach Bedienung implementiert.

## Exakte Nachweise des letzten Produktstands
- Quell-HEAD #40: `f82e377f23c5d7991bc1af066e44707681aa06a6`, lokal 151/151 ohne Überspringer; alle 67 versionierten lokalen Dateien per Git-Blob-Fingerabdruck mit veröffentlichtem Quellbaum identisch.
- PR-CI #41379032590 erfolgreich auf tatsächlichem Test-Merge `2876ec0016e23a79ddb83460e242290bc44ebf67`: 151 Python-/Medientests, 13 ausgeführte Chromium-Verträge, 20 echte Tastatur-/Kontrastfälle, 20 Layoutfälle.
- Berichte tragen die tatsächlich geprüfte CI-SHA. Artefakt `videozoom-layout-nachweise`, ID 13112139788 im #40-Lauf. Quell-HEAD, Test-Merge und Hauptzweig-Commit nicht gleichsetzen.
- Vorherige Tastaturprüfung #39: 25 natürliche Tab-Stopps pro Fall, kleinster gemessener Textkontrast 7,127:1 und Fokuskontrast 10,900:1. Diese Messwerte beziehen sich auf den #39-Artefaktbericht, nicht auf einen ungemessenen zukünftigen Stand. Entwickler-Sichtprobe der 800×600/200%- und 1280×720-Aufnahmen erfolgt; echte Kubuntu-Sichtprüfung bleibt OFFEN.

## Implementierte Wirkung
- Ausgewählte Bedienwerte mit exakter alter Dateisicherung, Fingerabdruck und gruppenweiser Rücknahme auch nach Neustart; keine Änderung von Medien/Pfaden/Ressourcen oder später veränderten anderen Werten. Schreibfehler, externe Einstellungsänderung und manipulierte Sicherung verhindern stilles Überschreiben.
- Während eigener laufender Verarbeitung nur das Farbschema speichern; laufende Worker-Konfiguration bleibt unverändert.
- Zweite Oberfläche prüft vorhandene Kern-Sperre nur lesend, zeigt frisches Journal und fremde Verarbeitung an, erfindet keine Prozente und verweigert fremde Start-/Stopp-/Schreibaktionen. Kein Löschen alter Sperren.
- Echte Tab-/Leertasten und berechnete Text-/Fokus-/disabled-/Hover-Kontraste in 20 Fällen; getrennte bestehende Layoutmatrix bleibt erhalten. Keine zusätzliche Produktruntime.

## Wiederaufnahme und verbleibender Umfang
Branch dieses reinen Nachweisabgleichs: `docs/ui-integration-evidence`, Basis `2eec90242b9477c2f41e0af690e0a35f5e287620`; neuer Dokumentations-HEAD/PR und seine vollständige Nachprüfung stehen im PR. Produktdateien unverändert. Vor weiteren Mutationen Nutzer-Input, main-HEAD und offene PRs erneut lesen.

`docs/TODO.md` bleibt allein operativ. Bedienfunktionen erledigt; UX-04b (freigegebene Pixelreferenz, Verlaufspixel/Farbsehprüfung) bleibt sichtbar offen. Danach Architektur-/Sicherheitsbewertungen, QA-FINAL, Rechte-/Lizenzentscheidung und eingefrorener Releasekandidat. Echte Kubuntu-/Nutzer-Endabnahme ausdrücklich zuletzt. Stable: NEIN.
