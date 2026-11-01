# Architektur

**Fachliche Phasen:** WAV-Erkennung -> Vorbereitung und Manifest -> Auftrag BEREIT -> Stapel -> Rückwärts/Zoom-Render -> MP4-Prüfung -> Archivierung -> ARCHIVIERT.

core.py enthält fachliche Verarbeitung, Journal, SHA-256, FFmpeg und Archiv. diagnose.py prüft Abhängigkeiten/Systemquoten. webui.py ist die lokale Tk-freie Browseroberfläche. __main__.py und STARTEN.sh sind die beiden Startwege.

Der Auftrag wird vor dem Rendern dauerhaft in PROTOKOLLE/auftraege.json gespeichert. Nach fertiger MP4 wird die Quellarchivierung fortgesetzt, ohne erneut zu rendern. Jede Ausgabe und Archivdatei wird ohne Überschreiben angelegt.

**Empfohlene spätere Trennung:** core.py nach Nachweis echter stabiler Medienproduktion fachlich in Auftragsjournal, Medienplanung, Render, Archiv und Sensorik aufteilen. Kein Großumbau nur wegen Dateigröße.

**VideoBatch bleibt unabhängig:** kein Codeimport, keine verpflichtende Kompatibilität oder Änderung an dessen Repository.
