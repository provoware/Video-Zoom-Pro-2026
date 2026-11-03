# Sparsamer Eingangsscan · 04.11.2026

Gemessener Produktcode: `cfcf75ea56127b11cca56b51123993bae446da07`, lokal blob- und baumidentisch zu `e3715d53316ba164db9bd6c2636d764f39c0d2a5`. Python 3.12.14. Keine neuen Abhängigkeiten.

## Vergleich und Grenzen
Ein vorbereiteter synthetischer Song (WAV und PNG 128×96), zehn weitere Vorbereitungsrunden je Variante, vorab einmal vollständig vorbereitet. Variante Vollanalyse leert vor jeder Runde ausschließlich den Metadaten-Cache; Variante Cache verwendet unveränderte Pfad-/Größe-/mtime-/ctime-Signaturen. Zeit mit `time.perf_counter`, Median; Aufrufe mit `unittest.mock.patch(wraps=...)` gezählt. Testdaten aus `tests/fixtures/generieren.py`, temporäre Ordner, expliziter isolierter Testmodus, kein Produktionsrender.

| Messung | Erneute Vollanalyse | Unveränderter Eingang |
|---|---:|---:|
| Median je Scan | 63,217 ms | 0,142 ms |
| Vollständige Dauerprüfungen / 10 Runden | 10 | 0 |
| Vollständige Dateihashes / 10 Runden | 20 | 0 |

Das ist eine kleine lokale Scanmessung, kein Renderbenchmark und keine Messung der gesamten CPU-/RAM-Last. Entscheidend ist die vermiedene wiederholte Medienanalyse. Neue/geänderte Medien und jeder tatsächliche Renderstart behalten ihre vollständige Prüfung. Der Cache ist nur für diesen Workflow-Prozess gültig.

## Gewählte Strategie
- Keine dauernden Dateisystem-Watcher und keine neuen Hintergrunddienste. Ein eigener Worker und echte Schreibsperre bleiben Pflicht.
- Automatik verlängert unveränderte Scanrunden schrittweise bis max(60 Sekunden, eingestelltes Intervall), Änderungen setzen auf das eingestellte Intervall zurück. Bewusstes Eingang-Prüfen bleibt sofort möglich.
- Sensorwerte mindestens fünf Sekunden wiederverwenden; STATUS-Datei höchstens einmal pro Sekunde außer Phasenwechsel/Abschluss. Journaländerungen bleiben atomar und unmittelbar gespeichert.
- Browserstatus aktiv 1,5 Sekunden, ruhend 5 Sekunden, Hintergrund/Verbindungsfehler 15 Sekunden; höchstens eine Anfrage gleichzeitig.
- Vorschauen nur bewusst erzeugen, Videos nicht parallel ohne Ressourcenprüfung starten. Vorhandene systemd-CPU-/RAM-Grenzen bleiben unverändert Pflicht.
- Beim sicheren Beenden eigenen Worker und eigene Dateidialoge stoppen, Journal unter Sperre nachladen und sichern, dann nur den eigenen lokalen Server schließen. Fensterverlust hat Schonfrist für Neuladen und gedrosselte Hintergrundfenster.

Negativprüfungen: geändertes Quellmedium trotz Cache vor Render abgewiesen; Schutzstatus und Auswahl beim Fundlisten-Reset erhalten; Cache- und Statusbudget sowie verlängerte Scanpause mit Rückkehr nach Änderung getestet. Die größere Renderumstellung bleibt getrennt gemäß `RENDER_VERGLEICH_2026-11-03.md`; die vorhandene RAM-Messung allein rechtfertigt keine ungeprüfte Produktionsintegration.
