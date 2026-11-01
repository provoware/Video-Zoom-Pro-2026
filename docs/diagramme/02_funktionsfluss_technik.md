# Funktionsdiagramm 02 – Technischer Daten- und Befehlsfluss

**Version:** 1.0 · **Quellstand:** `56162cc6a1b3e1e00d61c77c78518cd7e372a17d` · **Stand:** 01.11.2026.

Die Begriffe in Klammern sind tatsächliche Python-Funktionen aus diesem Repository. Werte ohne Zusatz sind **Standardwerte** und können teilweise in Einstellungen geändert werden.

```mermaid
flowchart TD
 subgraph START["A · START UND BEDIENUNG"]
   A["STARTEN.sh<br/>python3 -m videozoom"]
   B["__main__.main()<br/>lesen() + konfigurieren()<br/>Format, Kategorie, Ordner"]
   C["webui.starten()<br/>127.0.0.1 + Zugriffstoken<br/>GET /status, /diagnose<br/>POST /aktion, /einstellungen, /ordnerwahl"]
   A --> B --> C
 end
 subgraph INPUT["B · WAV/BILDER UND VORBEREITUNG"]
   D["Workflow.vorbereiten()<br/>bilder_einsortieren()<br/>stabil(): 5 s / >100 Byte<br/>Marker: chatgpt + eindeutiger Zweck"]
   E["titel() + slug()<br/>Songordner: EINGANG/<song>/BILDER<br/>keine unklare automatische Zuordnung"]
   F["dauer() → ffprobe<br/>zeitplan(): 25 fps, 0,45 s<br/>SHA-256 je Quelle → auftraege.json<br/>Status BEREIT"]
   D --> E --> F
 end
 subgraph RENDER["C · STAPEL UND VIDEO"]
   G["Workflow.stapel()<br/>_recover_inflight() + Sperre<br/>stapelgroesse=3, höchstens 20"]
   H["scope_verfuegbar(cfg) + quota_befehl()<br/>systemd-run --user --scope<br/>CPUQuota: 30 % verfügbare Kerne<br/>MemoryMax: 2048M"]
   I["Workflow._render()<br/>ffmpeg_befehl()<br/>concat rückwärts / zoompan vorwärts<br/>xfade Übergänge, ggf. fade"]
   J["FFmpeg H.264 libx264: crf=21<br/>AAC: 192 kbit/s · 25 fps<br/>-progress pipe:1"]
   G --> H --> I --> J
 end
 subgraph VERIFY["D · PRÜFUNG / ARCHIV / PROTOKOLL"]
   K["video_gueltig() → ffprobe<br/>Bild + Ton + Dauer prüfen<br/>SHA-256 sichern, MP4 exklusiv in FERTIG"]
   L["_archive() + kopieren_und_archivieren()<br/>Quellen prüfen, Kopie+fsync+SHA<br/>_verwendet_ · Quittung archiv.jsonl"]
   M["ARCHIVIERT → 100 %<br/>fortschreiben() / STATUS.json<br/>ereignisse.jsonl"]
   K --> L --> M
 end
 X["Fehlerkategorien<br/>WARTET / PAUSIERT / PRÜFEN<br/>max. 3 Versuche, sichere Originale"]
 Y["Sensoren.lesen()<br/>CPU, RAM, freier Speicher<br/>Browser /status alle 1,5 s"]
 C --> D
 F --> G
 J --> K
 G -. Fehler .-> X
 K -. Fehler .-> X
 L -. Fehler .-> X
 C -. Anzeige .-> Y
 M -. Fortschritt .-> Y
```

### Übermittelte Daten und häufigste Parameter

| Übergang | Eingaben | Ausgabe / Wirkung |
|---|---|---|
| Browser → Python | `POST /aktion` mit `prepare`, `batch`, `once`, `watch`, `stop` | startet genau einen Workflow; nicht zwei konkurrierende Writer |
| Einstellungen → Kern | `downloads`, `arbeitsordner`, `format`, `kategorie`, `fps`, `uebergang`, `stapelgroesse` | validierte Konfiguration |
| WAV → Vorbereitung | Dateipfad, Datum, Dateigröße, Titel, Bilder | Dauer, Bildliste, Quell-SHA-256; Status BEREIT/WARTET/PRÜFEN |
| Vorbereitung → Journal | `titel`, `status`, `dateien`, `laenge`, `versuche` | `PROTOKOLLE/auftraege.json` |
| Journal → FFmpeg | WAV und 1–40 Bilder, Gesamtzeit, Zielauflösung | zwei Bildfolgen mit einer Tonspur |
| FFmpeg → Prüfung | temporäre MP4 | `ffprobe` prüft Bild + Ton + Dauer; SHA-256 des Videos |
| Prüfung → Archiv | verifizierte MP4 + Quell-SHA-256 | Quelle erst nach geprüfter Kopie löschen, Quittung schreiben |
| Status → Browser | Sensoren, Auftragszähler, `phase`, `prozent` | drei getrennte Fortschrittsanzeigen, Protokoll |

### Verwendete Befehle (verkürzt, kein direkt kopierbarer vollständiger Renderbefehl)

```text
python3 -m videozoom
ffprobe -v error -show_entries format=duration:stream=codec_type,width,height -of json DATEI
systemd-run --user --scope -p CPUQuota=…% -p MemoryMax=…M -- ffmpeg …
ffmpeg -loop 1 ... -filter_complex "concat;zoompan;xfade" -c:v libx264 -crf 21 -c:a aac -b:a 192k -progress pipe:1 …
```

**Sicherheitsgrenze:** In normalen Läufen muss `systemd-run` funktionieren; fehlt die wirksame Quotenprüfung, wird **nicht ungebremst gerendert**. Der eigenständige Testmodus ersetzt diese Begrenzung **nur** für isolierte Tests. `FFmpeg`-Parameter werden vom Kern erstellt, nicht vom Browser als frei ausführbare Befehle übergeben.
