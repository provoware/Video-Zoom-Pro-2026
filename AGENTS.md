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
