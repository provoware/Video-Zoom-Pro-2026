# Scanwahl abschließend gegen doppelte Speicherung gesichert

Zwei schnelle Schalteränderungen dürfen keine überholenden Speicheranfragen erzeugen. Während der Scanwahl-Speicherung sind beide Schalter synchron gesperrt; ein zweiter Aufruf startet keine weitere Anfrage. Ein zusätzlicher ausgeführter JavaScript-Vertrag prüft dies. Neuer Vertragsumfang: 21. Der tatsächliche finale Main-SHA und dessen vollständige CI werden im Abschlussbericht genannt. Historische Nachweise unten behalten ihre damaligen Zählstände.

# Main-Integration abgeschlossen · 0.10.0-dev

Main `e911159d86050d3e230791a1924c2ab0a073bbd9`, Main-CI #41743438515 erfolgreich: vollständige Funktions-/Medienregression und Chromium-Prüfung. PR #43 ist geschlossen und als integriert erfasst, ohne Bereitschaltung und ohne Codex-Review-Auftrag. Paketprobe mit 20 Programmdateien erfolgreich; keine Benutzermedien im ZIP.

Letzter kleiner Abschlussnachtrag: übergeordnete `..`-Pfadschritte dürfen die Ordnergrenze nicht umgehen. Konfiguration und Medien-/Ordnerprüfung weisen solche Pfade vor Dateianlage verständlich ab. Ein neuer Negativtest belegt die Grenze. Die vorherigen 192 Funktionstests werden damit um einen Fall erweitert. Der neue Main-Abschlusscommit wird nochmals vollständig nachgeprüft; tatsächlicher SHA und CI-Link stehen in der Abschlussmeldung und im mitgelieferten Bericht.

Die zentralen Bedienungen und alle Anforderungen aus NI-20261104-01 sind umgesetzt. Größere Renderumstellung und echte Kubuntu-Endabnahme bleiben eigenständige spätere Gates. Kein Stable. Details und ältere Nachweise unten.

---

# Scanwahl, Ordner und sicherer Abschluss · 0.10.0-dev

Nutzerauftrag NI-20261104-01 umgesetzt auf eigenem Zweig `feat/scan-reset-safe-exit`, ein Schreiber. Geprüfter Produktstand: `cfcf75ea56127b11cca56b51123993bae446da07`. PR #43 bleibt für die Vorabprüfung ein Entwurf; kein Codex-Review angefordert.

CI #41743045748 erfolgreich auf Test-Merge `f879895eb24926838912963b22c738abf3e59014`: 192 Python-/Medientests ohne Auslassung, 20 echte Chromium-Verträge, je 20 Tastatur-/Kontrast- und Layoutfälle. 37 natürliche Tab-Stopps, Mindesttextkontrast 7,127:1, kein horizontaler/Textüberlauf. CI-Artefakt 13282042811 ausgewertet; Hauptoberfläche/Desktop und offene Songliste bei 200 % visuell geprüft. CSS-Zoomsimulation ersetzt keine KDE-Endabnahme.

Implementiert: gesicherter Fundlisten-Neuaufbau ohne Verlust bearbeiteter Aufträge, getrennte Auto-/Manuell-Schalter, native Medienauswahl mit Originalschutz, wahrheitsgemäßer Ordnerstatus und bewusstes Anlegen fehlender sicherer Pfade. Hauptaktionen stehen oben; vier Schritte und nächste Handlung erleichtern den Ablauf. Keine feststehende Leiste verdeckt Felder bei starker Vergrößerung.

Kooperativer Abschluss sichert den eigenen Worker unter Schreibsperre und beendet eigene Dialoge/Server bei bewusster Schließung, letztem Fenster und SIGINT/SIGTERM/SIGHUP. Neuladen und Hintergrundtimer haben Schonfristen; alte Fenster überschreiben keine neueren Einstellungen. Ein echter Speicherfehler hält den Server offen. Stromausfall/SIGKILL erlauben keinen Abschluss; atomare Journale erhalten den letzten bestätigten Stand.

Ressourcenentscheidung und gemessener Scanvergleich: `SCAN_VERGLEICH_2026-11-04.md`. Vollständige Quellprüfung vor Render bleibt Pflicht. Neue Abhängigkeiten: keine. Der abschließende Klartextnachtrag vermeidet eine unbestätigte Erfolgsaussage bei Verbindungsverlust; 20 lokale JavaScript-Verträge erneut bestanden. Kontrollierte Main-Vorwärtsintegration und vollständige CI auf dem tatsächlichen Main-Abschlusscommit werden separat nachgeprüft und in der Abschlussmeldung genannt.

Recovery-Key: Basis main `eb1c1ba0713d9c7bb6bb0462e56fc630f4ae218f`, Produktstand/CI oben, nächster Schritt Main-CI und Paketabschluss. Große Renderumstellung, Rechte-/Lizenzentscheidung und echte Kubuntu-/Nutzer-Endabnahme bleiben separat offen. Stable: NEIN.

---
## Historie

# Main-Integration abgeschlossen · 0.9.1-dev

**Produktstand in main:** 771891f062ef11b84c2355bdac96b4cbe12bdf2c. **Main-CI #41736344529 erfolgreich** auf genau diesem SHA: 173 Python-/Medientests ohne Überspringer, 16 echte Chromium-Verträge und je 20 Tastatur-/Kontrast-/Layoutfälle. Die zunächst integrierte Fassung 2f8155cf wurde ebenfalls eigenständig durch Main-CI #41735606838 bestätigt.

PR #42 ist regulär zusammengeführt. Drei zusätzliche bestätigte Befunde wurden auf eigenem Abschlusszweig korrigiert, lokal mit 173 Tests geprüft, alle 76 Quelldateien per Git-Blob-Fingerabdruck mit dem veröffentlichten Commit abgeglichen und anschließend mit SHA-geschützter Vorwärtsübernahme ohne Force-Push integriert. Keine neue PR und kein zusätzliches Codex-Review beauftragt. Alle vier vorhandenen Reviewhinweise sind nach Fehlerkorrektur und Prüfnachweis aufgelöst.

Korrigiert: erneute vollständige MP4-Prüfung vor Archivfreigabe, bewusste gezielte Erstvorbereitung ohne vorhandenes Manifest, Vorschauerhalt bei identischem Medienbestand und Invalidierung bei Änderung. Der vorab korrigierte hidden-Stil bleibt abgesichert. Version 0.9.1-dev, keine neue Produktabhängigkeit, kein neuer Renderumbau.

Recovery-Key: Hauptzweig; letzter geprüfter Produkt-SHA und Main-CI oben. Dieser abschließende Dokumentationsnachtrag verändert keine Produktdatei und wird separat nachgeprüft; seine tatsächliche Main-SHA steht in der Abschlussmeldung. Nächster zulässiger Entwicklungsschritt bleibt die separat geplante Phasenberechnung mit sicherem Zwischenzustand. Rechte-/Lizenzentscheidung, restliche QA und finale echte Kubuntu-/Nutzer-Endabnahme bleiben zuletzt OFFEN. Stable: NEIN.

---
## Historie der Integrationsarbeiten

# Main-Integration und Abschlusskorrekturen · 03.11.2026

PR #42 regulär integriert: main 2f8155cf4ae71f71f0b79aba79490565888e24c2. Der geprüfte PR-HEAD war 3a948f1257c40787588c069117289ca2ca337b6d, PR-CI #41734655588 erfolgreich mit 169 Python-/Medientests, 16 Chromium-Verträgen und je 20 Tastatur-/Kontrast-/Layoutfällen auf Test-Merge 0f28153b1b67fcab02d325ad78f3e8a1d15c5a3c. Main-Nachkontrolle #41735606838 getrennt.

Integrationskontrolle bestätigt drei zusätzliche offene Befunde aus den vorhandenen Reviewhinweisen: ungültige Altvideos dürfen nicht durch Hashvergleich allein zur Archivierung freigegeben werden; Erstvorbereitungsfehler ohne Manifest brauchen einen bewussten, auf genau diesen Auftrag beschränkten Wiederweg; unveränderte Quellen müssen ihre Vorschauzuordnung behalten. Der bereits vorher korrigierte hidden-Stil ist unverändert abgesichert.

Abschlusszweig fix/main-integration-closeout, Version 0.9.1-dev: erneute vollständige Videoprüfung vor Archivfreigabe; explizite Einzelvorbereitung ohne fremde Aufträge/Dateien zu bewegen; Erhalt gespeicherter Vorschauen nur bei gleicher Pfad-/Inhaltsidentität, sonst explizite Invalidierung. Vier neue Negative/Positive; gezielte Erstprüfung mit zwölf Fällen bestanden. Vollständiger Commitnachweis und Main-CI werden separat abschließend geprüft. Kein neuer Renderumbau, kein Stable-Release.

Recovery-Key: Basis main 2f8155cf; eigener Abschlusszweig oben; Ziel drei bestätigte Lücken schließen und regulär vorwärts integrieren; letzter Befund gezielte Tests bestanden; nächster Schritt vollständige gemeinsame Prüfung, SHA-geschützte Vorwärtsübernahme und Main-Nachkontrolle. Aktuelle Main-SHA und Prüflauf stehen zusätzlich in der Abschlussmeldung. Rechteentscheidung, restliche QA und echte Kubuntu-/Nutzer-Endabnahme bleiben zuletzt offen.

---
## Historischer Entwicklungsstand vor Main-Integration

# Arbeitsstand NI-20261103-01 · 03.11.2026

Basis main: d8798d35cdfe3406317d1124966f9b9834dff41c. Arbeitszweig: feat/audit-preview-jobs-20261103. Einzelne Korrekturen auf GitHub: A01 f403c56b307c9e5e75978b52b4408fcce7074a3a, A02 b19fd1a8cc10b40c89648ed3fa39b8f08772e1ed, A03 e328f1de65c3191453460db0a4ccc57d58cc9464, A04 0e4785181d0f505ef2f4c67f917b108d70160cbb. Vorschaukern c4c6869367974dbcaa2923aa0777c77870c57891, Auftragsoberfläche 95e08aadb72f09a46914b0633e8553b0b7f3ec58. PR #42: https://github.com/provoware/Video-Zoom-Pro-2026/pull/42. Noch nicht in main.

Gemeinsamer Produkt-HEAD 5ace6977fff897efb4144856467a4e37334ceabf: alle 75 lokalen Quelldateien per Git-Blob-Prüfsumme identisch. GitHub-Lauf #41732961907 erfolgreich auf Test-Merge c0798a202bdb16a80974508d30d0521dc06df655: 169 Python-/Medientests ohne Überspringer, 16 echte Chromium-Verträge, 20 Tastatur-/Kontrastfälle (28 Tab-Stopps, Mindesttextkontrast 7,127:1) und 20 Layoutfälle ohne horizontalen/Textüberlauf. Artefakt 13277267096 geprüft. Entwickler-Sichtprüfung Kopf/Desktop/200-%-Simulation erfolgt; ergänzender Nachtrag liefert gezielte Aufnahmen der neuen offenen Songliste. Dieser Nachtrag benötigt eine eigene CI und verändert keine Medienlogik.

Gezielte Messbestätigung auf Produkt-HEAD 5ace6977, saubere Arbeitskopie: BREI/10 Bilder, je zwei Läufe; Bestand 1267,4 MiB / 5,426 s, Zweiphasenprototyp 360,8 MiB / 5,676 s. Rund 71,5 % weniger Spitzen-RAM, ca. 4,6 % mehr Zeit; Bildfolgen identisch. Timing-Schwankungen gegenüber der breiteren Vorstudie ausdrücklich getrennt.

Vier Fehler einzeln behoben und gezielt geprüft. Gemeinsame lokale Gesamtprüfung nach A04: 160/160, keine Überspringer, lokaler Quellcommit 5d481c9a9bf88ef7307c6de1ad4ebcb514d2b35d. Lokale und GitHub-SHAs sind verschiedene Commitobjekte; der lokale Nachweis ist kein GitHub-CI-Nachweis. Neue Vorschau-/Auftragsproben und 16 ausgeführte JavaScript-Verträge lokal erfolgreich. Abschließende Gesamtprüfung und echte Chromium-Matrix folgen auf dem eingefrorenen gemeinsamen Stand.

Produkt 0.9.0-dev: kurze Vorschau, kompakte ausklappbare Songliste, bewusste Einzel-Freigabe. Originale/Archivzustände werden durch Vorschau nicht verändert. Kein neues Produktpaket. Größere Renderoptimierung wird ausschließlich anhand isolierter Messungen ausgewählt; Messprototyp ist kein produktiver Renderer. Siehe RENDER_VERGLEICH_2026-11-03.md.

Recovery-Key: Zweig oben; Ziel A01–A04 + Vorschau/Liste + Messentscheidung; letzter Befund lokale Kern-/HTTP-/JavaScript-Prüfungen bestanden; nächster Schritt gemeinsame Commitprüfung, Chromium und ZIP am endgültigen Stand. Verbleibende Altaufgaben ARCH-01/SEC-01/UX-04b und Rechteentscheidung nicht durch diesen Auftrag erledigt. Finale echte Kubuntu-/Nutzer-Endabnahme bleibt zuletzt OFFEN. Stable: NEIN.

---
## Vorheriger Nachweisstand (historisch)

# Status und Wiederaufnahme – 02.11.2026

## Integration vollständig durchgeführt
| Paket | Hauptzweig-Commit | Hauptzweigprüfung |
|---|---|---|
| #34 Strategie | d470ea00d239fc1d57031fcd43808d1ae0e6e353 | #41377347113 erfolgreich |
| #35 WAV | 60b24d9806f346f15f3f6bd645cde1cad7fb5589 | #41377490494 erfolgreich |
| #36 Speicher | 8fca030174d4a00bcf2b4dca7e673a8b93494951 | #41377620159 erfolgreich |
| #37 Einrichtung | e544b711794080be5300158dd6608b964c5b9bea | #41377743071 erfolgreich |
| #38 sichere Bedienwerte | 45ae369e04003ff0e8cef27d87ec7e6123da5835 | #41378432136 erfolgreich |
| #39 echte Tastatur/Kontrast | 83545bc26496a6d723fc4ea5eab723f9a1df1caf | #41378950862 erfolgreich |
| #40 zweites Fenster | 2eec90242b9477c2f41e0af690e0a35f5e287620 | #41379321415 erfolgreich |

Alle Übernahmen regulär, ohne Force-Push und ohne Abschwächung einer Pflichtprüfung. Originalauftrag #34 → #35 → #36 → #37 eingehalten, danach Bedienung implementiert.

## Exakte Nachweise des letzten Produktstands
- Quell-HEAD #40: `f82e377f23c5d7991bc1af066e44707681aa06a6`, lokal 151/151 ohne Überspringer; alle 67 versionierten lokalen Dateien per Git-Blob-Fingerabdruck mit veröffentlichtem Quellbaum identisch.
- PR-CI #41379032590 erfolgreich auf tatsächlichem Test-Merge `2876ec0016e23a79ddb83460e242290bc44ebf67`: 151 Python-/Medientests, 13 ausgeführte Chromium-Verträge, 20 echte Tastatur-/Kontrastfälle, 20 Layoutfälle.
- Berichte tragen die tatsächlich geprüfte CI-SHA. Artefakt `videozoom-layout-nachweise`, ID 13112139788 im #40-Lauf. Quell-HEAD, Test-Merge und Hauptzweig-Commit nicht gleichsetzen.
- Vorherige Tastaturprüfung #39: 25 natürliche Tab-Stopps pro Fall, kleinster gemessener Textkontrast 7,127:1 und Fokuskontrast 10,900:1. Diese Messwerte beziehen sich auf den #39-Artefaktbericht, nicht auf einen ungemessenen zukünftigen Stand. Entwickler-Sichtprobe der 800×600/200%- und 1280×720-Aufnahmen erfolgt; echte Kubuntu-Sichtprüfung bleibt OFFEN.

## Implementierte Wirkung
- Ausgewählte Bedienwerte mit exakter alter Dateisicherung, Fingerabdruck und gruppenweiser Rücknahme auch nach Neustart; keine Änderung von Medien/Pfaden/Ressourcen oder später veränderten anderen Werten. Schreibfehler, externe Einstellungsänderung und manipulierte Sicherung verhindern stilles Überschreiben.
- Während eigener laufender Verarbeitung nur das Farbschema speichern; laufende Worker-Konfiguration bleibt unverändert.
- Zweite Oberfläche prüft vorhandene Kern-Sperre nur lesend, zeigt frisches Journal und fremde Verarbeitung an, erfindet keine Prozente und verweigert fremde Start-/Stopp-/Schreibaktionen. Kein Löschen alter Sperren.
- Echte Tab-/Leertasten und berechnete Text-/Fokus-/disabled-/Hover-Kontraste in 20 Fällen; getrennte bestehende Layoutmatrix bleibt erhalten. Keine zusätzliche Produktruntime.

## Wiederaufnahme und verbleibender Umfang
Branch dieses reinen Nachweisabgleichs: `docs/ui-integration-evidence`, Basis `2eec90242b9477c2f41e0af690e0a35f5e287620`; neuer Dokumentations-HEAD/PR und seine vollständige Nachprüfung stehen im PR. Produktdateien unverändert. Vor weiteren Mutationen Nutzer-Input, main-HEAD und offene PRs erneut lesen.

`docs/TODO.md` bleibt allein operativ. Bedienfunktionen erledigt; UX-04b (freigegebene Pixelreferenz, Verlaufspixel/Farbsehprüfung) bleibt sichtbar offen. Danach Architektur-/Sicherheitsbewertungen, QA-FINAL, Rechte-/Lizenzentscheidung und eingefrorener Releasekandidat. Echte Kubuntu-/Nutzer-Endabnahme ausdrücklich zuletzt. Stable: NEIN.
