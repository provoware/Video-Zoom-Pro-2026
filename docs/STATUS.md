# Status und Recovery-Key – PROVOWARE Video Zoom Pro 2026

**Zeitbezug:** 2026-11-01; historischer GitHub-Zustand darf nicht als Zukunftsaussage verwendet werden.

## Bestätigter Hauptzweig
- Repository: `provoware/Video-Zoom-Pro-2026`.
- Letzter überprüfter main-HEAD: `e9e4c4fa79eb25e17e623a645bf32b99a78d3bb4`.
- Tatsächlich bestandener Main-CI: https://github.com/provoware/Video-Zoom-Pro-2026/actions/runs/41355104172 (**82/82 Tests**).
- Die Inhalte der Entwurfs-PRs #2–#6 wurden über #8 integriert; #9 (Kubuntu-Prüfhelfer) ebenfalls.
- **Kein Stable-Release** und **keine echte Kubuntu-Abnahme**.

## Laufende Aufgaben / Konfliktgrenze
- Fortschrittsvertrag PR #10 ist in main integriert und nachgeprüft.
- Technische Integrationen #14 (Kategorien, Quoten, 20 Songs, Archivbelege), #15 (prüfbares Offline-ZIP) und #16 (Diagnosewerte/Timeouts) sind in main und nachgeprüft.
- Ältere Einzel-PRs #12 und #13 sind durch #14 inhaltlich ersetzt und dürfen erst nach entsprechendem Nachweis geschlossen werden.
- Dokumentations-PR #11 enthält die hier angezeigten neuen Regeln und Befunde; Dokumentations-CI noch auf seinem endgültigen HEAD prüfen.
- Frühere Wiederanlauf-/Archiv-/Medien-Simulationen sind erfolgreich; echte Stromausfälle, längerer Zielsystembetrieb und Bildschirmprüfung sind ausdrücklich OFFEN.
- Vor neuer Mutation main-HEAD und offene PRs neu abrufen; jeweils nur ein schreibender Prozess je Bereich.
- Nächste erlaubte Entwicklung: Dokumentations-Gates #11 prüfen, isolierten ZIP-Entpack-/Start-Smoke einplanen, Fehlerklassifikation und Lizenzentscheidung vervollständigen; danach Releasekandidat einfrieren, zuletzt Kubuntu.

## Anforderung → Beleg → Gate
- Datei-/Medien- und Archivregeln: `videozoom/core.py`, `tests/test_workflow.py`, `tests/test_archive_recovery.py`, `tests/test_hardening.py`.
- Regression: `scripts/regression.py`, `tests/test_regression_runner.py`, bestehender CI-Workflow.
- Bedienung: `videozoom/webui.py`, `tests/test_webui.py`.
- Kubuntu-Abnahmehelfer: `scripts/kubuntu_abnahme.py`, `docs/KUBUNTU_ABNAHME.md`, `tests/test_kubuntu_abnahme.py`.
- Offen gebliebenes wird in `docs/TODO.md` fortlaufend geführt.

**Abnahmeordnung:** Entwicklungsfehler und Dokumentationsarbeit → gemeinsamer grüner Main-Stand → eingefrorener Kandidat → **zuletzt** echte Kubuntu-Abnahme → erst dann Stable-Entscheidung.

## Dokumentations-Abschluss (2026-11-01)
- AGENTS, TODO, STATUS, README, TESTPLAN und CHANGELOG durch PR #17 in main übernommen und GitHub-CI nachgeprüft.
- Historische Entwurfs-PRs #11/#12/#13 sind mit Verweis auf #17/#14 geschlossen; funktional kein Duplikat.
- Letzte offenen Aufgaben vor Kubuntu: technische Fehlerregel-/Wiederanlauf-Eskalation, Rechts-/Lizenzentscheidung und entpackter Entwicklungskandidaten-Starttest.
- Finale echte Kubuntu-Abnahme bleibt als **letzter** Schritt; bisher nicht durchgeführt.
