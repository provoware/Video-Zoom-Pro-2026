# Testplan

Testdaten mit python3 tests/fixtures/generieren.py erzeugen: eine synthetische WAV und zwei eigene kleine PNGs. Keine fremden Werke. Der Medienintegrationstest erzeugt ein echtes H.264/AAC-MP4 und kontrolliert die Archivierung.

Kernprüfungen: python3 -m compileall -q videozoom tests und python3 -m unittest discover -s tests -v. GitHub Actions enthält dieselben Schritte.

Negative Prüfungen: keine Bilder, beschädigte WAV, doppelte Sperre, beschädigtes Journal, Paketänderung, Dateinamenskollision, fehlender CPU-Scope, Abbruch während Rendern und Archivierung. Letztere bleiben auszubauen, bevor Stable freigegeben wird.

Nicht ausgeführte Tests sind offen; keine simulierte Kubuntu-Abnahme behaupten.

## Neue Regressionen – Wiederanlauf
`tests/test_recovery.py` prüft ohne FFmpeg per lokalem Prüfersatz die Kritischen Übergänge: Veröffentlichung vor Journalabschluss, bestätigte temporäre MP4, Abbruch ohne gespeicherten Hash, beschädigter Hash, alter Journalstand ohne Ausgabeverweis, sichere Teil-Dateinamen und unantastbare symbolische Verknüpfungen. Damit wird Datenintegrität absichtlich auch durch Negativfälle getestet.

**Nicht abgedeckt:** harte SIGKILL-Prozessabbrüche auf echten FFmpeg-Langzeitaufträgen, Stromausfall/Dateisystemfehler und reale systemd-Kontrollgruppen-Messung.

## Gezielte Regression und Pflicht-Gesamtlauf

Das eigenständige Skript `scripts/regression.py` ermittelt aus einer Liste geänderter Dateien die betroffenen Tests. Bekannte Änderungen aktivieren gezielt die passenden Module **plus unverzichtbare Archiv-/Journal-/Paket-Schutztests**. Unbekannte Dateien, fehlende Vergleichsdaten und Änderungen an der Prüf-Infrastruktur führen automatisch zur vollständigen Prüfung. Es gibt kein stilles „grün“, wenn keine Tests gelaufen sind.

Beispiele:
- Lokal gezielt: `python3 scripts/regression.py --paths videozoom/core.py`.
- Nach Branch-Vergleich: `python3 scripts/regression.py --base main`.
- Vollständig vor Integration: `python3 scripts/regression.py --all`.
- Bericht: zusätzlich `--bericht /gewünschter/ordner/regression.json`.

Der bestehende GitHub-CI-Workflow führt den **vollständigen** Lauf aus. Prüfberichte enthalten Commitkennung, Prüfstrategie, Anzahl, Ausfälle und übersprungene Tests. Ein fehlgeschlagener Test wird protokolliert, niemals automatisch als bestanden dargestellt. Das System ist eine Auswirkungs-/Regressionsauswahl, **keine** autonome Codekorrektur.
