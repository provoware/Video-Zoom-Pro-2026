# Changelog

## 0.8.0-dev – 01.11.2026
- Neues unabhängiges Repository und Tk-freie lokale Bedienoberfläche.
- WAV-Vorbereitung getrennt von Stapel, zweistufige Bildregie, Quotenbegrenzung.
- Journal, verifizierte Archivierung, synthetische Testdaten, GitHub CI.
- Entwicklung, noch keine Stable-Freigabe.

## Nachtrag 01.11.2026 – Archivkopie unterbrechungssicher
- Unterbrochene Archiv-Zwischenkopien werden erkannt. Bereits vollständig kopierte Dateien werden nach SHA-256-Prüfung wiederverwendet.
- Fehlerhafte Teilkopien erhalten einen kollisionssicheren Sicherungsnamen statt einen unbemerkten Überschreibversuch.
- Nach Absturz zwischen Archiv-Veröffentlichung und Aufräumen werden nur verifizierte identische Zwischenkopien entfernt.
- Sieben gezielte Negativ-/Wiederanlauftests zu Teilkopien, fsync-Fehler, Symlink, Zielkonflikt und wiederholtem Aufruf.
- Offene Risiken: echter Stromausfall, externe Dateisystemmanipulation, reale Kubuntu-Abnahme. Keine Stable-Freigabe.

## Vor-Kubuntu-Qualitaetsrunde – 01.11.2026
- #10: Drei getrennte Fortschritte; 100% erst nach gesicherter Archivierung.
- #14 (enthält #12/#13): Widerspruechliche Bildmarker geschützt, CPU-/RAM-Grenzen der tatsächlichen Benutzerkonfiguration, sichere Quellpfade, idempotente Archivquittungen, 20 Songs mit 60 Archivbelegen.
- #15: reproduzierbares Entwicklungskandidaten-ZIP, SHA-256-Manifest, sichere Ausgaberegeln; kein Stable-Release.
- #16: CLI-Diagnose prueft tatsächliche Einstellungen; grafische Installationsdialoge mit Zeitgrenze.
- Gemeinsamer Main-Commit `c1f67a460e17eaa11ab88999582a05a3d9399e44` bestand **82/82** Tests (Actions #41354636904).
- Offen vor Kubuntu: verbleibende Fehlerklassifikations-/Bereitstellungsdetails, Lizenzentscheidung, Synchronisierung der Dokumentation. Kubuntu-Abnahme **zuletzt**.
