# Rendervergleich und Auswahl · NI-20261103-01

## Entscheidung

Für die nächste größere Renderänderung wird die **getrennte Berechnung der schnellen Rückwärtsphase und der langsamen Vorwärtsphase** ausgewählt. Verlustfreie Zwischenvideos werden anschließend einmal gemeinsam kodiert. Der Messprototyp steht ausschließlich unter `scripts/render_phasenprobe.py`; er ist **nicht** im ausgelieferten Produktpfad aktiviert. Die derzeitige Produktionsberechnung bleibt unverändert.

Die reine Begrenzung auf einen Filterarbeiter wird nicht als allgemeine Optimierung übernommen: der geringe Speichergewinn rechtfertigt keine teils längere Laufzeit. Die Zweiphasenvariante reduziert die gemessenen Speicherspitzen deutlich, benötigt aber Zwischenplatz und zusätzliche Arbeitsschritte.

## Explorative Vergleichsmessung

36 echte Renderläufe: KLAS/BREI × 1/5/10 Bilder × drei Varianten × zwei Wiederholungen. Acht Sekunden eigene synthetische Musik, farbige eigene 512×384-PNGs, vier verfügbare CPU-Kerne; 2-GiB-Prozessbaum-Wächter und 60-s-Laufbudget. Variantenreihenfolge wechselt. Renderzeit und FFmpeg-Spitzen-RAM werden getrennt von der anschließenden Ergebnisprüfung erfasst. Die Ergebnisse sind eine lokale Arbeitskopien-Vorstudie, kein CI- oder Kubuntu-Beleg. Rohdaten: `messungen/render_vergleich_vorstudie_2026-11-03.json`.

| Format | Bilder | Bestand: s / MiB | Ein Filter: s / MiB | Zwei Phasen: s / MiB | RAM-Ersparnis Phasen |
|---|---:|---:|---:|---:|---:|
| KLAS | 1 | 1.13 / 234.2 | 1.17 / 232.3 | 1.37 / 106.6 | 54.5 % |
| KLAS | 5 | 1.73 / 321.0 | 1.48 / 306.9 | 2.09 / 108.5 | 66.2 % |
| KLAS | 10 | 1.74 / 390.5 | 1.82 / 362.6 | 2.22 / 162.2 | 58.5 % |
| BREI | 1 | 2.84 / 829.3 | 3.05 / 826.7 | 3.56 / 282.0 | 66.0 % |
| BREI | 5 | 4.84 / 1089.8 | 5.32 / 1070.0 | 5.54 / 286.0 | 73.8 % |
| BREI | 10 | 5.10 / 1266.4 | 5.48 / 1228.0 | 5.81 / 360.8 | 71.5 % |

In allen sechs Gruppen waren die vollständig decodierten Bildfolgen über alle Varianten und Wiederholungen identisch (Frame-Prüfsummen). Alle 36 Ausgaben bestanden die neue Auflösungs-/Bildraten-/Spurdauer-/Gesamtleseprüfung. Das beweist die Gleichheit dieser Testdaten, keine allgemeine Bildgleichheit beliebiger Produktionen. Audio wurde mit geprüfter Spurdauer und vollständigem Lesetest kontrolliert; keine gesonderte bitweise Tonvergleichsmessung.

BREI mit zehn Bildern: ungefähr 71,5 % weniger Spitzen-RAM, dabei rund 13,8 % mehr Rechenzeit in dieser Vorstudie. Auf einer HDD können Zwischenvideos zusätzlich bremsen; das wurde hier nicht als Zielsystemmessung geprüft. Es werden keine allgemeinen Geschwindigkeitsgewinne versprochen.

Ein früher Versuch mit einer 3-GiB-Adressraumgrenze wurde verworfen: virtueller Adressraum ist nicht derselbe Schutz wie der produktive residente RAM-Verbrauch. Dessen Fehlerwerte fließen nicht in die Entscheidung ein.

## Reproduzieren

`python3 scripts/render_vergleich.py --bericht /tmp/render-vergleich.json` führt die volle isolierte Messreihe aus. `--formate BREI --bilder 10 --varianten bestand zweiphasig` führt den gezielten abschließenden Vergleich aus. Der Bericht enthält Commit, lokale Änderungen, Quelldatei-Prüfsummen, FFmpeg-Version, Grenzen und Einzelwerte. Berichte außerhalb des Repositorys ablegen, damit sie keine unbemerkte Arbeitskopienänderung erzeugen.

## Nächste Implementierung, bewusst außerhalb dieses Pakets

1. Phasenrendern als eigenen Produktpfad entwerfen; keine fragile Filtertext-Umschreibung aus dem Messprototyp direkt übernehmen.
2. Temporärplatz vorab planen und in das vorhandene Journal einbinden; jede Phase atomar veröffentlichen und vollständig prüfen. Nur bestätigte Phasen nach Abbruch wiederverwenden.
3. CPU-/RAM-Scope, Stopp, Originalschutz, Archivgrenzen und alle fünf Ausgabeformate erhalten. Dauer, Bildfolge und Ton über den Phasenübergang mit komplexeren synthetischen Bildern prüfen.
4. Erst danach lange Songs, 20/40 Bilder, 4K und echte HDD-Bedingungen prüfen; die abschließende persönliche Kubuntu-Abnahme bleibt zuletzt.

Diese Iteration erfüllt die beauftragte **Auswahl anhand einer Vergleichsmessung**, nicht die noch nicht beauftragte Produktintegration des größeren Umbaus.
