# Status und Recovery-Key – PROVOWARE Video Zoom Pro 2026

**Aktuelle geprüfte Basis, 01.11.2026:** `main` `d486f30d2098777b59bc99330ddc3e5e1e2a884e`; [GitHub-Prüfung #41356578575](https://github.com/provoware/Video-Zoom-Pro-2026/actions/runs/41356578575) erfolgreich.

## Abgeschlossene Entwicklung
- Kern-Workflow WAV → Bildregie → MP4 → Archiv, Dauer- und Prüfsummenkontrolle, drei Formatbereiche und fünf Formate.
- #8/#9: Basisintegration und Kubuntu-Prüfhelfer.
- #10/#14/#15/#16: Fortschritt ohne falsche 100 %, Bilder-/Quoten-/Archiv-Härtung, 20-Song-Test, Offline-ZIP und Diagnose.
- #17/#18: Dokumentations- und Zustandsbereinigung.
- #19: maximale Wiederholungsanzahl, Wartefrist, status PRUEFEN statt unendlicher Fehlerschleifen; 86/86 Tests auf PR und erfolgreicher Hauptzweig-Lauf.
- #20: isolierter Start aus frisch entpacktem Offline-ZIP (STARTEN.sh --help/--doctor), keine installierten Zusatzpakete; 88/88 PR-Tests und Main-CI erfolgreich.
- Qualitätsstandards aus TOOL_2026_Multi und PROVOWARE_DATEIFINDER nur selektiv übernommen: kleine Scope-Änderung, Single Writer, belegter SHA, wiederholbare Negativtests, keine riskanten automatischen Reparaturen.

## Verbleibende Gates (in dieser Reihenfolge)
1. **Recht/Lizenz:** Nutzerentscheidung für die öffentliche Quellcode-Lizenz und Rechte-/Veröffentlichungsprüfung; die Software setzt keine Lizenz stillschweigend voraus.
2. **Releasekandidat:** Nach Entscheidung exakten Quellcode- und ZIP-SHA dokumentieren und Entwicklung einfrieren.
3. **Zuletzt Kubuntu:** echte Sichtprüfung 800×600/100–200 %, native Dialoge und Tastatur; 30%-CPU-/RAM-cgroup-Messung und reale Langzeit-Stapelverarbeitung. Nicht in GitHub simulierbar.

## Recovery-Key
- Repo: `provoware/Video-Zoom-Pro-2026`, aktueller bestätigter Ausgangsstand siehe oben; bei jeder Mutation SHA erneut lesen.
- Quellprojekt VideoBatch bleibt unberührt; keine Tk- oder Cloud-Abhängigkeit.
- `docs/TODO.md` = einziger verbindlicher offener Aufgabenplan; `docs/TESTPLAN.md` = Prüfanweisung.
- Geprüftes Ergebnis ≠ Stable. Bis zur Kubuntu-Endabnahme kein Release als fertig kennzeichnen.
