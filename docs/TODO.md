# PROVOWARE Video Zoom Pro – priorisierte Aufgaben (aktualisiert 01.11.2026)

**Stand bei letzter Bestandsprüfung:** main `c1f67a460e17eaa11ab88999582a05a3d9399e44`; Main-CI https://github.com/provoware/Video-Zoom-Pro-2026/actions/runs/41354636904 mit **82/82 Tests bestanden**.
**Wichtig:** Die echte Kubuntu-Gesamtabnahme ist ausdrücklich der **letzte Schritt**. #10, #14 (mit #12/#13), #15 und #16 wurden nach erfolgreich getesteten Entwicklungsständen integriert. Simulationsprüfungen sind keine echte Kubuntu-Abnahme.

## P0 – vor Kubuntu fachlich abschliessen
- [x] 2026-11-01 | Fortschritt | Vorbereitung, Stapel und aktuelles Video mit getrennten tatsächlichen Werten; keine falschen 100 % | prüfen: PR #10, fünf Negativtests und Main-CI #41353245356 | fertig wenn: 100 % nur nach nachgewiesener Archivierung.
- [x] 2026-11-01 | Ressourcenvertrag | Startdiagnose muss fuer die wirkliche Benutzerkonfiguration denselben CPU-/RAM-Scope wie der Renderer prüfen | prüfen: PRs #12/#14, CPU-/RAM-Negativtests und Main-CI #41354636904; abweichender RAM-Wert, kein systemd, Wiederanlauf | fertig wenn: identischer Grenzvertrag, ohne neue Abhaengigkeit.
- [x] 2026-11-01 | Bildkategorien | Mehrdeutige Marker (z. B. ChatGPT+PROVOWARE+THEMA) nicht automatisch verschieben | prüfen: PRs #12/#14, Konfliktmatrix und Main-CI #41354636904; alle Ein-/Zwei-/Dreifachkombinationen, konflikthafte Bildnamen | fertig wenn: eindeutige Kategorien, sonst unveraenderte Quelle.
- [ ] 2026-11-01 | Fehlerpraevention | Fehlerarten, automatische sichere Korrektur, Maximalversuche und wiederaufnehmbare Auftraege gezielt vervollstaendigen | prüfen: Medienfehler, Laufzeitabbruch, Datenträger voll, unklare Quelle, Journalfehler | fertig wenn: keine Endlosschleife, kein fremder Dateiverlust.
- [x] 2026-11-01 | Archiv | Luecken zwischen Kopieren, Dateifingerabdruck, Veroeffentlichung, Entfernen der Quelle, Quittung und Journalspeicherung absichern | prüfen: PR #14, Quellpfad-/Quittungs-/Fehlerinjektionstests, Main-CI #41354636904; gezielte Fehler-Injektionen pro Grenze | fertig wenn: keine Scheinerfolge und keine unbemerkten Quittungsduplikate.
- [x] 2026-11-01 | Medien-Stapel | Mindestens 20 synthetische Songs vor der Zielsystemabnahme automatisch testen | prüfen: PRs #13/#14, 20 MP4/5 Neustarts/60 Quittungen, Main-CI #41354636904; mehrere Stapel, Crash/Neustart, 20 MP4s, Original- und Log-Konsistenz | fertig wenn: auf einem GitHub-Commit reproduzierbar bestanden.
- [ ] 2026-11-01 | Recht | Geeignete Lizenzentscheidung und Nutzungsrechte der Veroeffentlichungsdateien dokumentieren | prüfen: Rechte der eingebundenen Dateien und ausdrueckliche Entscheidung | fertig wenn: vor Stable nachvollziehbar geklärt.

## P1 – Qualitaetsabschluss vor Kubuntu
- [x] 2026-11-01 | Regression | Alle technischen Korrekturen zusammen testen und Main-Gesamtpruefung erfolgreich auswerten | prüfen: 82/82 Tests auf main #41354636904; unveraenderter SHA, echtes FFmpeg, Negative und Browser-Sicherheit | fertig wenn: keine bekannten blockierenden Codefehler.
- [ ] 2026-11-01 | Dokumentation | TODO, STATUS, README, TESTPLAN und CHANGELOG mit der Implementierung und den Testnachweisen synchronisieren | prüfen: Dateien gegen aktuellen main-HEAD und offenes PR-Protokoll | fertig wenn: keine historischen Staende als aktuell markiert.
- [x] 2026-11-01 | Paket | Deterministisches Offline-ZIP mit prüfbaren Dateifingerabdrücken ohne Nutzer- und Testdaten erstellen | prüfen: PR #15, vier Build-/Negativtests und Main-CI #41354636904 | fertig wenn: reproduzierbarer Entwicklungskandidat ohne Stable-Behauptung.
- [ ] 2026-11-01 | Bereitstellung | Den aus ZIP entpackten Programmstart in isolierter Umgebung prüfen und Releasekandidaten einfrieren | prüfen: Startskript, Hilfe, Prüfsummen, keine Systemänderungen | fertig wenn: Kandidat für abschließendes Kubuntu bereit.

## Bereits nachweisbar erledigte Entwicklungsbausteine
- [x] 2026-11-01 | Integration | PRs #2–#6 durch #8 zusammengeführt; #9 integriert | prüfen: Main `641b695...` und CI #41349153630 | fertig wenn: geprüfter Main-Stand vorliegt.
- [x] 2026-11-01 | Wiederanlauf | LAEUFT-Status und fertige MP4 nach Prozessabbruch wiederfinden | prüfen: tests/test_recovery.py, tests/test_hardening.py, 58/58 CI | fertig wenn: geprüfte Wiederaufnahme ohne nachgewiesenen Doppelrender.
- [x] 2026-11-01 | Dateieingang | Originale schützen, drei Kategorien und Bilddimensionen als JSON speichern | prüfen: tests/test_workflow.py | fertig wenn: Basispfad ohne Quellueberschreiben vorhanden; Konfliktverbesserung P0 offen.
- [x] 2026-11-01 | Ordnerauswahl | Tk-freie lokale KDE-/Zenity-Ordnerdialoge implementieren | prüfen: tests/test_webui.py | fertig wenn: API- und Logiktests gruen; reale Desktop-Sichtprüfung folgt zuletzt.

## FINAL – Kubuntu-Abnahme erst nach allen vorherigen Gates
- [ ] 2026-11-01 | Kubuntu-Endabnahme | 800×600, 100/125/150/200 %, Tastatur, echte Dateidialoge, 30%-CPU-/RAM-cgroup-Messung und Langzeitbetrieb | prüfen: Zielrechner, Screenshots, JSON-Messbericht, Originalschutz, Release-SHA | fertig wenn: alle realen Belege auf eingefrorenem Kandidaten positiv und Stable-Entscheidung dokumentiert.

**Nächster erlaubter Entwicklungsschritt:** Dokumentations-PR #11 abschließen, den isolierten Entpack-/Starttest dokumentieren und die noch offene Lizenz-/Fehlerregel-Entscheidung klären. **Erst danach Kubuntu-Endabnahme.**
