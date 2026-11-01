# PROVOWARE Video Zoom Pro – priorisierte Aufgaben (aktualisiert 01.11.2026)

**Stand:** main `d486f30d2098777b59bc99330ddc3e5e1e2a884e`; vollständige Hauptzweig-Nachprüfung [GitHub #41356578575](https://github.com/provoware/Video-Zoom-Pro-2026/actions/runs/41356578575) erfolgreich. PR #19 begrenzte Fehlerwiederholungen, PR #20 isolierter ZIP-Start, jeweils per CI getestet. Stable weiterhin gesperrt.
**Wichtig:** Die echte Kubuntu-Gesamtabnahme ist ausdrücklich der **letzte Schritt**. #10, #14 (mit #12/#13), #15 und #16 wurden nach erfolgreich getesteten Entwicklungsständen integriert. Simulationsprüfungen sind keine echte Kubuntu-Abnahme.

## P0 – vor Kubuntu fachlich abschliessen
- [x] 2026-11-01 | Fortschritt | Vorbereitung, Stapel und aktuelles Video mit getrennten tatsächlichen Werten; keine falschen 100 % | prüfen: PR #10, fünf Negativtests und Main-CI #41353245356 | fertig wenn: 100 % nur nach nachgewiesener Archivierung.
- [x] 2026-11-01 | Ressourcenvertrag | Startdiagnose muss fuer die wirkliche Benutzerkonfiguration denselben CPU-/RAM-Scope wie der Renderer prüfen | prüfen: PRs #12/#14, CPU-/RAM-Negativtests und Main-CI #41354636904; abweichender RAM-Wert, kein systemd, Wiederanlauf | fertig wenn: identischer Grenzvertrag, ohne neue Abhaengigkeit.
- [x] 2026-11-01 | Bildkategorien | Mehrdeutige Marker (z. B. ChatGPT+PROVOWARE+THEMA) nicht automatisch verschieben | prüfen: PRs #12/#14, Konfliktmatrix und Main-CI #41354636904; alle Ein-/Zwei-/Dreifachkombinationen, konflikthafte Bildnamen | fertig wenn: eindeutige Kategorien, sonst unveraenderte Quelle.
- [x] 2026-11-01 | Fehlerpraevention | Fehlerarten, automatische sichere Korrektur, Maximalversuche und wiederaufnehmbare Auftraege gezielt vervollstaendigen | prüfen: PR #19, vier neue Grenztests, 86/86 PR-Tests, Main-CI #41356376384 | fertig wenn: maximal drei technische Render- und Archivversuche, danach PRUEFEN ohne Originalverlust.
- [x] 2026-11-01 | Archiv | Luecken zwischen Kopieren, Dateifingerabdruck, Veroeffentlichung, Entfernen der Quelle, Quittung und Journalspeicherung absichern | prüfen: PR #14, Quellpfad-/Quittungs-/Fehlerinjektionstests, Main-CI #41354636904; gezielte Fehler-Injektionen pro Grenze | fertig wenn: keine Scheinerfolge und keine unbemerkten Quittungsduplikate.
- [x] 2026-11-01 | Medien-Stapel | Mindestens 20 synthetische Songs vor der Zielsystemabnahme automatisch testen | prüfen: PRs #13/#14, 20 MP4/5 Neustarts/60 Quittungen, Main-CI #41354636904; mehrere Stapel, Crash/Neustart, 20 MP4s, Original- und Log-Konsistenz | fertig wenn: auf einem GitHub-Commit reproduzierbar bestanden.
- [ ] 2026-11-01 | Recht | Geeignete Lizenzentscheidung und Nutzungsrechte der Veroeffentlichungsdateien dokumentieren | prüfen: Rechte der eingebundenen Dateien und ausdrueckliche Entscheidung | fertig wenn: vor Stable nachvollziehbar geklärt.

## P1 – Qualitaetsabschluss vor Kubuntu
- [x] 2026-11-01 | Regression | Alle technischen Korrekturen zusammen testen und Main-Gesamtpruefung erfolgreich auswerten | prüfen: 82/82 Tests auf main #41354636904; unveraenderter SHA, echtes FFmpeg, Negative und Browser-Sicherheit | fertig wenn: keine bekannten blockierenden Codefehler.
- [x] 2026-11-01 | Dokumentation | TODO, STATUS, README, TESTPLAN und CHANGELOG mit der Implementierung und den Testnachweisen synchronisieren | prüfen: PR #17, Main-CI https://github.com/provoware/Video-Zoom-Pro-2026/actions/runs/41355104172 erfolgreich; Dateien gegen aktuellen main-HEAD und offenes PR-Protokoll | fertig wenn: keine historischen Staende als aktuell markiert.
- [x] 2026-11-01 | Paket | Deterministisches Offline-ZIP mit prüfbaren Dateifingerabdrücken ohne Nutzer- und Testdaten erstellen | prüfen: PR #15, vier Build-/Negativtests und Main-CI #41354636904 | fertig wenn: reproduzierbarer Entwicklungskandidat ohne Stable-Behauptung.
- [x] 2026-11-01 | Bereitstellung | Frisch entpackten ZIP-Programmstart in isolierter Umgebung prüfen | prüfen: PR #20, 88/88 Tests, Main-CI #41356578575, --help/--doctor mit getrenntem HOME | fertig wenn: Paket ohne Systemeingriffe testbar.
- [ ] 2026-11-01 | Releasekandidat | Nach geklärter Lizenz den unveränderlichen Kandidaten-SHA einfrieren | prüfen: Rechte, CI, ZIP-Manifest und Hash | fertig wenn: letzter technischer Stand vor Kubuntu dokumentiert.

## Bereits nachweisbar erledigte Entwicklungsbausteine
- [x] 2026-11-01 | Integration | PRs #2–#6 durch #8 zusammengeführt; #9 integriert | prüfen: Main `641b695...` und CI #41349153630 | fertig wenn: geprüfter Main-Stand vorliegt.
- [x] 2026-11-01 | Wiederanlauf | LAEUFT-Status und fertige MP4 nach Prozessabbruch wiederfinden | prüfen: tests/test_recovery.py, tests/test_hardening.py, 58/58 CI | fertig wenn: geprüfte Wiederaufnahme ohne nachgewiesenen Doppelrender.
- [x] 2026-11-01 | Dateieingang | Originale schützen, drei Kategorien und Bilddimensionen als JSON speichern | prüfen: tests/test_workflow.py | fertig wenn: Basispfad ohne Quellueberschreiben vorhanden; Konfliktverbesserung P0 offen.
- [x] 2026-11-01 | Ordnerauswahl | Tk-freie lokale KDE-/Zenity-Ordnerdialoge implementieren | prüfen: tests/test_webui.py | fertig wenn: API- und Logiktests gruen; reale Desktop-Sichtprüfung folgt zuletzt.


## P1 – DateiFinder-Designtransfer (NI-20261101-01, vor der letzten Kubuntu-Abnahme)

**Quelle:** Nutzerauftrag im Chat vom 01.11.2026: beiden Funktionsdiagramme versionieren, Layout/Design des DateiFinders prüfen und konfliktfreie Muster übernehmen. **Abhängigkeiten:** CODE-Vergleich und Datenintegrität vor Gestaltung, Browser-/Regressionstest vor Integration, Lizenz/Release vor Kubuntu. Kein Re-Import von Tauri/Rust.

- [x] 2026-11-01 | Dokumentation | Zwei Funktionsgrafiken als versionierte, in GitHub direkt sichtbare Mermaid-Diagramme übernehmen | prüfen: `docs/diagramme/01_einfacher_prozess.md`, `02_funktionsfluss_technik.md` mit Python-Funktionen abgleichen | fertig wenn: Diagramme fachlich konsistent mit main sind.
- [x] 2026-11-01 | Designanalyse | DateiFinder-Referenzlayout, Farben, Bedienmuster und Qualitätssicherung gegen Video-Zoom-Pro-Architektur abgleichen | prüfen: `docs/DESIGN_TRANSFER_DATEIFINDER.md` inklusive Konfliktmatrix | fertig wenn: Übertragbares von Tauri-/Rust-/Mini-Layout-Abhängigkeiten getrennt ist.
- [x] 2026-11-01 | Farbsystem | Vier eigene Themen Cyan, Violett, Grün, Orange mit sicherer dauerhafter Auswahl | prüfen: PR #23, Whitelist-/Persistenztests, CI + Browserproben | fertig wenn: Farben/Backend-Einstellungen ohne Tauri/Tk-Code und ohne neue Laufzeitabhängigkeit funktionieren.
- [ ] 2026-11-01 | Kontraste | Alle Interaktionszustände (inkl. Fehler/disabled/Fokus) nach WCAG AA und Farbblindheit untersuchen | prüfen: kontrastbasierte Regression + dokumentierte Sichtprobe | fertig wenn: kontrastkritische Zustände auch ohne Farbe lesbar bleiben.
- [x] 2026-11-01 | Kopf und Navigation | Vier direkte Sprunganker und kompakterer Kopf mit verständlichen Kurzbezeichnungen auch bei 200%-Vergrößerung | prüfen: PRs #23/#25, 100 Python-Tests, 20 Chromium-Matrixfälle, Screenshot-/Textüberlaufprüfung | fertig wenn: Hauptbereiche lesbar, Anker erreichbar und Schrift nicht über Kartenränder ragt.
- [ ] 2026-11-01 | Bedienkomfort | Diagnose/Protokolle einklappbar und scrollend, Aufgabenkarte/Fehlerhilfe laienverständlich gestalten | prüfen: 800×600/200%, fokussierte Tastatur- und Browserprüfungen | fertig wenn: Start/Stop und Fehlerlösung ohne Verwirrung erreichbar bleiben.
- [ ] 2026-11-01 | Barrierefreiheit | Fokus, ARIA-Status, reduzierte Animationen, farbunabhängige Warnungen und verständliche Leerzustände | prüfen: Tastatur- und automatisierte UI-Sicherheitsprüfungen | fertig wenn: kein kritischer Bedienweg nur durch Farbe, Maus oder Animation verständlich ist.
- [x] 2026-11-01 | Browser-Vorprüfung | Echte Chromium-Aufnahmen ohne Nutzerdaten, 800×600 bei 100/125/150/200% sowie 1280×720, alle vier Farbschemata, Überlauf/Textgrenzen | prüfen: PRs #24/#25, je 20 Browserproben und 5 Bildnachweise pro Lauf | fertig wenn: Messwerte und Screenshots im Actions-Artefakt dem SHA zugeordnet sind.
- [ ] 2026-11-01 | Pixel-/Interaktionsregression | Versioniertes freigegebenes Referenzbild, bewusste Bildänderungsfreigabe, echter Browser-Zoom und Tab-/Fokusfolge | prüfen: reproduzierbarer Pixelvergleich + Tastaturtest bei 200% | fertig wenn: nicht nur Layoutbreite, sondern unbeabsichtigte Bildänderungen und Fokusfehler automatisch auffallen.
- [ ] 2026-11-01 | Konsolidierung | Dokumentation, Diagramme und automatisierte Funktions-/Layouttests nach Designänderungen synchronisieren | prüfen: vollständige CI, keine Medienregression, Update des Referenzstands | fertig wenn: gemeinsamer geprüfter Entwicklungsstand vorliegt.

**Schutz gegen Planaufweichung:** DateiFinder liefert Muster, keine Lizenz- oder Architekturfreigabe für 1:1-Kopie. Keine Änderung der Render-/Archivverträge in einem reinen UI-Patch; Kubuntu bleibt letzter Abnahmeschritt.

## FINAL – Kubuntu-Abnahme erst nach allen vorherigen Gates
- [ ] 2026-11-01 | Kubuntu-Endabnahme | 800×600, 100/125/150/200 %, Tastatur, echte Dateidialoge, 30%-CPU-/RAM-cgroup-Messung und Langzeitbetrieb | prüfen: Zielrechner, Screenshots, JSON-Messbericht, Originalschutz, Release-SHA | fertig wenn: alle realen Belege auf eingefrorenem Kandidaten positiv und Stable-Entscheidung dokumentiert.

**Nächster erlaubter Schritt:** DateiFinder-Designtransfer bei Textkontrasten, verständlicher Detailansicht und Pixel-/Tastaturregression fertigstellen und danach die geprüfte gemeinsame Dokumentation einfrieren. Danach Lizenz/Rechte verbindlich entscheiden, einen unveränderlichen Releasekandidaten bilden; **Kubuntu-Endabnahme bleibt strikt der letzte Schritt.**
