# Fachliche Anforderungen

- WAV-Datei im Downloads-Ordner als eindeutiger Trigger; Teildownload abwarten.
- Titelwörter vor URL/Provider/Zeitstempel erhalten und Sonderzeichen schonend entfernen.
- Bilder nur über eindeutigen Song-Projektordner zuordnen.
- Bildmarker ChatGPT und PROVOWARE gemeinsam als Herkunft plus Kategorie erkennen; außerdem CODING und THEMA.
- Bilder erhalten technische Angaben (Breite, Höhe, Qualität/Format) als Zusatzdaten, nicht als zwingenden Dateinamen.
- Erste Runde rückwärts, schnell, ohne Zoom. Zweite Runde vorwärts, sanft wechselnder Zoom und Schwenk.
- WAV-Länge steuert die gesamte Bildzeit. Konservative Bewegungen schützen Schrift und Bildränder.
- HOCH, BREI, QUAD, KLAS und 4K, gleiche Plattformformate nur einmal berechnen.
- Separate Workflows Song vorbereiten und Stapel verarbeiten; automatische Ordnerüberwachung optional.
- Speicherbare Warteschlange, transparente Fortschritte, intelligente Korrektur begrenzter technischer Fehler.
- Nur tatsächliche Datenfehler sperren betroffenen Auftrag; andere Probleme warten oder werden sicher gelöst.
- Nach MP4-Prüfung Quellen mit _verwendet_ archivieren, Hash, Quelle/Ziel und Zeitpunkt bestätigen.
- CPU-Ziel 30 % der zugänglichen Gesamtkapazität via systemd-CPUQuota; RAM separat.
- Startprüfung und sichere Paket-Simulation, keine Installationen ohne Benutzerzustimmung.
- Offline und Tk-frei, laienfreundliche große UI bei 800x600 und Zoom.

## Neues Anforderungsprofil – Designtransfer aus DateiFinder (01.11.2026)
- Dunkles, eigenständiges Design mit vier wählbaren Akzentfarben (Cyan, Violett, Grün, Orange) und dauerhaft gespeicherter Auswahl.
- Klare Gliederung in Songs vorbereiten, Stapelverarbeitung, Diagnose und Protokoll; wesentliche Aktionen ohne Suchen erreichbar.
- Für 800×600 und 100–200% Anzeige keine horizontal abgeschnittenen Eingaben oder Schaltflächen; vertikal scrollbare, große Bedienelemente.
- Status immer in verständlichem Text zusätzlich zu Farben; gut sichtbarer Tastaturfokus, klare Stopp- und Fehlerfunktionen.
- Reduzierte Animationen; keine Ablenkung bei laufenden Renderaufträgen.
- Bildprüfung mit reproduzierbaren Browserreferenzen und kontrollierten Änderungen; letzte Kubuntu-Sichtabnahme nicht vorziehen.
- Übertragene Designregeln nur aus eigenem CSS/HTML, keine DateiFinder-Runtime, kein Qt/Tk/Tauri-/Rust-Import.
