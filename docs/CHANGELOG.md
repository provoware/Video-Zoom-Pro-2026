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
