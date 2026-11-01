# Architektur

**Fachliche Phasen:** WAV-Erkennung -> Vorbereitung und Manifest -> Auftrag BEREIT -> Stapel -> Rückwärts/Zoom-Render -> MP4-Prüfung -> Archivierung -> ARCHIVIERT.

core.py enthält fachliche Verarbeitung, Journal, SHA-256, FFmpeg und Archiv. diagnose.py prüft Abhängigkeiten/Systemquoten. webui.py ist die lokale Tk-freie Browseroberfläche. __main__.py und STARTEN.sh sind die beiden Startwege.

Der Auftrag wird vor dem Rendern dauerhaft in PROTOKOLLE/auftraege.json gespeichert. Nach fertiger MP4 wird die Quellarchivierung fortgesetzt, ohne erneut zu rendern. Jede Ausgabe und Archivdatei wird ohne Überschreiben angelegt.

**Empfohlene spätere Trennung:** core.py nach Nachweis echter stabiler Medienproduktion fachlich in Auftragsjournal, Medienplanung, Render, Archiv und Sensorik aufteilen. Kein Großumbau nur wegen Dateigröße.

**VideoBatch bleibt unabhängig:** kein Codeimport, keine verpflichtende Kompatibilität oder Änderung an dessen Repository.

## Absturzfeste Renderveröffentlichung (01.11.2026)
- Vor der FFmpeg-Verarbeitung wird der exklusive geplante Ausgabepfad (`video_ziel`) atomar im Auftragsjournal gespeichert.
- Nach erfolgreicher Bild-/Ton-/Dauerprüfung wird der SHA-256-Fingerabdruck der vollständigen temporären MP4 (`render_hash`) gespeichert, **bevor** das Video durch eine kollisionssichere Hardlink-Veröffentlichung sichtbar wird.
- Wiederanlauf nach `LAEUFT` oder unterbrochener Veröffentlichung: Nur bei passendem Pfad, Fingerabdruck und FFprobe-Prüfung wird eine endgültige oder vollständig geprüfte temporäre MP4 übernommen; danach wird ausschließlich archiviert. Bei unbekanntem Ausgabepfad oder veränderter Datei gilt `PRUEFEN`, kein blinder Doppelrender.
- Während der Berechnung abgebrochene temporäre Dateien werden eindeutig als `.abbruch-N` gesichert und niemals zur fertigen MP4 erklärt.
- Bestehende Status `FERTIG` und `ARCHIV_WARTET` bleiben vom Renderer getrennt. Einzeldefekte lassen andere Aufträge weiterlaufen.
- Die Reparatur ist ein begrenzter, lokaler Mechanismus; die reale Absturz-Endabnahme auf Kubuntu bleibt offen.
