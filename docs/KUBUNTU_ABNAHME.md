# Kubuntu-Endabnahme – PROVOWARE Video Zoom Pro

**Stand 2026-11-01: OFFEN.** Erfolgreiche GitHub-Tests auf Ubuntu-GitHub-Runner sind kein Ersatz für Tests auf deinem eigenen Kubuntu-Rechner. Das Tool ist ohne Tk, Cloud und zusätzliche Python-Abhängigkeiten gebaut.

## 1. Start und automatische System-/Ressourcenprüfung

Voraussetzung: Repository-ZIP vollständig entpackt, Kubuntu mit normalem Benutzerkonto, FFmpeg installiert. Keine Administratorrechte für den normalen Programmstart.

Im Projektordner:

```bash
python3 scripts/kubuntu_abnahme.py --bericht "$HOME/kubuntu_videozoom_diagnose.json"
```

Der Schnellbericht prüft Linux-Distribution, Desktopumgebung, Python, vorhandene FFmpeg-Befehle und den systemd-Status, **ohne** eine CPU-Lastprobe auszulösen. Der Bericht vermerkt alle noch offenen Sichtprüfungen.

### Optionale echte cgroup-Lastmessung

```bash
python3 scripts/kubuntu_abnahme.py --cpu-test --bericht "$HOME/kubuntu_videozoom_abnahme.json"
```

Dieser zweite Befehl startet **auf ausdrücklichen Aufruf** einen auf 2,5 Sekunden begrenzten Lastversuch im selben `systemd --user`-CPU-/RAM-Scope wie die Videoberechnung. Das Skript liest `cpu.max`, `memory.max` und den tatsächlichen CPU-Verbrauch aus `/sys/fs/cgroup`. Die Messung gilt nur, wenn die konfigurierte Quote und die beobachtete obere Belastungsgrenze plausibel übereinstimmen. Ein fehlender Benutzerscope führt zu einem sichtbaren Fehler, niemals zu einer erfundenen Freigabe. Andere Prozesse, Grafikkarte und Datenträgerlast werden dadurch nicht pauschal auf 30 % beschränkt.

Der CPU-Wert wird anhand der Zahl der für den Prozess tatsächlich zugänglichen logischen Kerne berechnet; 4 Kerne × 30 % entsprechen `CPUQuota=120%` bezogen auf eine einzelne CPU. Prüfe zusätzlich das reale Verhalten beim Langzeitrender.

## 2. Sicht- und Bedienabnahme (manuell; noch OFFEN)

Für jede der vier Stufen **100, 125, 150 und 200 %** das Programm bei **800 × 600 Pixeln** prüfen. Dokumentiere je Stufe einen Screenshot und Datum/Uhrzeit. Der Prüfer darf diese Werte nicht automatisch auf BESTANDEN setzen.

| Prüffall | Erfolgskriterium |
|---|---|
| Start | Browseroberfläche öffnet sich lokal; keine Tk-Abhängigkeit |
| Ordner wählen | KDE-Dialog öffnet, Abbrechen bewahrt alten Pfad |
| Songvorbereitung | WAV wird erkannt; fehlende Bilder verständlich angezeigt |
| Stapel | Kontrollknöpfe bleiben erreichbar; Fortschritte getrennt |
| Tastatur | Alle Schalter, Felder und Auswahlmenüs mit Tab erreichbar; Fokus sichtbar |
| Schrift/Zoom | Bei 800 × 600 und 200 % keine verdeckten Pflichtknöpfe; vertikales Scrollen möglich |
| Fehlerhinweis | Ursache, automatische Korrektur, notwendige Handlung und Logpfad verständlich |
| Stop/Neustart | Auftrag bleibt erhalten, kein erneutes Rendern einer bestätigten MP4 |

Prüfe zusätzlich mindestens **20 Songs über mehrere Stapel**, einen echten Programmabbruch, eine beschädigte WAV, ein unterbrochenes Archiv und den vollständigen 30-%-CPU-Langzeitrender. Für jede Prüfung gehören erwartetes Ergebnis, tatsächliches Ergebnis und Beleg (Screenshot/Protokoll) in ein lokales Abnahmeverzeichnis.

## 3. Freigabeentscheidung

**Automatische Grenzen und sichtbare Bedienbarkeit sind zwei unabhängige Gates.** Der JSON-Bericht des Prüfers ist kein Stable-Zertifikat. Ohne persönliche Sichtkontrolle, echte Ressourcenmessung und Langzeitstabilität bleibt `stable_freigabe=false`.

Erst nach eingefrorenem Release-Commit und allen bestandenen Tests eine Stable-Version veröffentlichen. Andere Repositories – besonders VideoBatch – bleiben unverändert.
