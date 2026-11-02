# Technisches Qualitäts-Audit – 02.11.2026

**Referenz:** main c2ab5f51673c6912c68601db2510f4d832fb3065. **Status:** Quellcodebefunde und Empfehlungen, keine durchgeführte Kubuntu-Endabnahme. NI-20261102-02.

## Priorisierte Befunde

1. **P0 Render-Watchdog fehlt:** `Workflow._render` liest blockierend `proc.stdout`; die nachfolgende `communicate(timeout=...)`-Grenze greift nicht, solange die Ausgabe offen bleibt und keine Zeilen kommen. Negativtest mit stillstehendem Kindprozess; Fortschritts-Wächter mit monotoner Uhr und sicherem Prozessabschluss ergänzen.
2. **P1 Browseraufrufe ohne Deadline:** In `webui.HTML` verwendet `api()` unbeschränktes `fetch`; `setInterval(status,1500)` kann parallele Statusabfragen starten. AbortController mit 10-Sekunden-Budget und nur ein laufender Statusaufruf.
3. **P1 Falsche Exitcodes:** `__main__.main(--doctor)` gibt auch bei `startbereit=false` 0 zurück. Fehlende Systemabhängigkeiten müssen zu Exitcode ungleich 0 führen; Negativtest.
4. **P1 Unvollständige Startanzeige:** `Bedienung.status()` zeigt ohne neues `Workflow`-Objekt zunächst leere Aufträge an, obwohl ein gespeichertes Journal existieren kann. Geschütztes Nur-Lesen zu Beginn.
5. **P1 Benutzer-Stopp:** Der technische Render-Fehlerpfad erhöht `versuche` vor dem Start; ein bewusster Stopp darf nicht wiederholte technische Fehler vortäuschen oder Quellmedien verlieren.
6. **P1 Fertiger Download nicht verlässlich erkannt:** `stabil()` prüft nur Größe >100 B und eine letzte Änderungszeit über fünf Sekunden. Angehaltene, aber unvollständige Übertragungen separat kennzeichnen.
7. **P1 Kein Platzbedarf vor Render:** Sensoren lesen freien Speicher, doch die Eingangs- und Ausgabereserve wird nicht als Pflichtprüfung genutzt. Konservativen Platzbedarf vor großen MP4-/Archivvorgängen prüfen.
8. **P2 Erststart:** `STARTEN.sh` prüft Python, aber kein geführter Einrichtungsassistent führt durch Ordner, FFmpeg-Filter, Zugriffsrechte und systemd-Grenzen.
9. **P2 Diagnose verständlicher machen:** Roh-JSON durch Klartext-Ampel, Ursache und sichere Handlung ergänzen; technische Details aufklappbar behalten.
10. **P2 Fehlermeldung sichtbar halten:** Browser meldet bei API-Ausfall den Fehler im Status, alte Auftragskacheln bleiben jedoch eventuell stehen. Stale-Daten erkennbar machen.
11. **P2 Unbekannter Fortschritt:** Fehlender Prozentwert wird aktuell zu 0 statt „noch unbekannt“. Das visuell unterscheiden.
12. **P2 Einstellungen:** Während der Verarbeitung werden auch rein optische Änderungen blockiert. Farbschema und Medienkonfiguration getrennt speichern.
13. **P2 Wartbarkeit:** `webui.py` enthält HTML, CSS, JavaScript, HTTP-Handler und Threadverwaltung zusammen. Bei echten Wartungsproblemen gezielt lokal aufteilen, ohne neue Laufzeitbibliothek.
14. **P2 Schema/Migration:** Konfiguration und Journalversionen mit testbaren Vorwärts-/Rückwärtsregeln versehen, Original vor Migration sichern.
15. **P2 Zugriffsschutz:** Lokales Token in der URL und `unsafe-inline` in Content-Security-Policy überprüfen; keine externen Dienste, keine Token in Export-/Fehlerlogs.
16. **P2 Zwei Instanzen:** Arbeit wird über `dienst.lock` geschützt, doch getrennt gestartete Browseroberflächen können unterschiedliche Anzeigen liefern. Klaren Eininstanzhinweis anbieten.
17. **P2 Starterreparatur:** Bereits simulierte Installation mit Zustimmung beibehalten; zusätzlich Versions-/Abhängigkeitsbericht und verständliche Rücksetzoption anbieten.
18. **P2 Tastatur und Bildvergleich:** 20 Chromium-CSS-Zoomtests sind keine echte Tab-/Fokus- und Pixel-Differenzprüfung. Diese vor der letzten Kubuntu-Endabnahme vervollständigen.
19. **P3 Erscheinungsbild:** einheitliche Kartenhöhen, ruhige Leerzustände, bessere Auftragsliste, lesbare Statusinformationen statt Rohdaten und klarere Hierarchie ohne Animationsexzesse.
20. **P3 Erweiterbarkeit:** Formate, Zustandsnamen und Aktionen maschinenlesbar dokumentieren; Schnittstellen zwischen Vorbereitung und Stapel beibehalten, keine Kopplung an VideoBatch.

## Umsetzung vor Kubuntu

- **Gate 1:** Punkte 1–7 korrigieren und mit Negativ-/Wiederanlauftests prüfen.
- **Gate 2:** Punkte 8–12 und 17 verbessern, besonders Erststart und Störungsfeedback.
- **Gate 3:** Punkte 13–16 und 18–20 nur nach Nutzen-/Abhängigkeitsanalyse umsetzen; vollständige UI-/Medienregression.
- **Gate 4:** Lizenz, Release-Manifest und SHA absichern.
- **Letzter Schritt:** echte Kubuntu-/Nutzer-Endabnahme.

**Wichtig:** Ein dokumentierter Timeoutvertrag ist keine fertig implementierte technische Prozessüberwachung. Keine Stable-Freigabe durch diesen Audit.
