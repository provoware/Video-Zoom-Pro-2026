# Moderne Medienoberflächen – unabhängige Gestaltungsrecherche

**Stand:** 02.11.2026  
**Arbeitsauftrag:** NI-20261102-01 · Video Zoom Pro, nicht VideoBatch.  
**Quellcode-Ausgangsstand:** `94b09a1e327367c5a9de83549d284e9efc89547c`  
**Prüfregel:** Nur funktional relevante **Gestaltungsprinzipien** übernehmen. Keine Logos, Screenshots, Quellcode, Bibliotheken oder fremden Assets einbetten. Die Screenshots der Vorbilder dienen ausschließlich zur Analyse.

## Quellen und Erkenntnisse

| Werkzeug | Beobachteter Nutzen | Originalquelle | Bewertung |
|---|---|---|---|
| Shutter Encoder | Funktionseinstellungen, Renderwarteschlange, Speicherorte und Hinweise sind getrennt; Fortschrittsstatus steht sichtbar am Prozess. | https://www.shutterencoder.com/ und https://www.shutterencoder.com/documentation/ | **A – Direkt übernehmen:** Zusammenfassung wichtiger Informationen und ruhigere technische Details. |
| HandBrake | Klar erkennbarer Auftragsstatus und Presetauswahl, ohne dass jeder Benutzer die Codecdetails verstehen muss. | https://handbrake.fr/docs/en/1.10.0/advanced/queue.html und https://github.com/HandBrake/HandBrake-docs/blob/master/source/docs/en/latest/technical/official-presets.markdown | **A – Direkt übernehmen:** Statuszahlen, lesbare Format-Zusammenfassung. |
| Adobe Media Encoder | Aufträge, Einstellungen und laufende Verarbeitung werden als getrennte Oberflächenbereiche behandelt. | https://helpx.adobe.com/sg/media-encoder/desktop/encoding-quick-start-and-basics/overview-media-encoder-user-interface.html | **A – Direkt übernehmen:** Fortschrittswerte klar neben den drei Balken; Warteschlange separat. |
| LosslessCut | Dunkle ruhige Oberfläche und kompakte Bedienbereiche; fortgeschrittene Funktionen bleiben auffindbar. | https://github.com/mifi/lossless-cut und https://losslesscut.app/docs/features | **B – Inspiriert übernehmen:** kompakte Karten, technische Details standardmäßig zugeklappt. |
| CapCut | Anpassbare Oberfläche, klar strukturierte Einstellungen und Hilfen. | https://www.capcut.com/help/interface-and-settings | **C – Für später:** nutzerdefinierte Paneelgrößen nur mit echtem Bedarf; vorerst keine komplexe Layoutmaschine. |

## Niedriges Risiko, hoher Nutzen: tatsächliche Implementierung

1. **Fünf kleine Zustandskacheln** oberhalb der beiden Workflows: BEREIT, WARTET, LAEUFT, ARCHIVIERT und PRUEFEN/ARCHIV_WARTET. Die Werte kommen **ausschließlich** aus dem vorhandenen `GET /status`; kein Dateizugriff und keine zusätzliche Backend-API. Null heißt: keine Aufträge mit diesem Status. Bei API-Fehlern bleibt die Fehlermeldung sichtbar, es wird nichts erfunden.
2. **Formatbeschreibung unter dem vorhandenen Auswahlfeld:** BREI, HOCH, QUAD, KLAS und 4K mit echten Abmessungen und Zweck; kein neues Preset und keine Änderung der Videoerstellung.
3. **Diagnose, Sensordaten und beide Protokollansichten** in native `<details><summary>`-Elemente verlagert. Das hält die Startansicht lesbarer; Texte bleiben weiterhin im DOM und über Tastatur erreichbar. Die Systemprüfung kann unabhängig vom aufklappbaren Detail gestartet werden.
4. **Fortschritt mit Zahl direkt am Balken:** Die drei unabhängigen Prozentwerte stammen weiterhin vom vorhandenen Backend. Bei fehlenden/ungültigen Werten wird kein erfundener Fortschritt angezeigt. Die 100%-Sicherheitsregel bleibt allein im Kern.
5. **Zurückhaltende Optik:** leichte Flächenabstufungen, lesbarer Kontrast, dezente Hervorhebung von Erfolg/Warnung, keine Laufzeitabhängigkeit, keine externe Schrift. Vier bestehende Themes bleiben unverändert.

## Ausgeschlossene Ideen

- Schnitt-Timeline, Wellenform-Editor, Drag-and-drop-Layer, Miniplayer, Neuaufteilung von WAV-/FFmpeg-Verarbeitung: **hoher Aufwand, nicht erforderlich**.
- Individuelle Auftragsvorschaubilder: ohne gesicherte lokale Vorschauquelle und sicheren Medienpfad entstehen neue Risiken; vorerst nicht sinnvoll.
- Tauri, React, Electron, umfangreiche Icon-Pakete, Cloud-Bibliotheken oder fremde CSS-Dateien: **keine neue Abhängigkeit**.
- Dekorative Pseudo-Prozentzahlen, frei erfundene Restzeiten und grüne Erfolgsmeldungen ohne echte Prüfung: **ausgeschlossen**.

## Verifikation, Konfliktprüfung und spätere Abnahme

- HTML-Markup und dynamische Werte: `tests/test_ui_polish.py` mit sechs Struktur-/Negativtests.
- Vollständige bestehende Python-/FFmpeg-/Wiederanlauftests + 20 Chromium-Layouteinstellungen auf exakt geprüftem Commit. Bei Fehlern in Chrome-Fixture nicht blind übergehen.
- Backend unberührt: Auftragsjournal, Sensoren, HTTP-Tokens, Laufzeitlimits und Dateischreibschutz bleiben funktional gleich.
- Die tatsächliche 200%-Browser-Zoom-/Tab-/Kubuntu-Abnahme **bleibt die letzte persönliche Abnahme**.
- Die Recherche ist eine **Quellenanalyse**, keine Aussage, dass fremde Apps mit unseren Benutzerdaten verbunden wurden.
