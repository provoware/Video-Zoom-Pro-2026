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

## 01.11.2026 – letzter technischer Qualitätsschritt vor Lizenz/Kubuntu
- PR #19: Begrenzte Wiederholungen von Render- und Archivfehlern; automatische Eskalation statt Endlosschleifen. 86/86 GitHub-Tests auf PR erfolgreich.
- PR #20: Echtes Starten von STARTEN.sh --help/--doctor aus frisch entpacktem ZIP mit isolierten Benutzereinstellungen und Paket-Pfadschutz; 88/88 PR-Tests.
- Gemeinsamer Hauptzweig danach: `d486f30d2098777b59bc99330ddc3e5e1e2a884e`, [Main-CI](https://github.com/provoware/Video-Zoom-Pro-2026/actions/runs/41356578575) erfolgreich.
- Offen: Lizenz/Rechte, Release-SHA einfrieren, **zuletzt** echte Kubuntu-Abnahme. Kein Stable.

## 02.11.2026 – Moderne Medienoberflächen als eigenständiges UI-Muster

Recherchiert: Shutter Encoder, HandBrake, Adobe Media Encoder, LosslessCut und CapCut; Designmatrix in `docs/DESIGN_RECHERCHE_MEDIEN_UI_2026-11-02.md`. Visuelle Statuskacheln, Format-Hinweise, native Details und Fortschrittswerte ohne Backendänderung geplant/umgesetzt. Vollständige CI-Belege nach erfolgreicher PR-Integration ergänzen; Stable weiterhin nicht freigegeben.

## 02.11.2026 – Visuelle Komfortdetails übernommen (#28)

Fünf Live-Statuskacheln, kleine Formatübersicht, einklappbare Diagnose/Protokolle und tatsächliche Prozentangaben an drei Balken. Auftrags-, Render-, Archiv- und CPU-Verträge unverändert. Zusätzlich 800px-Pfadfelder verbreitert und 180px-Breiten-Gate ergänzt. PR-HEAD `db5f600963df2a57dd2a983bb541adbcd9ba3e8d`: 108 Tests plus 20 Chromium-Fälle bestanden; integrierter `main` `ee3f9014a8ea8d2822c53a5c762db316738b6fe8`. Kubuntu-Endabnahme zuletzt.

## 2026-11-02 – Issue #31
- FFmpeg-Ausgaben nichtblockierend und begrenzt lesen; Warnung/Stillstand mit monotoner Uhr und CPU-Nachweis.
- Eigene Prozesssitzung kontrolliert beenden; Teilvideo erhalten; Benutzer-Stopp ohne technischen Fehlversuch.
- Neun dauerhafte Negativ-/Regressionsfälle; ZIP-Liste um benötigtes Modul ergänzt.

## 2026-11-02 – Browser/Start nach Issue #31
- Browseraufrufe begrenzen, Statusabfragen serialisieren und veraltete Anzeigen sichtbar markieren; manuelle Dialoge mit eigenem Budget.
- Doctor-Exitcode entspricht Startbereitschaft; CI/ZIP prüfen diesen Vertrag ohne fehlende systemd-Benutzersitzung als Startbereitschaft auszugeben.
- Journal bei Oberflächenstart nur lesen, Datenfehler sichtbar erhalten. Acht ausführbare JavaScript-Verträge und vier Journaltests ergänzt.

## 2026-11-02 – Entwicklungsstrategie und Nachweiskette
- Führende TODO ohne konkurrierende historische Offen-/Aktuell-Aussagen; alten Wortlaut getrennt erhalten.
- Medien-/Prozessänderungen erzwingen volle Regression, Browser-/CLI-Testauswahl um fehlende Verträge ergänzt.
- CI sichert Python-/Medienbericht, JavaScript-Verträge und SHA-bezogene Layoutbelege gemeinsam.
