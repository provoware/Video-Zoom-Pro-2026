# PROVOWARE Video Zoom Pro – priorisierte Aufgaben (aktualisiert 01.11.2026)

**Stand bei Bestandsprüfung:** main `641b695a0c06cddb35e3a51a880d46ec2494341f`; letzter Main-CI https://github.com/provoware/Video-Zoom-Pro-2026/actions/runs/41349153630 **58/58 Tests erfolgreich**.
**Wichtig:** Die Abnahme auf Kubuntu ist der **letzte Entwicklungsschritt** vor einer Stable-Veröffentlichung, nicht das nächste Arbeitspaket. Simulierte Tests ersetzen die reale Sichtprüfung nicht. Der offene Fortschritts-PR #10 zählt bis zur Integration noch nicht als erledigt.

## P0 – vor Kubuntu fachlich abschliessen
- [ ] 2026-11-01 | Fortschritt | Vorbereitung, Stapel und aktuelles Video mit getrennten tatsächlichen Werten; keine falschen 100 % | prüfen: Pausieren, Archivierungsfehler, Teilstapel, Neustart und Main-CI; PR #10 | fertig wenn: 100 % nur nach nachgewiesener Archivierung.
- [ ] 2026-11-01 | Ressourcenvertrag | Startdiagnose muss fuer die wirkliche Benutzerkonfiguration denselben CPU-/RAM-Scope wie der Renderer prüfen | prüfen: abweichender RAM-Wert, kein systemd, Wiederanlauf | fertig wenn: identischer Grenzvertrag, ohne neue Abhaengigkeit.
- [ ] 2026-11-01 | Bildkategorien | Mehrdeutige Marker (z. B. ChatGPT+PROVOWARE+THEMA) nicht automatisch verschieben | prüfen: alle Ein-/Zwei-/Dreifachkombinationen, konflikthafte Bildnamen | fertig wenn: eindeutige Kategorien, sonst unveraenderte Quelle.
- [ ] 2026-11-01 | Fehlerpraevention | Fehlerarten, automatische sichere Korrektur, Maximalversuche und wiederaufnehmbare Auftraege gezielt vervollstaendigen | prüfen: Medienfehler, Laufzeitabbruch, Datenträger voll, unklare Quelle, Journalfehler | fertig wenn: keine Endlosschleife, kein fremder Dateiverlust.
- [ ] 2026-11-01 | Archiv | Luecken zwischen Kopieren, Dateifingerabdruck, Veroeffentlichung, Entfernen der Quelle, Quittung und Journalspeicherung absichern | prüfen: gezielte Fehler-Injektionen pro Grenze | fertig wenn: keine Scheinerfolge und keine unbemerkten Quittungsduplikate.
- [ ] 2026-11-01 | Medien-Stapel | Mindestens 20 synthetische Songs vor der Zielsystemabnahme automatisch testen | prüfen: mehrere Stapel, Crash/Neustart, 20 MP4s, Original- und Log-Konsistenz | fertig wenn: auf einem GitHub-Commit reproduzierbar bestanden.
- [ ] 2026-11-01 | Recht | Geeignete Lizenzentscheidung und Nutzungsrechte der Veroeffentlichungsdateien dokumentieren | prüfen: Rechte der eingebundenen Dateien und ausdrueckliche Entscheidung | fertig wenn: vor Stable nachvollziehbar geklärt.

## P1 – Qualitaetsabschluss vor Kubuntu
- [ ] 2026-11-01 | Regression | Alle technischen Korrekturen zusammen testen und Main-Gesamtpruefung erfolgreich auswerten | prüfen: unveraenderter SHA, echtes FFmpeg, Negative und Browser-Sicherheit | fertig wenn: keine bekannten blockierenden Codefehler.
- [ ] 2026-11-01 | Dokumentation | TODO, STATUS, README, TESTPLAN und CHANGELOG mit der Implementierung und den Testnachweisen synchronisieren | prüfen: Dateien gegen aktuellen main-HEAD und offenes PR-Protokoll | fertig wenn: keine historischen Staende als aktuell markiert.
- [ ] 2026-11-01 | Releasevorbereitung | Portables Paket, Startprüfung, notwendige Systemkomponenten, Testdaten und Metadaten auf vorletztem Entwicklungsstand absichern | prüfen: Build-/Installations-/Entpacktest und SHA-256 | fertig wenn: eingefrorener Releasekandidat zur Kubuntu-Abnahme bereit.

## Bereits nachweisbar erledigte Entwicklungsbausteine
- [x] 2026-11-01 | Integration | PRs #2–#6 durch #8 zusammengeführt; #9 integriert | prüfen: Main `641b695...` und CI #41349153630 | fertig wenn: geprüfter Main-Stand vorliegt.
- [x] 2026-11-01 | Wiederanlauf | LAEUFT-Status und fertige MP4 nach Prozessabbruch wiederfinden | prüfen: tests/test_recovery.py, tests/test_hardening.py, 58/58 CI | fertig wenn: geprüfte Wiederaufnahme ohne nachgewiesenen Doppelrender.
- [x] 2026-11-01 | Dateieingang | Originale schützen, drei Kategorien und Bilddimensionen als JSON speichern | prüfen: tests/test_workflow.py | fertig wenn: Basispfad ohne Quellueberschreiben vorhanden; Konfliktverbesserung P0 offen.
- [x] 2026-11-01 | Ordnerauswahl | Tk-freie lokale KDE-/Zenity-Ordnerdialoge implementieren | prüfen: tests/test_webui.py | fertig wenn: API- und Logiktests gruen; reale Desktop-Sichtprüfung folgt zuletzt.

## FINAL – Kubuntu-Abnahme erst nach allen vorherigen Gates
- [ ] 2026-11-01 | Kubuntu-Endabnahme | 800×600, 100/125/150/200 %, Tastatur, echte Dateidialoge, 30%-CPU-/RAM-cgroup-Messung und Langzeitbetrieb | prüfen: Zielrechner, Screenshots, JSON-Messbericht, Originalschutz, Release-SHA | fertig wenn: alle realen Belege auf eingefrorenem Kandidaten positiv und Stable-Entscheidung dokumentiert.

**Nächster erlaubter Entwicklungsschritt:** echten Fortschritts-PR #10 abschliessend pruefen; dann Ressourcenkonsistenz und mehrdeutige Bildkategorien klein und mit Negativtests korrigieren.
