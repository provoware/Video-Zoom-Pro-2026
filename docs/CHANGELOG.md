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

## 2026-11-02 – DATA-01
- Vollständige WAV-Containerblöcke einschließlich RF64 vor Vorbereitung prüfen; Teilkopie oder laufende Änderung wartet statt Render/Fehlversuch.
- Fünf neue Negative/Wiederanlaufprüfungen; Modul ausdrücklich im Offline-ZIP.

## 2026-11-02 – DATA-02
- Konservativen Render-/faststart-/Archivbedarf und freie Reserve vor großen Schreibvorgängen prüfen.
- Gesamtes Archiv vor erster Quellbewegung prüfen; gültige vorhandene Kopien weiterverwenden.
- Speicherknappheit pausiert ohne technischen Versuch; unabhängige Aufträge bleiben bearbeitbar.

## 2026-11-02 – Einrichtung und echte Fortschrittswerte
- Einrichtungsfolge, Ordner-/Zugriffs-/Versionsprüfung und klare nächste Handlung ohne Dateianlage.
- Unbekannter Fortschritt als unbestimmt statt erfundener Null; technische Einzelheiten bleiben vollständig.
- Vier neue Pythonfälle und zwei zusätzliche ausgeführte JavaScript-Verträge; Auswahlregeln nachgeführt.

## 2026-11-02 – Integration und sichere Bedienwerte
- #34–#37 der Reihe nach mit jeweils erfolgreicher Main-Gesamtprüfung übernommen.
- Gruppenweise Einstellungsrücksetzung mit exakter Original-Sicherung und wiederaufnehmbarer, fingerabdruckgeprüfter Rücknahme; Medien/Pfade/Ressourcen bleiben erhalten.
- Farbschema während laufender Verarbeitung speicherbar; Renderparameter bleiben gesperrt und Worker-Konfiguration unverändert.
- Neun neue Pythonprüfungen und zwei zusätzliche JavaScript-Verträge; Modul im Offline-ZIP.

## 2026-11-02 – echte Browser-Bedienungsprüfung
- Isolierten Chromium-Test ohne neue Pakete ergänzt: echte Tab-/Leertasten, Fokusreihenfolge, Text-/Fokus-/disabled-/Hover-Kontrast in 20 Fällen.
- SHA-bezogenen JSON-Nachweis in bestehendes CI-Artefakt aufnehmen; fehlende Pixel-/Kubuntu-Abnahme ausdrücklich offen.

## 2026-11-02 – zweite Oberfläche als Nur-Leser
- Aktive fremde Kern-Sperre ohne Anlage/Löschung prüfen; frischen Journalstand und eindeutigen Fensterhinweis anzeigen.
- Fremde Start-/Stopp-/Einstellungs-/Rücksetzversuche abweisen, keine erfundenen fremden Prozentwerte.
- Sechs neue Pythonfälle, ein weiterer JavaScript-Vertrag und lange Statusmeldung in der echten Browsermatrix.

## 2026-11-02 – Abschlussnachweis der Integrations- und Bedienpakete
- #34–#40 mit getrennten Quell-/Test-Merge-/Main-Nachweisen dokumentiert.
- TODO trennt erledigte automatisierte Tastatur-/Kontrastprüfungen von offener Pixel-/Zielsystemfreigabe.
- Gemeinsamer geprüfter Produktumfang: 151 Python-/Medientests, 13 Chromium-Verträge sowie je 20 Tastatur-/Kontrast- und Layoutfälle.

## 0.9.0-dev · 03.11.2026 – NI-20261103-01
- A01: nach erfolgreicher Schreibsperre aktuelles Journal laden; fehlerhaften Stand nicht ersetzen.
- A02: manuelle Prüfsperre durch Vorbereitung erhalten, Versuchsgrenze vor jedem Start prüfen.
- A03: neue vollständige Audioinhalte am archivierten Dateipfad als eigene Revision aufnehmen; Historie und identische Inhalte erhalten.
- A04: Auflösung, Bildrate, beide Spurdauern und vollständiges Decodieren prüfen; Originalschutz und Ressourcenhülle erhalten.
- Kurze echte Vorschau mit unverändertem Produktionsstatus und Quellbestand; sichere lokale Teilabrufe.
- Kompakte Songliste mit Einzel-Freigabe, verständlicher Rückmeldung und Erhalt von Details/Fokus/Wiedergabe beim Polling.
- Reproduzierbare Entwickler-Vergleichsmessung, einschließlich getrenntem Phasenprototyp; keine ungeprüfte Umschaltung des Produktpfads.
- Gemeinsame finale SHA-/CI-/Browser-/ZIP-Nachweise stehen im PR; echte Kubuntu-Abnahme bleibt zuletzt offen.

## 0.9.1-dev · Integrationsabschluss
- PR #42 regulär in main übernommen.
- Vollständige erneute Videoprüfung vor manueller Freigabe einer Archivierung; alte Hashnachweise ersetzen keine gültige MP4.
- Bewusste Einzelvorbereitung rettet anfänglich fehlgeschlagene Aufträge ohne Manifest; kein automatisches Umgehen der Prüfsperre.
- Unveränderte Quellen behalten ihre Vorschauzuordnung; geänderte Medien invalidieren sie ohne ungeprüftes Löschen alter Vorschauen.
- Vier dauerhafte Integrationsproben, Main-Nachkontrolle separat; kein Stable-Release.

Integrationsnachweis 0.9.1-dev: Produkt-main 771891f, Main-CI #41736344529 vollständig erfolgreich (173 Python-/Medientests, 16 Chromium-Verträge, je 20 Tastatur-/Kontrast- und Layoutfälle). Alle vier vorhandenen Reviewhinweise aufgelöst. Abschließender Dokumentationsnachtrag ohne Produktänderung wird separat nachgeprüft.
