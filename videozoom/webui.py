"""Sichere lokale Browser-Oberfläche: kein Tk, kein Netzwerkdienst nach außen."""
from __future__ import annotations
import json
import fcntl
import stat
import os
import secrets
import shutil
import subprocess
import threading
import webbrowser
from collections import deque
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from .core import Workflow, konfigurieren, json_sicher, lesen
from .diagnose import pruefen
from .einstellungen_sicher import zuruecksetzen, wiederherstellen


def ordner_waehlen(feld: str, startwert: str) -> str | None:
    """Native Ordnerauswahl: kein Tk, keine freie Befehlsausführung."""
    if feld not in {"downloads", "arbeitsordner"}:
        raise ValueError("Nur Downloads- und Arbeitsordner dürfen ausgewählt werden.")
    if not (os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY")):
        raise RuntimeError("Kein grafischer Desktop aktiv. Ordner im Textfeld eingeben.")
    anfang = Path(startwert).expanduser()
    if not anfang.is_dir() or anfang.is_symlink():
        anfang = Path.home()
    if shutil.which("kdialog"):
        befehl = ["kdialog", "--getexistingdirectory", str(anfang),
                   "--title", "PROVOWARE – Ordner auswählen"]
    elif shutil.which("zenity"):
        befehl = ["zenity", "--file-selection", "--directory",
                   "--filename=" + str(anfang) + "/",
                   "--title=PROVOWARE – Ordner auswählen"]
    else:
        raise RuntimeError("KDE-Ordnerdialog nicht verfügbar. Ordner im Textfeld eingeben.")
    try:
        ergebnis = subprocess.run(befehl, capture_output=True, text=True,
                                 check=False, timeout=120)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise RuntimeError("Ordnerauswahl fehlgeschlagen: " + str(exc)) from exc
    if ergebnis.returncode:
        return None  # Abbrechen ist kein Datenfehler.
    wert = ergebnis.stdout.strip()
    if not wert:
        return None
    ziel = Path(wert).expanduser()
    if not ziel.is_absolute() or ziel.is_symlink() or not ziel.is_dir():
        raise ValueError("Ungültiger oder unsicherer Ordner. Keine Einstellung geändert.")
    return str(ziel)


HTML = r'''<!doctype html><html lang="de"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>PROVOWARE · Video Zoom Pro</title>
<style>
:root{
 font:18px/1.5 system-ui,sans-serif;color-scheme:dark;
 --bg:#0b151d;--panel:#132b35;--text:#f4fbff;--muted:#d0e0e9;
 --field:#0a202a;--line:#547780;--accent:#33d9e3;--accent-rgb:51,217,227;
 --accent-ink:#07242c;--focus:#ffe78c;--success:#74e5b0;--danger:#913c49;
 background:var(--bg);color:var(--text)
}
body[data-theme="violett"]{--accent:#baa6ff;--accent-rgb:186,166,255;--accent-ink:#251a42;--line:#8177ac}
body[data-theme="gruen"]{--accent:#7deaaf;--accent-rgb:125,234,175;--accent-ink:#0a3723;--line:#568b74}
body[data-theme="orange"]{--accent:#ffd082;--accent-rgb:255,208,130;--accent-ink:#382308;--line:#a18c63}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{max-width:1190px;min-width:0;margin:auto;padding:clamp(12px,2vw,24px);overflow-x:hidden;background:var(--bg);color:var(--text)}
h1{margin:0;font-size:clamp(1.55rem,3vw,2.15rem);line-height:1.2}
h2{font-size:1.22rem;margin:0 0 12px}
small{color:var(--muted)}
.app-header{display:flex;flex-wrap:wrap;justify-content:space-between;gap:12px;align-items:center;padding:10px 14px;border:1px solid rgba(var(--accent-rgb),.48);border-radius:14px;background:linear-gradient(125deg,rgba(var(--accent-rgb),.11),transparent 68%),var(--panel);box-shadow:0 8px 22px rgba(0,0,0,.16)}
.header-tools{display:flex;align-items:center;flex-wrap:wrap;gap:10px}
.header-tools label{margin:0;font-size:.93rem}
.header-tools select{width:auto;min-width:155px;margin:0}
.phase-nav{display:flex;flex-wrap:wrap;gap:8px;margin:12px 0 10px}
.phase-nav a{flex:1 1 150px;padding:9px 8px;min-height:44px;border:1px solid rgba(var(--accent-rgb),.53);border-radius:10px;background:rgba(var(--accent-rgb),.08);color:var(--text);text-align:center;font-size:.87rem;font-weight:700;text-decoration:none}
.phase-nav a:hover{background:rgba(var(--accent-rgb),.18)}
.phase-nav a{overflow-wrap:anywhere;word-break:normal}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,310px),1fr));gap:12px;margin:12px 0}
.overview{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,140px),1fr));gap:9px;margin:12px 0}
.metric{min-width:0;padding:9px 12px;border:1px solid var(--line);border-radius:12px;background:linear-gradient(125deg,rgba(var(--accent-rgb),.09),transparent 85%),var(--panel)}
.metric small{display:block;font-size:.83rem}
.metric strong{display:block;font-size:1.4rem;line-height:1.2;font-variant-numeric:tabular-nums}
.metric[data-kind="ok"]{border-color:var(--success)}
.metric[data-kind="achtung"]{border-color:var(--focus)}
.format-hint{margin:0 0 6px;padding:8px 11px;border-left:3px solid var(--accent);border-radius:6px;background:rgba(var(--accent-rgb),.07);color:var(--muted);font-size:.9rem}
.technical-details{margin:8px 0;padding:8px 12px;border:1px solid rgba(var(--accent-rgb),.43);border-radius:10px;background:rgba(var(--accent-rgb),.04)}
.technical-details summary{cursor:pointer;font-weight:700;min-height:44px;display:flex;align-items:center;gap:7px}
.technical-details summary::marker{color:var(--accent)}
.technical-details[open] summary{margin-bottom:8px}
.technical-details pre{margin:6px 0}
.card-subtitle{color:var(--muted);margin:0 0 8px}
.progress-label{display:flex;justify-content:space-between;gap:8px;align-items:baseline}
.progress-label output{font-variant-numeric:tabular-nums;font-weight:700;color:var(--text)}

article{min-width:0;border:1px solid var(--line);border-radius:14px;background:linear-gradient(180deg,rgba(var(--accent-rgb),.045),transparent 40%),var(--panel);padding:18px;box-shadow:inset 0 0 18px rgba(var(--accent-rgb),.04)}
article:target{outline:3px solid var(--accent);outline-offset:3px}
input,select,button{display:block;width:100%;min-width:0;padding:10px;margin:8px 0;border-radius:9px;border:2px solid var(--line);background:var(--field);color:var(--text);font:inherit;min-height:46px}
label{display:block;margin-top:12px;font-weight:650}
button{background:var(--accent);border-color:var(--accent);color:var(--accent-ink);font-weight:800;cursor:pointer}
button:hover{filter:brightness(1.08)}
button.warn{background:var(--danger);border-color:#f8adb6;color:#fff}
:focus-visible{outline:3px solid var(--focus);outline-offset:3px}
.ordner{display:grid;grid-template-columns:minmax(0,1fr);gap:6px;align-items:center}
.ordner input{min-width:0}.ordner button{width:100%;min-width:150px}
progress{width:100%;height:24px;accent-color:var(--success)}
pre{font:.82rem/1.4 monospace;white-space:pre-wrap;overflow:auto;word-break:break-word;max-height:200px;padding:12px;background:#081821;border-radius:9px}
#status{display:inline-block;padding:6px 12px;border:1px solid var(--success);border-radius:10px;background:#173b32;margin:0;color:#e9fff5}
#hinweis:not(:empty){padding:9px 12px;border-left:4px solid var(--accent);background:var(--panel);border-radius:8px}
#hinweis:empty{display:none}
@media(max-width:900px){
 .app-header{padding:8px}
 .app-brand small{display:none}
 .app-header h1{font-size:1.35rem;line-height:1.16}
 .header-tools{gap:6px}
 .phase-nav{margin:8px 0}
 .phase-nav a{font-size:.84rem;padding:6px}
}
@media(max-width:570px){.ordner{grid-template-columns:1fr}.ordner button{width:100%}.phase-nav a{flex-basis:calc(50% - 8px)}}
@media(max-width:520px){
 article{padding:12px}
 .app-header{padding:8px}
 .app-brand small{display:none}
 .app-header h1{font-size:1.25rem;line-height:1.13}
 .header-tools{width:100%;gap:6px}
 .header-tools label{font-size:.85rem}
 .header-tools select{flex:1;min-width:0;min-height:40px;padding:4px;font-size:.91rem}
 #status{padding:4px 8px;font-size:.91rem}
 .phase-nav{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:6px;margin:8px 0}
 .phase-nav a{min-width:0;min-height:42px;padding:5px;font-size:.84rem}
}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}*{animation:none!important;transition:none!important}}
</style></head><body>
<header class="app-header">
<div class="app-brand"><h1>🎬 PROVOWARE · Video Zoom Pro</h1><small>Lokal · offline · ohne Tk · zwei getrennte Workflows</small></div>
<div class="header-tools"><label for="theme">Farbschema</label><select id="theme" onchange="themaWaehlen()"></select>
<p id="status" role="status" aria-live="polite">Bereit</p></div>
</header>
<nav class="phase-nav" aria-label="Arbeitsbereiche">
<a href="#vorbereitung" aria-label="Zu Songs vorbereiten">1 · Vorbereiten</a><a href="#stapel-karte" aria-label="Zur Stapelverarbeitung">2 · Stapel</a>
<a href="#diagnose-karte">3 · Diagnose</a><a href="#protokoll-karte">4 · Protokoll</a>
</nav>
<section class="overview" aria-label="Auftragsübersicht">
<div class="metric"><small>Bereit</small><strong id="kpi-bereit">0</strong></div>
<div class="metric"><small>Warten auf Bilder</small><strong id="kpi-wartet">0</strong></div>
<div class="metric"><small>Video läuft</small><strong id="kpi-laeuft">0</strong></div>
<div class="metric" data-kind="ok"><small>Archiviert</small><strong id="kpi-fertig">0</strong></div>
<div class="metric" data-kind="achtung"><small>Prüfen / Archiv offen</small><strong id="kpi-pruefen">0</strong></div>
</section>
<p id="hinweis" role="alert" aria-live="assertive"></p><div class="grid">
<article id="vorbereitung"><h2>1 · Songs vorbereiten</h2>
<p>WAV erkennen, Titel bereinigen, Bilder zuordnen.</p>
<ol aria-label="Erste Einrichtung"><li>Downloads- und eigenen Arbeitsordner wählen.</li><li>Einstellungen speichern und Systemprüfung ausführen.</li><li>WAV fertig herunterladen, Bilder im zugehörigen Songordner ablegen, dann vorbereiten.</li></ol>
<label for="downloads">Downloads-Ordner</label>
<div class="ordner"><input id="downloads" aria-label="Downloads-Ordnerpfad">
<button type="button" onclick="ordnerwahl('downloads')">📁 Ordner wählen</button></div>
<label for="arbeitsordner">Arbeitsordner</label>
<div class="ordner"><input id="arbeitsordner" aria-label="Arbeitsordnerpfad">
<button type="button" onclick="ordnerwahl('arbeitsordner')">📁 Ordner wählen</button></div>
<label for="format">Videoformat</label><select id="format" onchange="formatHinweis()"></select><p class="format-hint" id="formatinfo">Format auswählen</p>
<label for="kategorie">Dateikategorie</label><select id="kategorie"></select>
<button onclick="speichern()">Einstellungen speichern</button>
<p><small>Während der Verarbeitung lässt sich nur das Farbschema speichern.</small></p>
<label for="resetgruppe">Ausgewählte Einstellungen zurücksetzen</label>
<select id="resetgruppe"><option value="ansicht">Nur Farbschema</option><option value="format">Nur Format und Kategorie</option><option value="bedienung">Farbschema, Format und Kategorie</option></select>
<button onclick="ruecksetzen(false)">Auswahl zurücksetzen · Sicherung anlegen</button>
<button onclick="ruecksetzen(true)">Letzte Rücksetzung zurücknehmen</button>
<p><small>Ordner, Medien und CPU-/RAM-Grenzen bleiben erhalten. Rücksetzen nur bei angehaltener Verarbeitung.</small></p>
<button onclick="aktion('prepare')">Songs vorbereiten</button>
<p><strong id="ready">0</strong> bereit · <strong id="wait">0</strong> warten</p>
</article><article id="stapel-karte"><h2>2 · Stapelverarbeitung</h2>
<p>Erst Bilder rückwärts und schnell, dann vorwärts mit sanften Kamerabewegungen.</p>
<button onclick="aktion('batch')">Stapel starten</button>
<button onclick="aktion('once')">Einmal alles ausführen</button>
<button onclick="aktion('watch')">Automatik einschalten</button>
<button class="warn" onclick="aktion('stop')">Sicher stoppen</button>
<div class="progress-label"><label for="vorbereitungsbar">Songs vorbereiten</label><output id="vorbereitung-wert" for="vorbereitungsbar">0 %</output></div>
<progress id="vorbereitungsbar" value="0" max="100"></progress>
<div class="progress-label"><label for="stapelbar">Stapelverarbeitung</label><output id="stapel-wert" for="stapelbar">0 %</output></div>
<progress id="stapelbar" value="0" max="100"></progress>
<div class="progress-label"><label for="videobar">Aktuelles Video (einschließlich Archivierung)</label><output id="video-wert" for="videobar">0 %</output></div>
<progress id="videobar" value="0" max="100"></progress>
<p id="phase">Kein Vorgang aktiv</p>
</article><article id="diagnose-karte"><h2>3 · Diagnose</h2>
<p>CPU-Ziel: maximal 30 % der zugänglichen Prozessorkapazität. Ohne nachgewiesene Grenze kein Rendern.</p>
<button onclick="diagnose()">Systemprüfung ausführen</button>
<details class="technical-details"><summary>Systemprüfung anzeigen</summary><pre id="diagnose">Noch nicht geprüft</pre></details>
<details class="technical-details"><summary>CPU, RAM und Speicher ansehen</summary><pre id="sensoren">Wird gemessen</pre></details>
<p><small>Die Vorbereitung kann unabhängig von der CPU-Grenze weiterlaufen.</small></p>
</article><article id="protokoll-karte"><h2>4 · Protokoll</h2>
<p class="card-subtitle">Fehler und Aufträge bleiben erhalten. Einzelheiten bei Bedarf öffnen.</p>
<details class="technical-details"><summary>Auftragszahlen ansehen</summary><pre id="jobs">Noch keine Aufträge.</pre></details>
<details class="technical-details"><summary>Meldungen ansehen</summary><pre id="log">Bereit.</pre></details>
</article></div>
<script>
const token=new URL(location.href).searchParams.get('token');
const el=id=>document.getElementById(id);
const THEMEN=['cyan','violett','gruen','orange'];
const FORMATHILFE={
 BREI:'1920 × 1080 · Breitbild (YouTube)',
 HOCH:'1080 × 1920 · Hochformat (Shorts, Reels)',
 QUAD:'1080 × 1080 · Quadrat',
 KLAS:'800 × 600 · Klassisches 4:3',
 '4K':'3840 × 2160 · 4K-Breitbild'
};
function formatHinweis(){
 const code=el('format').value;
 el('formatinfo').textContent=FORMATHILFE[code]||'Bitte ein gültiges Format auswählen.';
}
function prozentWert(value){
 if(value===null||value===undefined||value==='')return null;
 const n=Number(value);
 return Number.isFinite(n)?Math.min(100,Math.max(0,Math.floor(n))):null;
}
function fortschrittAnzeigen(id,feld,info){
 const wert=prozentWert(info&&info.prozent);
 if(wert===null){el(id).removeAttribute('value');el(feld).textContent='Noch unbekannt';return;}
 el(id).value=wert;
 el(feld).textContent=wert+' %';
}
function auftragszahlen(jobs){
 const daten=jobs||{};
 const wert=status=>Math.max(0,Number(daten[status])||0);
 el('kpi-bereit').textContent=wert('BEREIT');
 el('kpi-wartet').textContent=wert('WARTET');
 el('kpi-laeuft').textContent=wert('LAEUFT');
 el('kpi-fertig').textContent=wert('ARCHIVIERT');
 el('kpi-pruefen').textContent=wert('PRUEFEN')+wert('ARCHIV_WARTET');
}
function themaWaehlen(){
 const theme=el('theme').value;
 if(THEMEN.includes(theme))document.body.dataset.theme=theme;
}
async function api(path,data,budget=10000){
 const controller=new AbortController();
 const timer=setTimeout(()=>controller.abort(),budget);
 try{
  const r=await fetch(path+'?token='+encodeURIComponent(token),{method:data?'POST':'GET',
   headers:data?{'Content-Type':'application/json'}:{},body:data?JSON.stringify(data):undefined,
   cache:'no-store',signal:controller.signal});
  const v=await r.json();if(!r.ok)throw Error(v.fehler||'Aktion fehlgeschlagen');return v;
 }catch(e){
  if(e.name==='AbortError')throw Error('Zeitlimit erreicht. Verbindung prüfen; Auftrag bleibt gespeichert.');
  throw e;
 }finally{clearTimeout(timer);}
}
async function aktion(mode){try{let r=await api('/aktion',{mode});el('hinweis').textContent=r.meldung;}
catch(e){el('hinweis').textContent=e.message;}}
async function ordnerwahl(feld){try{
 el('hinweis').textContent='Grafische Ordnerauswahl wird geöffnet …';
 const r=await api('/ordnerwahl',{feld},125000);
 if(r.pfad)el(feld).value=r.pfad;
 el('hinweis').textContent=r.meldung;
}catch(e){el('hinweis').textContent=e.message;}}
async function speichern(){try{
 const cfg={};for(let id of ['downloads','arbeitsordner','format','kategorie','theme'])cfg[id]=el(id).value;
 el('hinweis').textContent=(await api('/einstellungen',{cfg})).meldung;
}catch(e){el('hinweis').textContent=e.message;}}
async function ruecksetzen(zurueck){try{
 const r=await api('/ruecksetzen',{modus:zurueck?'wiederherstellen':'zuruecksetzen',gruppe:el('resetgruppe').value});
 for(const id of ['theme','format','kategorie'])el(id).value=r.cfg[id];
 themaWaehlen();formatHinweis();el('hinweis').textContent=r.meldung;
}catch(e){el('hinweis').textContent=e.message;}}
function diagnoseText(bericht){
 const zeilen=[bericht.startbereit?'BEREIT · Systemprüfung bestanden.':'HANDLUNG NÖTIG · Vor Videoberechnung die offenen Punkte beheben.'];
 for(const punkt of bericht.pruefungen||[]){
  zeilen.push((punkt.ok?'OK · ':'PRÜFEN · ')+punkt.name+': '+punkt.hinweis);
  if(!punkt.ok)zeilen.push('Nächster Schritt: '+(punkt.handlung||'Einstellung prüfen.'));
 }
 zeilen.push('Originaldateien werden durch diese Prüfung nicht verändert.');
 zeilen.push('Technische Einzelheiten:\n'+JSON.stringify(bericht,null,2));
 return zeilen.join('\n\n');
}
async function diagnose(){try{el('diagnose').textContent=diagnoseText(await api('/diagnose',undefined,60000));}
catch(e){el('diagnose').textContent=e.message;}}
let statusLaeuft=false;
async function status(){
 if(statusLaeuft)return;
 statusLaeuft=true;
 try{let r=await api('/status');
 if(r.fehler)throw Error(r.fehler);
 fortschrittAnzeigen('vorbereitungsbar','vorbereitung-wert',r.vorbereitung);
 fortschrittAnzeigen('stapelbar','stapel-wert',r.stapel);
 fortschrittAnzeigen('videobar','video-wert',r.video);
 auftragszahlen(r.jobs);
 el('phase').textContent=(r.event.phase||'Bereit')+' · '+(r.event.titel||'');
 el('jobs').textContent=JSON.stringify(r.jobs,null,2);el('log').textContent=(r.messages||[]).join('\n');
 el('sensoren').textContent=JSON.stringify(r.sensoren||{},null,2);
 el('ready').textContent=r.jobs.BEREIT||0;el('wait').textContent=r.jobs.WARTET||0;
 if(!el('downloads').dataset.ready){
  for(let id of ['downloads','arbeitsordner','format','kategorie','theme'])el(id).value=r.cfg[id];
  themaWaehlen();formatHinweis();
  el('downloads').dataset.ready='1';
 }
 el('status').textContent=r.andere_instanz?'Arbeitet im anderen Fenster':r.active?'In Arbeit':'Bereit / pausiert';
}catch(e){el('status').textContent='Anzeige veraltet: '+e.message;}
 finally{statusLaeuft=false;setTimeout(status,1500);}}
for(let [id,list] of [['format',['BREI','HOCH','QUAD','KLAS','4K']],
['kategorie',['PROVOWARE','CODING','THEMA']],
['theme',['cyan','violett','gruen','orange']]]){
 el(id).innerHTML=list.map(x=>'<option>'+x+'</option>').join('');
}
formatHinweis();status();diagnose();
</script></body></html>'''


class Bedienung:
    def __init__(self, cfg, config_path):
        self.cfg = konfigurieren(cfg)
        self.config_path = Path(config_path)
        self.service = None
        self.thread = None
        self.messages = deque(maxlen=20)
        self.event = {"phase": "bereit", "prozent": 0}
        self.vorbereitung = {"prozent": None}
        self.stapel = {"prozent": None}
        self.video = {"prozent": None}
        self.lock = threading.RLock()

    def _meldung(self, msg):
        with self.lock:
            self.messages.appendleft(str(msg))

    def _fortschritt(self, value):
        with self.lock:
            self.event = value
            phase = value.get("phase")
            if phase == "vorbereiten":
                self.vorbereitung = value
            elif phase in {"stapel", "pausiert_ressourcen"}:
                self.stapel = value
            elif phase in {"video_start", "rendern", "video_pruefen", "archivieren",
                           "video_fertig", "video_pausiert"}:
                self.video = value

    def _anderer_schreiber(self):
        """Vorhandene Kern-Sperre nur prüfen; niemals anlegen/löschen."""
        pfad = Path(self.cfg["arbeitsordner"]).expanduser().absolute() / "PROTOKOLLE" / "dienst.lock"
        if any(p.is_symlink() for p in (pfad, *pfad.parents)):
            raise RuntimeError("Unsicherer Sperrpfad: symbolische Verknüpfung; Arbeitsordner prüfen.")
        try:
            fd = os.open(pfad, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
        except FileNotFoundError:
            return False
        with os.fdopen(fd, "rb") as stream:
            if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
                raise RuntimeError("Sperrdatei ist nicht regulär; keine Verarbeitung starten.")
            try:
                fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                return True
            fcntl.flock(stream.fileno(), fcntl.LOCK_UN)
        return False

    def status(self):
        with self.lock:
            fehler = None
            aktiv = bool(self.thread and self.thread.is_alive())
            andere = False
            try:
                andere = not aktiv and self._anderer_schreiber()
                info = self.service.status() if aktiv and self.service else self._gespeicherter_status()
            except (RuntimeError, OSError, ValueError, KeyError, TypeError) as exc:
                info = {"auftraege": {}}
                fehler = "Auftrags-/Sperrstand nicht lesbar; Original bleibt erhalten: " + str(exc)
            unbekannt = {"prozent": None}
            event = {"phase": "Verarbeitung im anderen Fenster", "prozent": None} if andere else self.event
            return {"cfg": self.cfg, "jobs": info["auftraege"], "event": event, "fehler": fehler,
                    "vorbereitung": unbekannt if andere else self.vorbereitung,
                    "stapel": unbekannt if andere else self.stapel,
                    "video": unbekannt if andere else self.video,
                    "messages": list(self.messages), "sensoren": info.get("sensoren", {}),
                    "active": aktiv, "andere_instanz": andere}

    def _gespeicherter_status(self):
        """Aktuellen Journalstand lesen, ohne Workflow/Ordner/Dateien anzulegen."""
        pfad = Path(self.cfg["arbeitsordner"]).expanduser().absolute() / "PROTOKOLLE" / "auftraege.json"
        if any(p.is_symlink() for p in (pfad, *pfad.parents)):
            raise RuntimeError("Unsicherer Journalpfad: symbolische Verknüpfung.")
        journal = lesen(pfad, {"schema": 1, "auftraege": {}})
        if journal.get("schema") != 1 or not isinstance(journal.get("auftraege"), dict):
            raise RuntimeError("Unbekanntes Auftragsjournal.")
        counts = {}
        for job in journal["auftraege"].values():
            if not isinstance(job, dict) or not isinstance(job.get("status"), str):
                raise RuntimeError("Ungültiger gespeicherter Auftrag.")
            key = job["status"]
            counts[key] = counts.get(key, 0) + 1
        return {"auftraege": counts}

    def einstellungen(self, data):
        with self.lock:
            if not (self.thread and self.thread.is_alive()) and self._anderer_schreiber():
                raise RuntimeError("Anderes Fenster verarbeitet diesen Arbeitsordner. Einstellungen dort ändern.")
            cfg = konfigurieren({**self.cfg, **data})
            medienaenderung = any(cfg[k] != self.cfg[k] for k in cfg if k != "theme")
            if self.thread and self.thread.is_alive() and medienaenderung:
                raise RuntimeError("Während der Verarbeitung nur das Farbschema ändern.")
            if medienaenderung and not Path(cfg["downloads"]).expanduser().is_dir():
                raise ValueError("Downloads-Ordner existiert nicht.")
            json_sicher(self.config_path, cfg)
            self.cfg = cfg

    def ruecksetzen(self, modus, gruppe):
        with self.lock:
            if (self.thread and self.thread.is_alive()) or self._anderer_schreiber():
                raise RuntimeError("Vor dem Rücksetzen Verarbeitung sicher stoppen und Ende abwarten.")
            if modus == "zuruecksetzen":
                cfg, backup = zuruecksetzen(self.config_path, self.cfg, gruppe)
                meldung = "Auswahl zurückgesetzt. Bisherige Einstellungen gesichert: " + backup
            elif modus == "wiederherstellen":
                cfg = wiederherstellen(self.config_path, self.cfg)
                meldung = "Zurückgesetzte Werte wiederhergestellt. Ordner und Medien unverändert."
            else:
                raise ValueError("Unbekannte Rücksetzaktion.")
            self.cfg = cfg
            return {"cfg": {k:cfg[k] for k in ("theme","format","kategorie")}, "meldung": meldung}

    def aktion(self, mode):
        with self.lock:
            if not (self.thread and self.thread.is_alive()) and self._anderer_schreiber():
                raise RuntimeError("Anderes Fenster verarbeitet diesen Arbeitsordner. Dort sicher stoppen; hier nur ansehen.")
            if mode == "stop":
                if not (self.thread and self.thread.is_alive()):
                    return "Keine laufende Verarbeitung in diesem Fenster."
                if self.service:
                    self.service.stop.set()
                return "Stopp angefordert. Auftrag wird gesichert."
            if mode not in {"prepare", "batch", "once", "watch"}:
                raise ValueError("Unbekannter Ablauf.")
            if self.thread and self.thread.is_alive():
                raise RuntimeError("Ein anderer Vorgang läuft bereits.")
            self.service = Workflow(self.cfg, self._meldung, self._fortschritt)
            service = self.service

            def arbeit():
                try:
                    if mode == "watch":
                        service.beobachten()
                    else:
                        service.sperren()
                        try:
                            if mode in {"prepare", "once"}:
                                service.vorbereiten()
                            if mode in {"batch", "once"}:
                                service.stapel()
                        finally:
                            service.freigeben()
                except Exception as exc:
                    self._meldung("Fehler: " + str(exc))
            self.thread = threading.Thread(target=arbeit, daemon=True)
            self.thread.start()
            return "Gestartet: " + mode


def starten(cfg, config_path, port=0, browser=True, bereit=None):
    bedienung = Bedienung(cfg, config_path)
    token = secrets.token_urlsafe(32)

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_):
            return
        def antwort(self, data, status=200):
            body=json.dumps(data,ensure_ascii=False).encode()
            self.send_response(status)
            self.send_header("Content-Type","application/json; charset=utf-8")
            self.send_header("Cache-Control","no-store")
            self.send_header("X-Content-Type-Options","nosniff")
            self.send_header("Content-Security-Policy","default-src 'none'")
            self.send_header("Content-Length",str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        def zugriff(self):
            return (self.client_address[0]=="127.0.0.1" and
                    self.headers.get("Host")==f"127.0.0.1:{self.server.server_port}" and
                    parse_qs(urlsplit(self.path).query).get("token")==[token])
        def do_GET(self):
            if not self.zugriff():
                self.antwort({"fehler":"Zugriff verweigert"},403); return
            path=urlsplit(self.path).path
            if path=="/":
                body=HTML.encode()
                self.send_response(200)
                self.send_header("Content-Type","text/html; charset=utf-8")
                self.send_header("Cache-Control","no-store")
                self.send_header("X-Content-Type-Options","nosniff")
                self.send_header("Content-Security-Policy",
                                 "default-src 'self' 'unsafe-inline'; connect-src 'self'; frame-ancestors 'none'")
                self.send_header("Content-Length",str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            elif path=="/status": self.antwort(bedienung.status())
            elif path=="/diagnose": self.antwort(pruefen(cfg=bedienung.cfg))
            else: self.antwort({"fehler":"Seite nicht gefunden"},404)
        def do_POST(self):
            if not self.zugriff() or self.headers.get("Origin") not in (
                None, f"http://127.0.0.1:{self.server.server_port}"):
                self.antwort({"fehler":"Zugriff verweigert"},403); return
            if self.headers.get("Content-Type","").split(";")[0]!="application/json":
                self.antwort({"fehler":"Nur JSON erlaubt"},415); return
            try:
                length=int(self.headers.get("Content-Length","0"))
                if not 1<=length<=4096: raise ValueError("Ungültige Eingabelänge.")
                data=json.loads(self.rfile.read(length))
                if not isinstance(data,dict): raise ValueError("Ungültige Daten.")
                path=urlsplit(self.path).path
                if path=="/aktion": value={"meldung":bedienung.aktion(data.get("mode"))}
                elif path=="/ordnerwahl":
                    feld = data.get("feld")
                    if feld not in {"downloads", "arbeitsordner"}:
                        raise ValueError("Unbekannter Ordnerbereich.")
                    ziel = ordner_waehlen(feld, bedienung.cfg[feld])
                    value = {"pfad": ziel, "meldung": (
                        "Ordner übernommen; Einstellungen bitte speichern." if ziel
                        else "Auswahl abgebrochen, Einstellungen unverändert.")}
                elif path=="/ruecksetzen":
                    value=bedienung.ruecksetzen(data.get("modus"),data.get("gruppe"))
                elif path=="/einstellungen":
                    if not isinstance(data.get("cfg"),dict): raise ValueError("Einstellungen fehlen.")
                    bedienung.einstellungen(data["cfg"])
                    value={"meldung":"Einstellungen gespeichert."}
                else:
                    self.antwort({"fehler":"Seite nicht gefunden"},404); return
                self.antwort(value)
            except (ValueError,RuntimeError,OSError) as exc:
                self.antwort({"fehler":str(exc)},400)

    server=ThreadingHTTPServer(("127.0.0.1",port),Handler)
    server.daemon_threads=True
    url=f"http://127.0.0.1:{server.server_port}/?token={token}"
    print("Lokale Bedienoberfläche: "+url,flush=True)
    if bereit is not None:
        bereit(server, url)
    if browser: webbrowser.open(url)
    try: server.serve_forever(poll_interval=.3)
    finally:
        if bedienung.service: bedienung.service.stop.set()
        server.server_close()
