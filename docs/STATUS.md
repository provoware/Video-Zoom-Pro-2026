# Status und Recovery-Key – PROVOWARE Video Zoom Pro 2026

**Zeitbezug:** 2026-11-01; historischer GitHub-Zustand darf nicht als Zukunftsaussage verwendet werden.

## Bestätigter Hauptzweig
- Repository: `provoware/Video-Zoom-Pro-2026`.
- Letzter vor dieser Iteration geprüfter main-HEAD: `641b695a0c06cddb35e3a51a880d46ec2494341f`.
- Tatsächlich bestandener Main-CI: https://github.com/provoware/Video-Zoom-Pro-2026/actions/runs/41349153630 mit **58 Tests erfolgreich**.
- Die Inhalte der Entwurfs-PRs #2–#6 wurden über #8 integriert; #9 (Kubuntu-Prüfhelfer) ebenfalls.
- **Kein Stable-Release** und **keine echte Kubuntu-Abnahme**.

## Laufende Aufgaben / Konfliktgrenze
- Offener Entwicklungszweig zum Fortschrittsvertrag: `fix/progress-truthful-20261101` / PR #10, noch **nicht** main.
- Frühere Wiederanlauf-/Archiv-/Medien-Simulationen sind erfolgreich; echte Stromausfälle, längerer Zielsystembetrieb und Bildschirmprüfung sind ausdrücklich OFFEN.
- Vor neuer Mutation main-HEAD und offene PRs neu abrufen; jeweils nur ein schreibender Prozess je Bereich.
- Die nächste kleinste erlaubte Entwicklung: PR #10 auf exaktem HEAD prüfen und Integrationsstatus dokumentieren, anschließend gezielte kleine Korrekturen für Ressourcenvertrag und Bildkategoriekonflikte.

## Anforderung → Beleg → Gate
- Datei-/Medien- und Archivregeln: `videozoom/core.py`, `tests/test_workflow.py`, `tests/test_archive_recovery.py`, `tests/test_hardening.py`.
- Regression: `scripts/regression.py`, `tests/test_regression_runner.py`, bestehender CI-Workflow.
- Bedienung: `videozoom/webui.py`, `tests/test_webui.py`.
- Kubuntu-Abnahmehelfer: `scripts/kubuntu_abnahme.py`, `docs/KUBUNTU_ABNAHME.md`, `tests/test_kubuntu_abnahme.py`.
- Offen gebliebenes wird in `docs/TODO.md` fortlaufend geführt.

**Abnahmeordnung:** Entwicklungsfehler und Dokumentationsarbeit → gemeinsamer grüner Main-Stand → eingefrorener Kandidat → **zuletzt** echte Kubuntu-Abnahme → erst dann Stable-Entscheidung.
