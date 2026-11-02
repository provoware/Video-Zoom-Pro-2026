# Entwicklung: Wirkung vor Umfang – NI-20261102-03

## Feste Reihenfolge und kleine Pakete
1. Issue #31 isoliert implementieren, Negativ- und Gesamttests ausführen.
2. Danach Browser-/Startkorrekturen mit eigener Prüfspur.
3. Danach Datenvollständigkeit und Speicherreserve, anschließend Bedienung und begründete Architekturarbeit.

Ein Schreiber und ein Hauptziel je Paket. Vor Mutation aktuelle Basis/Branch/HEAD, PRs und Nutzer-Input prüfen. Neue Ideen ergänzen die führende TODO, sie vergrößern den aktuellen Patch nicht. Ein Paket beginnt mit Fundstelle, Fehlerreproduktion, prognostizierter Wirkung, Quell-/Abhängigkeitsrisiko und Fertig-Kriterium. Abschluss: gemessene Wirkung gegen Prognose und offener Rest.

## Effiziente, belastbare Prüfungen
- Während Umsetzung nur passende Negative, danach einmal vollständig am eingefrorenen Commit. Nach Änderungen nur betroffene Gate-Wiederholung; ein neuer endgültiger Stand benötigt wieder die vollständige Freigabe.
- Änderungen an Medien-/Archiv-/Prozessgrenzen (`core.py`, `render_watchdog.py`) erzwingen im Selektor die Gesamtprüfung. Diese Kopplung ist zu kritisch für eine leicht veraltende Teiltestliste.
- Oberflächenänderungen wählen auch Startjournal, Themen, Darstellung und Fortschritt aus. CLI-Änderungen wählen Einstellungs- und entpackte ZIP-Tests aus. Unbekannter Einfluss bleibt Gesamtprüfung.
- Pythonbericht ist keine Browserfreigabe. CI führt ausgeführte JavaScript-Verträge und 20 Chromium-Layoutfälle getrennt aus und sichert beide JSON-Berichte zusammen mit Medienbericht und Screenshots. SHA/Umfang bleiben sichtbar.
- Kurze Tests haben äußere Budgets; Renderprozesse bewerten echte Medienzeit und Aktivität. Keine Wiederholung grüner unveränderter Prüfungen ohne konkreten Grund. Keine Aufweichung von Testbedingungen.

## Nutzenvergleich
Prognose: weniger doppelte/überholte TODO-Punkte, keine ausgelassenen neuen Renderer-/Starttests im Selektor, bessere Zuordnung der Nachweise zum getesteten Commit; keine neue Produktruntime.
Messung: Selektornegative, vollständige Regression und CI-Berichte; ältere Aufgabenliste separat als Historie erhalten. Tatsächliche Entwicklungszeitverkürzung ist noch nicht gemessen und wird nicht behauptet.

## Getrennte Schranken
BEHOBEN ≠ GETESTET ≠ IN MAIN ≠ KUBUNTU BESTÄTIGT. PR-HEAD und GitHub-Test-Merge sind getrennte SHA. Rechteentscheidung, eingefrorener Kandidat und reale Kubuntu-Endabnahme bleiben letzte eigene Schritte.
