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

## Reale Abbruch- und Stapel-Haertetests (2026-11-01)
`tests/test_hardening.py` erzeugt ausschliesslich synthetische WAV-/PNG-Testmedien in temporaeren Verzeichnissen und nutzt echtes FFmpeg/FFprobe. Die Pruefungen simulieren reale Programmabbrueche:
1. `os._exit` nach fertiger Videodatei, bevor der normale Journaleintrag erfolgt: Wiederanlauf ohne doppeltes MP4 und mit abgeschlossener Archivierung.
2. `os._exit` mitten im Kopieren einer Archivdatei: Originale bleiben erhalten, der naechste Lauf archiviert sicher.
3. Ein echter `SIGKILL` eines vorbereitenden Python-Prozesses: Der gespeicherte Auftrag ist nach Neustart weiter nutzbar.
4. Drei Songs in zwei aufeinanderfolgenden Stapeln und nochmaliger Leerlaufpruefung.
5. Ein beschaedigtes WAV-Medium wird isoliert, ein gesunder Auftrag wird trotzdem vollstaendig verarbeitet.

Die Medien-Haertetests nutzen ausdruecklich den internen **Testmodus** ohne systemd-Quote. Dies ist kein Nachweis der CPU-/RAM-Grenze unter Kubuntu und ersetzt keine reale Endabnahme. CI-Erfolg gilt nur fuer den exakt ausgewiesenen Commit.

## Qualitätsergebnisse vor der letzten Kubuntu-Abnahme (01.11.2026)

- Fortschritt: `tests/test_progress.py` deckt Pausieren, Archivfehler, Teilstapel und die korrekte 100%-Grenze ab.
- Bild/Quota: `tests/test_category_quota.py` prueft Konfliktmarker, unveränderte Quellen sowie die tatsächliche Benutzerkonfiguration.
- Archivbelege: `tests/test_archive_evidence.py` prueft idempotente Logzeilen, verbotene externe Quellen, ungültige Logdaten und Symlink-Konflikte.
- Langzeit-Simulation: `tests/test_batch_20.py` erzeugt 20 synthetische WAV-Videos mit echtem FFmpeg, 5 Stapelinstanzen und 60 Archivbelegen; keine Zielsystem-Lastgarantie.
- Entwicklungspaket: `tests/test_build_bundle.py` prüft reproduzierbare ZIPs, SHA-256-Manifest, ausführbare STARTEN.sh-Rechte und Nichtüberschreiben.
- CLI: `tests/test_cli_settings.py` sichert ab, dass --doctor die gespeicherten Quotenwerte nutzt.
- **82/82 Tests** auf main `c1f67a460e17eaa11ab88999582a05a3d9399e44`, GitHub-Lauf https://github.com/provoware/Video-Zoom-Pro-2026/actions/runs/41354636904 erfolgreich.

Weiterhin offen: echte Kubuntu-/KDE-Sichtprüfung, reales cgroup-Verhalten unter Songlast, Langzeitbetrieb auf Zielrechner und der Rechts-/Stable-Gate. Der kontrollierte Testmodus ist kein Ersatz für diese Nachweise.

## Fehler-Eskalation und automatische Grenzen (01.11.2026)
Wiederholbare Renderfehler werden maximal dreimal automatisch versucht. Fehlgeschlagene Archivschritte werden maximal dreimal versucht; zwischen Wiederholungen liegt eine ansteigende Wartezeit. Die erste Archivierung zählt als erster Versuch. Danach bleibt der Auftrag mit verständlichem Status **PRUEFEN** erhalten, ohne Originaldaten zu verändern. Der restliche Stapel kann weiterlaufen. Diese Regeln werden durch `tests/test_retry_limits.py` mit Negativfällen überprüft. Der Status ist keine automatische Reparaturgarantie; manuelle Wiederfreigabe darf nur nach Ursacheprüfung erfolgen.
