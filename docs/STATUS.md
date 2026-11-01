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

## 01.11.2026 – DateiFinder-Designtransfer (Stand der Entwicklung, nicht Stable)

- Referenz: DateiFinder main `9cc035240ece8a32ffd0b53774754e77ade6d422`. Nur Layout-/Qualitätsprinzipien übertragen, kein CSS-Import, kein Tauri/Rust oder Tk.
- #22: zwei Mermaid-Diagramme und Design-Konfliktmatrix versioniert; `AGENTS.md`, TODO, README und Anforderungen ergänzt.
- #23: vier Farbschemata mit Whitelist/Persistenz, Kopfzeile und phasenbezogener Navigation; CI erfolgreich.
- #24: reproduzierbare Chrome/Chromium-Layoutkontrollen und Screenshot-Artefakte; CI erfolgreich.
- #25: 800px-/200%-Kopf kompakter, kurze Bedienbezeichnungen, Testdaten in Dropdowns und Prüfung auf abgeschnittenen Navigationstext. Auf PR-HEAD `013f3f54f0023320ba4538227c016424917ca61d` **100/100 Python-Tests + 20 Browserproben** erfolgreich; Main-Nachkontrolle nach Merge separat prüfen.
- **Noch offen vor letzter Kubuntu-Abnahme:** vollständige Kontrast-/Tastaturprüfung, optional einklappbare Details und Pixel-Referenzvergleich; Lizenz/Rechte und finale Release-SHA.
- **Weiterhin kein Stable.** Browser-Vortests verwenden CSS-Zoomsimulation, echte Kubuntu- und Nutzer-Sichtabnahme bleibt zuletzt.

## 02.11.2026 – Recherchegestützte UI-Komfortverbesserung (NI-20261102-01)

Recherche: Shutter Encoder (Renderliste/Status), HandBrake (Warteschlange/Format), Adobe Media Encoder (Auftrags-/Encodingtrennung), LosslessCut (kompakte Details), CapCut (Einstellungsstruktur). Quellen, Aufwands-/Konfliktmatrix und ausdrücklich ausgeschlossene Elemente in `docs/DESIGN_RECHERCHE_MEDIEN_UI_2026-11-02.md`.

Vorgesehene kleine UI-Anpassungen: fünf Auftragskacheln aus existierendem `GET /status`, lesbare Formatabmessungen, native aufklappbare Diagnose/Logs, Textwerte an drei Fortschrittsbalken und dezente Flächen. Keine Änderungen am Renderer oder der Archivierung. **Prüfstatus pro Patch anhand GitHub-Run und SHA aktualisieren; nicht mit Stable oder der persönlichen Kubuntu-Endabnahme verwechseln.**

## 02.11.2026 – Recherchebasierte UI-Ergänzung integriert (#28)

- Neue kompakte Statuskacheln für `BEREIT`, `WARTET`, `LAEUFT`, `ARCHIVIERT`, `PRUEFEN/ARCHIV_WARTET` ausschließlich aus bestehenden lokalen Statusdaten.
- Format-Hilfetext für fünf Formate, vier native `details`-Bereiche und drei lesbare Prozentwerte; Ordnerfelder auf kleinen Karten breiter.
- 108 Python-/Medien-/Negativtests und 20 Chromium-Layoutfälle auf PR-HEAD `db5f600963df2a57dd2a983bb541adbcd9ba3e8d` erfolgreich; alle Eingabefelder im Browser-Layout mindestens 333 Pixel breit.
- Integration nach `main` `ee3f9014a8ea8d2822c53a5c762db316738b6fe8`; [Main-CI #41364010012](https://github.com/provoware/Video-Zoom-Pro-2026/actions/runs/41364010012). Keine neue Runtime; Lizenzentscheidung und echte Kubuntu-Endabnahme **offen**.
