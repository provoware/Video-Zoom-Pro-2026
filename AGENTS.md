# AGENTS.md – PROVOWARE Video Zoom Pro 2026

Verbindlicher Qualitäts- und Entwicklungsvertrag für das eigenständige, offline-fähige Linux-Werkzeug. VideoBatch ist kein Produktbestandteil. Erkenntnisse anderer Programme nur nach fachlicher Prüfung übernehmen. GUI ohne Tk. Keine Cloud, kein Tracking, kein selbstständiger Netzverkehr.

## Prioritäten
1. Datenintegrität, verständlicher Fehlerpfad und sichere Wiederaufnahme.
2. Nachgewiesen funktionsfähiger WAV/Bild/MP4-Ablauf, keine Scheinerfolge.
3. Laienfreundliche Oberfläche, größere Schrift, Tastatur, 800x600 bis 200 % Zoom.
4. Wartbarkeit, minimale Abhängigkeiten, unabhängige Module und klare Zuständigkeit.
5. Effiziente Renderzeit und schonender Umgang mit Systemressourcen.

## Verbindlicher Entwicklungsprozess
- Ziel prüfen: Nutzen und reale Wirkung vor dem Code nennen.
- Bestand prüfen: aktuellen HEAD, offene PRs/Issues, funktionierenden Code und Tests lesen.
- Alternativen prüfen: kleinste fachlich passende Änderung auswählen, keine unnötigen Abstraktionen.
- Wirkung prognostizieren: Nutzen, Fehler-/Abhängigkeits-/Datenrisiken benennen.
- Minimal implementieren: Änderungen auf einem eigenen Entwicklungszweig; main nicht blind ändern.
- Negativtests und Regression: Daten-, Ausgabe-, Fehler-, Start- und GUI-Verträge prüfen.
- Prognose mit tatsächlich gemessener Wirkung vergleichen; dokumentieren.
- Keine Tests als PASS melden, die nicht nachweislich auf dem exakten Commit liefen.
- Single Writer pro produktivem Bereich, keine konkurrierenden automatischen Mutationen.
- Geplante Aufgaben nicht still vergrößern; Neues als Next Queue für nächste Iteration festhalten.
- Bevorzugt höchstens 3 Produktdateien plus 1 Testdatei pro einzelnem Patch.
- Neue Module bevorzugt höchstens 400 Zeilen; größere Konstrukte schrittweise fachlich trennen.
- Vor einer neuen Abhängigkeit prüfen, ob Standardbibliothek oder bewährtes Systemprogramm genügt.

## Geschützte Daten
- Originalmedien werden zur Fehlerbehebung niemals verändert.
- WAV-Dateien lösen Aufträge erst nach vollständig abgeschlossener Kopie aus.
- Unklare Dateinamen oder Bildzuordnung dürfen keine fremden Downloads verschieben.
- Nur Bilder aus einem eindeutig zugeordneten Song-Projektordner für ein Video verwenden.
- Für jede Quell- und Ausgabedatei einen SHA-256-Fingerabdruck führen.
- Vor einem Rendern Quellhash und Gültigkeit erneut prüfen.
- Temporäre Dateien sind keine fertigen Videos; MP4 erst nach FFprobe-Bild-/Ton-/Dauerprüfung veröffentlichen.
- Fertige Ausgabe ohne Überschreiben und möglichst atomar veröffentlichen.
- Archivieren ausschließlich nach überprüfter MP4: Kopie schreiben, fsync, Hash prüfen, veröffentlichen und erst danach Quelle löschen.
- Archivdatei enthält _verwendet_; Log enthält Quelle, Ziel, Prüfsumme und Zeitpunkt.
- Ein unvollständiges Archiv wird bei Neustart fortgesetzt und löst keinen Doppelrender aus.
- Journal atomar schreiben, beschädigten Zustand nicht durch leeren Zustand überschreiben.
- Zweiter Prozess desselben Arbeitsordners darf nicht parallel schreiben.
- Bei echten Medien-/Datenfehlern betroffenen Auftrag sperren, übrige Aufträge fortsetzen.
- Temporäre Ausfälle, unvollständiger Download, fehlende Bilder und Systemlast lösen Warten/Pausieren statt globalem Abbruch aus.
- Korrekturversuche bleiben begrenzt und werden protokolliert.

## Technische Sicherheitsregeln
- Kein Tk, kein sudo als normaler Programmstart, kein shell=True, os.system, eval oder exec mit Benutzerdaten.
- Browser nur localhost 127.0.0.1, zufälliges Token, Host- und Origin-Prüfung, keine Fremdskripte.
- CPU-Ziel maximal 30 % der zugänglichen logischen Gesamtkapazität per systemd CPUQuota, gesondertes RAM-Limit.
- Ohne echten systemd-Benutzerscope keine Videoberechnung (fail closed); Vorbereitung bleibt erlaubt.
- GPU, Datenträger und Gesamtlast anderer Prozesse sind dadurch nicht pauschal auf 30 % begrenzt.
- Abhängigkeiten vor jedem Start erkennen; Paketreparatur nur nach apt-Simulation und ausdrücklicher Zustimmung.
- Installation blockieren, wenn vorhandene Pakete aktualisiert oder entfernt würden.
- Kein automatisches Update von systemd, keine ungeprüfte globale Python-Installation.
- Betrieb ohne Internet und ohne Benutzerkonto ermöglichen.

## Fachlicher Workflow
Eingang -> Vorbereitung -> Wartet/Bereit -> Stapel -> Rendervideo -> MP4-Prüfung -> Archiv-Wartet -> Archiviert.
- Vorbereitung und Stapel sind fachlich getrennt, separat start-/stoppbar, mit eigenen Fortschrittswerten.
- Eingang WAV, Titel vor sicher erkanntem URL-/Zeitstempelanhang.
- Herkunftsmarker chatgpt ist keine Kategorie; nur CODING, PROVOWARE, THEMA.
- Bildabmessungen und Auflösung separat als JSON, nicht als Pflichtdateiname.
- Erste Bildsequenz: alle Bilder rückwärts, schnell, ohne Zoom.
- Zweite Bildsequenz: vorwärts, sanfte Zoom-in/out- und Schwenkbewegungen, wechselnde Übergänge.
- Schonende Bildregie hält Schrift und wichtige Ränder sichtbar; keine aggressiven Blitze.
- Kürzel HOCH, BREI, QUAD, KLAS und 4K, identische Plattformabmessungen einmal berechnen.
- Kein künstliches 100 % vor abgeschlossener Videoprüfung und Archivquittung.
- Diagnosen an Anwender verständlich ausgeben: Was, Ursache, Korrektur, verbleibende Handlung, Protokollpfad.

## Tests und Abnahme
- Python-Code kompilieren, alle unittest-Tests und echte WAV-/PNG-/MP4-Medienprüfung ausführen.
- Pflichtnegativtests: beschädigte WAV, fehlendes Bild, unvollständige Kopie, Symlink, Pfad- und Dateikollision, defektes JSON-Journal, doppelter Start, Crash vor/nach MP4 und jeder Archivgrenze, fehlende systemd-Grenze, Upgrade-Simulation.
- Browser-Test: Token, Host, Origin, ungültiger POST, Tastaturbedienung.
- Laufzeitprüfungen: CPU, RAM, Speicher, vielteiliger Stapel, Wiederanlauf, fehlerhafter Einzelfall.
- Testdaten dürfen nur synthetische eigene Bilder und WAV oder bewusst kopierte Medien umfassen.
- CI-GRÜN ist nur Integrationsbeleg, nicht persönliche Stable-Freigabe.
- Finale echte Kubuntu-Abnahme: 800x600, 100/125/150/200 %, Tastatur, Browser, reales FFmpeg, Langzeitstapel und 30-%-Limit.
- Ungetestetes explizit OFFEN nennen. Lizenz- und Rechtefragen vor öffentlichem Release klären.

## Entwicklungsdokumentation
- Eine zentrale README, ARCHITEKTUR, SICHERHEIT, TESTPLAN, STATUS, TODO und CHANGELOG.
- Jeder Patch: geändert, geprüft auf exaktem SHA, offen, Risiko, nächste kleinste zulässige Aufgabe.
- To-do-Format: [ ] Datum | Bereich | Aufgabe | prüfen: Nachweis | fertig wenn: Kriterium.
- Recovery-Key muss Branch, HEAD, Ziel, letzten Befund und nächsten erlaubten Schritt enthalten.
- Kein Merge oder Stable-Release ohne erfolgreiche Pflichtkontrollen.

## Entwicklungsqualitaet und Aufgaben-Gates – Konsolidierung 2026-11-01
Dieser Zusatz übernimmt nur fachlich nachweislich passende Regeln aus TOOL_2026_Multi, PROVOWARE_VIDEO_AUTOMATION_2026 und PROVOWARE_DATEIFINDER. Keine fremden Laufzeitabhaengigkeiten oder Architekturzwang.

- **Kubuntu zuletzt:** Entwicklungs-PRs benoetigen passende automatisierte Tests, Medien-/GUI-/Datenvertragssimulationen und echten Main-CI-Nachweis. Erst nach abgeschlossenem Produktumfang, aktualisierten Dokumenten und einem eingefrorenen Releasekandidaten wird **einmal** die reale Gesamt-Kubuntu-Abnahme durchgefuehrt. Fehlende echte Belege bleiben OFFEN.
- **Befundstatus getrennt halten:** VERMUTET → REPRODUZIERT → BEHOBEN → GETESTET → IN MAIN; „Kubuntu bestaetigt“ ist eine eigenstaendige, spaetere Freigabe. Gruene CI ersetzt keine Zielsystemevidenz.
- **Beweis- und Herkunftskette:** Anforderungen-ID/Quelle → konkrete Fundstelle → Risiko/Nutzen-Prognose → kleinster Patch → reproduzierbarer Negativtest → exakter Commit/Prueflauf → Ergebnis → offener Rest. Bei fehlender Quelle keine erfundenen Erfolge.
- **Regression verantwortungsvoll:** neue Fehler erzeugen moeglichst einen dauerhaften Test; Unbekanntes verlangt Gesamtpruefung; kritische Schreiber-, Wiederanlauf- und Archivvertraege werden nie durch Optimierungen ausgeklammert.
- **Ein Schreiber, eingefrorener Arbeitsumfang:** vor jeder Mutation main/Branch/Head, laufende PRs und erlaubte Dateigrenzen kontrollieren. Ein Arbeitspaket hat ein Hauptziel; Nebenideen in die naechste Aufgabenliste statt still in den Patch.
- **Keine Fehlerverdeckung:** Keine endlosen Versuche, keine unbeschraenkten externen Befehle, keine unbelegten 100-Prozent-Anzeigen. Jeder relevante Endzustand meldet erfolgreich, pausiert, korrekturbedingt wartend oder Datenpruefung notwendig. Technische Hintergrunddetails duerfen im Log stehen; die Bedienoberflaeche erklaert in einfachem Deutsch „Was? Warum? Geschuetzt? Naechste Handlung?“.
- **Sichere Testumgebung:** belastende Tests, Datei-Manipulation und kuenstliche Abbrueche ausschliesslich mit synthetischen Daten in isolierten Testordnern. Keine echten Downloads oder persoenliche Dateien fuer CI verwenden.
- **Bedienung fuer Laien:** Standardaktionen mit grossen Schaltflaechen, deutlichem Fokus, sichtbarer aktueller Handlung, getrennten echten Fortschritten und einem naechsten sicheren Schritt. Nativer Ordnerdialog bevorzugt, Texteingabe als Fallback. Keine Erweiterung des Pakete-Stacks nur fuer Oberflaechenkosmetik.
- **Wiederaufnahme-Schluessel:** docs/STATUS.md enthaelt aktuellen main-HEAD, offenen Arbeitszweig/PR, letzten unveraenderten Testnachweis, zentrale Blocker, naechsten kleinen Arbeitsschritt und eindeutig den Status der finalen Kubuntu-Abnahme.
- **Freigaben:** Entwicklungs-CI/Integration, externe Rechte-/Lizenzentscheidung und finale Kubuntu-Endabnahme sind drei getrennte Schranken. Bei Konflikten verhindern Datenintegritaet und Quellschutz die Freigabe.

## Gepruefte Standards-Herkunft
- TOOL_2026_Multi AGENTS.md: letzte gemeinsame Kubuntu-Pruefung, kleine iterative Patches, strukturierte Fehlerberichte, kein PASS ohne Nachweis.
- PROVOWARE_VIDEO_AUTOMATION_2026 AGENTS.md: Quellschutz, produktive Fehlergrenzen, terminale Ereignisse und strenge Trennung von Entwicklung/Release.
- PROVOWARE_DATEIFINDER AGENTS.md: eine schreibende Instanz, SHA/Scope, automatisierte Negativtests und definierter Recovery-Key.

Nur die Prinzipien wurden uebernommen; **kein Codeimport**, keine Tk-Abhaengigkeit, keine VideoBatch-Kopplung.


## DateiFinder-Designtransfer – verbindlicher Zusatz (01.11.2026)

**Referenz:** `provoware/PROVOWARE_DATEIFINDER`, main `9cc035240ece8a32ffd0b53774754e77ade6d422`, insbesondere `index.html`, `src/styles.css`, `docs/VISUAL_REGRESSION.md` und das versionierte Referenzbild `dateifinder-768x512-chromium-linux.png`.

**Eigene Artefakte / Single Source of Truth:**
- `docs/DESIGN_TRANSFER_DATEIFINDER.md` – beobachtete Komponenten, Transferentscheidung, Konfliktmatrix, Abnahmekriterien.
- `docs/diagramme/01_einfacher_prozess.md` – fachlicher Ablauf mit Mermaid-Grafik.
- `docs/diagramme/02_funktionsfluss_technik.md` – konkrete Python-/FFmpeg-Übergänge und Datenparameter.
- `docs/TODO.md` – priorisierter Plan; Mermaid-Diagramme sind **abgeleitete Dokumentation**, der tatsächlich geprüfte Python-Code ist maßgebend.

**Transfer-Grenzen:**
- Nur eigene HTML/CSS/JavaScript-Muster übernehmen: konsistente Farbtokens und 4 Akzentfarben, Kontrast, Phasen-/Statusführung, sichtbarer Tastaturfokus, sichere scrollbare Detailbereiche, responsive Kacheln und deterministische Screenshot-Prüfungen.
- **Nicht kopieren:** Tauri, Rust, Node/npm, DateiFinder-Dateisuche, 159px-Zwangsseitenleiste, Mini-Schriftgrößen, Tauri-Fensterknöpfe, Code/Icons/Schriftdateien oder nicht freigegebene Fremdassets. Kein neues Paket ohne Nutzen-/Abhängigkeitsprüfung.
- Video Zoom Pro bleibt **Python-Standardbibliothek + FFmpeg + lokaler Browser**, ohne Tk/Cloud. Start-, Auftrags-, Render-, Archiv- und Netzwerkschutzverträge nicht durch Designarbeit verändern.
- Keine feste Zweispaltigkeit bei 800×600/200%; mindestens 44px große Primäraktionen, ausreichende Schrift, Tab-Fokus und Textstatus. Layout darf vertikal scrollen, nicht horizontal abschneiden.
- Eine sichtbare Gestaltung nur mit dokumentierter Pixel-/Layout-/Tastaturprüfung als fertig markieren. Lokale Quellcode-Screenshots sind **kein** Kubuntu-Endabnahmebeleg. Keine Referenzbilder stillschweigend „grün“ überschreiben.
- Designpatches strikt getrennt von Medien-/Archiv-Änderungen. Pro Patch Änderung → gezielte Browser- und Sicherheitsprüfung → volle CI → dokumentierte Wirkung / Risiko. Die abschließende reale Kubuntu-Abnahme wird **nicht vorgezogen**.

**Pflichtmatrix bei UI-Änderungen:** 800×600 bei 100%, 125%, 150%, 200%; 1280×720 Desktop; Cyan/Violett/Grün/Orange; Tastaturfokus, Lesbarkeit, kein horizontaler Überlauf, Status/Fehlertext, Begrenzung der lokalen API und Originalschutz. Fehlende manuelle Sichtprüfung bleibt explizit OFFEN.

## Qualitätsnachtrag: bewährte Regeln selektiv übernommen (01.11.2026)
Aus PROVOWARE/TOOL_2026_Multi: **ein Hauptziel je Patch**, eine feste Obergrenze für Wiederholungen, nachvollziehbare Ereignisgründe und nutzerverständliche Fehlerhinweise. Aus PROVOWARE_DATEIFINDER: **Frozen Current Plan**, kein zweiter schreibender Prozess, Prüfung auf exakt aktuellem SHA, sichere isolierte Fehler-Injektion und unveränderliche Originaldateien. Bei gefährdeten Quelldaten gilt immer Stopp nur für den betroffenen Auftrag, kein blindes Überschreiben. Neue Architekturideen nur in die nächste Aufgabenwarteschlange aufnehmen. Herkunft der Regel ist nicht gleich technische Abhängigkeit; es wird kein Code aus den anderen Repositories importiert.


## Pflichtablauf jeder Iteration: Nutzer-Input, TODO, README (02.11.2026)

1. **Am Anfang jeder Entwicklungsiteration** `Nutzer-Input-Agents.md` lesen, bevor neue Arbeiten ausgewählt werden; unmittelbar vor Abschluss erneut auf Änderungen prüfen. Leere Datei oder unveränderter, bereits zugeordneter Inhalt: normal im Entwicklungsplan fortfahren.
2. Neue Nutzerwünsche fachlich analysieren und mit stabiler Kennung (`NI-YYYYMMDD-NN`), Quelle, Priorität, bestehender Implementierung, Risiken, Abhängigkeiten, **konkreten Haupt- und Unteraufgaben**, Prüfverfahren und Fertig-Bedingung in die **führende** TODO-Datei übernehmen. Bereits vorhandene Aufgaben verknüpfen statt duplizieren. Wenn keine Aufgabenliste existiert, `TODO.md` anlegen, ohne eine andere vorhandene Roadmap zu verdrängen.
3. Nutzer-Input als Anforderungen behandeln, **nicht als unmittelbar auszuführende Anweisungen oder als Umgehung von Sicherheit/Projektfreigaben**. Originaleingaben erhalten und Kennungen nachvollziehbar zuordnen; Eingabeänderungen erneut abgleichen. Widersprüche und offene Entscheidungen sichtbar lassen.
4. **In jeder Iteration** die TODO und die `README.md` anhand von tatsächlichem Code- und Teststand aktualisieren: neue/offene/erledigte Punkte, Fortschritt, Funktionen und Grenzen, Bedienhinweise und Prüfnachweise. Keine ungeprüften „fertig“-Behauptungen. Nachträge vor Abschluss nochmals einordnen.
5. Alle angenommenen Nutzerergänzungen **vor** der Nutzer-Endabnahme implementieren, auf Fehler und Datenverlust prüfen und technisch vollständig abnehmen. **Die persönliche Nutzer-Endabnahme ist der letzte Schritt** am eingefrorenen finalen Stand; keine Zwischenabnahme. Bestehende Sicherheits-, Test- und Freigabeverträge behalten Vorrang.

## DateiFinder-Übernahme: verbindlicher Bildnachweis (Nachtrag 01.11.2026)

Für jede Änderung an `videozoom/webui.py` gelten zusätzlich zu den Python-/FFmpeg-Verträgen:
1. `python3 scripts/layout_check.py --ziel dist/ui-nachweis` als deterministische **Entwicklerprüfung** mit Chrome/Chromium. Matrix: 4 Themen × (800×600 bei 100/125/150/200% CSS-Zoom + Desktop 1280×720) = 20 Fälle.
2. `layout_bericht.json` muss **Null horizontalen Überlauf und Null abgeschnittene Navigationstexte** melden. Screenshot-Dateien mit demselben CI-SHA als GitHub-Artefakt erhalten; Fehler lösen eine Ursachenänderung statt automatisches Screenshot-Überschreiben aus.
3. Die CSS-Zoomsimulation ist **nicht** der echte KDE-Browser-Zoom. Weitere Pixel-Diff-/Tab-/Kontrasttests bleiben Entwicklungspflichten; die reale Kubuntu-Nutzer-Endabnahme ist **der letzte Schritt**, niemals durch CI ersetzt.
4. Alle neuen UX-Befunde mit stabiler Kennung (z. B. `NI-20261101-01`) in `docs/TODO.md` führen. `Nutzer-Input-Agents.md` vor jedem Patch und vor Abschluss lesen; parallele Änderungen an `AGENTS.md` oder Originaldateien nicht überschreiben.

## UI-Designrecherche: Medienwerkzeuge (NI-20261102-01)

**Verbindliche Herkunft:** `docs/DESIGN_RECHERCHE_MEDIEN_UI_2026-11-02.md`. Offizielle Quellen sind Shutter Encoder, HandBrake, Adobe Media Encoder, LosslessCut und CapCut. Übernommen werden **eigene** HTML/CSS/JS-Interaktionsmuster, niemals Lizenz-/Rechte-pflichtige Fremddateien, fremder Programmcode oder neue Runtimes.

**Invarianten für kosmetische Änderung:** `GET /status` bleibt alleinige Datenquelle der Auftragszahlen; die Kacheln müssen exakt vorhandene Statusschlüssel auswerten. Keine neuen FFmpeg-, Archiv-, Netzwerk- oder Sensoraufrufe. Progressanzeigen übernehmen nur bereits im Kern bestätigte Prozentwerte; nie eigenständig 100 % „berechnen“. Aufklappbare Diagnosen müssen per Tastatur bedienbar sein und weiterhin ihre vollständigen Texte bereitstellen. Neues Benutzerfeedback immer mit Tests und bei Browsergrößen 800×600/100–200 % prüfen.

**Abnahme:** Vor jedem Patch Nutzer-Input-Datei kontrollieren, TODO und README nachweisbasiert aktualisieren. Quell- und Medienregression plus Browsermatrix auf demselben SHA; keine neue externe Laufzeit. Alle echten Kubuntu-/Nutzer-Endprüfungen bleiben **zuletzt**.

## NI-20261102-01 – Prüfbelege und Status der Übernahme

- Abschluss der kleinen UI-Änderungen: PR #28, geprüfter HEAD `db5f600963df2a57dd2a983bb541adbcd9ba3e8d`, **108 Python-/Medientests und 20 Chromium-Layoutprüfungen**. Integration `ee3f9014a8ea8d2822c53a5c762db316738b6fe8`, Main-CI #41364010012 getrennt.
- Bei künftigem UI-Patch bleiben Browser-Screenshots und die echten `pfadfeldBreiten` verbindliche Layoutbelege. Werte unter 180 px in der Testmatrix = FAIL. Nicht mit realem KDE-/Native-Zoom gleichsetzen.
- Oberflächenkacheln dürfen WARTET/PRUEFEN/ARCHIV_WARTET nicht zu einem scheinbaren „FERTIG“ zusammenfassen. Medien-/Archivstatus bleiben allein unter Kontrolle des Workflows.

## NI-20261102-02 – Zeitbudgets für Fehlerprüfungen und hängende Aktionen

Der Standard `docs/PROVOWARE_TIMEOUT_STANDARD.md` ist für neue Entwicklungsarbeiten verbindlich. Die konkrete offene Runtime-Umsetzung steht in `docs/QUALITY_AUDIT_2026-11-02.md`. Warnzeit, fehlender echter Fortschritt und maximale Prüfzeit getrennt bewerten; nicht auf einen blockierenden FFmpeg-stdout-Read vertrauen. Nur eigene Kindprozesse kontrolliert stoppen, Originale erhalten, Fehler niemals zu PASS erklären. Bereits bestehende 15-Minuten-CI-Grenze und finale Kubuntu-Endabnahme unverändert.

## Issue #31 – Renderüberwachung
`videozoom/render_watchdog.py` hält beide Pipes nichtblockierend und begrenzt. Warnzeit 120 s, Stillstandsprüfung 300 s; steigende Medienzeit und CPU-Arbeit des eigenen Prozessbaums getrennt bewerten. Kein absolutes Renderlimit. Eigene Sitzung mit 5 s Aufräumfrist, danach gezieltem Kill/Wait. Benutzer-Stopp verbraucht keinen technischen Versuch. Modul bleibt ausdrücklich im ZIP-Manifest.
