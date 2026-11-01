# Funktionsdiagramm 01 – Einfacher Ablauf

**Version:** 1.0 · **Quellstand:** `56162cc6a1b3e1e00d61c77c78518cd7e372a17d` · **Stand:** 01.11.2026.

Dieses Diagramm übersetzt die beiden getrennten Workflows und die Ausgabeabsicherung in einfache Schritte. Es ersetzt keine Funktionsprüfung.

```mermaid
flowchart TD
  A["1 · Programm starten<br/>STARTEN.sh → Python → lokale Browseroberfläche"]
  B["2 · WAV und Bilder erkennen<br/>Dateien erst nach abgeschlossener Übertragung übernehmen"]
  C["3 · Song vorbereiten<br/>Titel, Bildordner, Songlänge, Prüfsummen"]
  D{"Alle Medien eindeutig<br/>und gültig?"}
  W["WARTET: Bilder fehlen<br/>oder PRÜFEN: Quelldaten unklar"]
  E["4 · BEREIT<br/>Auftrag dauerhaft im Journal sichern"]
  F["5 · Stapel auswählen<br/>Wiederanlauf + CPU-/RAM-Grenzen"]
  G["6 · Schnell: Bilder rückwärts<br/>ohne Zoom, kurz anzeigen"]
  H["7 · Ruhig: Bilder vorwärts<br/>sanfter Zoom + Übergänge"]
  I{"8 · MP4-Prüfung<br/>Bild, Ton, Songdauer und SHA-256"}
  R["Sichere Korrektur mit Wartezeit<br/>maximal drei Versuche, sonst PRÜFEN"]
  J["9 · Quellen archivieren<br/>_verwendet_ · Kopie prüfen · Quittung"]
  K["10 · ARCHIVIERT<br/>Video in FERTIG · 100 %"]
  S["Begleitend: Sensoren + Auftragsjournal<br/>STATUS.json / ereignisse.jsonl / Browserstatus"]
  A --> B --> C --> D
  D -- "Nein" --> W
  D -- "Ja" --> E --> F --> G --> H --> I
  I -- "Nein" --> R
  I -- "Ja" --> J --> K
  R -. "technisch lösbar" .-> F
  F -. "Messwerte und Fortschritt" .-> S
  J -. "Ablage-/Prüfstatus" .-> S
  classDef blue fill:#d9eeff,color:#102333,stroke:#3980b6;
  classDef green fill:#d8f4e9,color:#103c2c,stroke:#279675;
  classDef orange fill:#fff0d6,color:#42300b,stroke:#d3a243;
  classDef purple fill:#ede2ff,color:#362151,stroke:#8962ad;
  classDef danger fill:#ffe4dd,color:#582721,stroke:#d27c6c;
  class A,B blue;
  class C,D,E green;
  class F,G,H orange;
  class I,J,K purple;
  class W,R danger;
```

### Was die Pfeile bedeuten

Der Eingang darf unabhängig vom Video-Renderer weiterarbeiten. `WARTET` ist **kein** Datenfehler; ein unklarer oder beschädigter Datensatz bleibt unter `PRÜFEN`. Erst nach einer geprüften MP4 und bestätigter Archivierung erreicht der Auftrag 100 %.

**Dateiorte:** `Downloads/` → `EINGANG/<song>/BILDER/` → `PROTOKOLLE/auftraege.json` → `FERTIG/*.mp4` und `VERWENDET/*_verwendet_*`.

**Hinweis zur Bildablage:** Die separate Kategorisierung `BILDER/PROVOWARE|CODING|THEMA` ordnet Bilder **noch keinem Song** zu. Das passiert erst durch dessen eigenen `EINGANG/<song>/BILDER`-Ordner.

**Änderungspflicht:** Nach einer Änderung an `vorbereiten`, `stapel`, `_render`, `_archive` oder der Datenstruktur den Fluss mit Code und Tests erneut abgleichen.
