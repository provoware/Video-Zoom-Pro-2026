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
import time
import webbrowser
from collections import deque
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from .core import Workflow, konfigurieren, json_sicher, lesen
from .diagnose import pruefen
from .einstellungen_sicher import zuruecksetzen, wiederherstellen


def ordner_waehlen(feld: str, startwert: str, stop=None) -> str | None:
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
        if stop is None:
            ergebnis = subprocess.run(befehl, capture_output=True, text=True,
                                     check=False, timeout=120)
        else:
            with subprocess.Popen(befehl,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True) as proc:
                deadline=time.monotonic()+120
                try:
                    while True:
                        if stop.is_set() or time.monotonic()>=deadline:return None
                        try:
                            out,err=proc.communicate(timeout=.2)
                            ergebnis=subprocess.CompletedProcess(befehl,proc.returncode,out,err)
                            break
                        except subprocess.TimeoutExpired:continue
                finally:
                    if proc.poll() is None:
                        proc.terminate()
                        try:proc.wait(timeout=3)
                        except subprocess.TimeoutExpired:proc.kill();proc.wait(timeout=3)
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
[hidden]{display:none!important}
.main-actions{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,180px),1fr));gap:8px;position:relative;background:var(--bg);padding:8px 0}
.main-actions button{margin:0;font-size:.94rem}
article{scroll-margin-top:10rem}
.flow{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,170px),1fr));gap:8px;margin:12px 0}
.flow-step{min-width:0;border:1px solid var(--line);border-radius:10px;padding:9px 12px;background:var(--panel);color:var(--muted)}
.flow-step strong{display:block;color:var(--text)}
.flow-step[aria-current="step"]{border:3px solid var(--accent);padding:7px 10px;background:rgba(var(--accent-rgb),.12)}
.next-step{margin:8px 0 12px;border-left:4px solid var(--focus);padding:9px 12px;background:var(--panel);overflow-wrap:anywhere}
.scan-switch{display:flex;align-items:flex-start;gap:12px;border:1px solid var(--line);padding:12px;border-radius:10px;min-height:66px;cursor:pointer}
.scan-switch input{display:block;flex:0 0 28px;width:28px;height:28px;min-height:28px;padding:0;margin:3px 0 0;accent-color:var(--accent)}
.scan-switch small{display:block;font-weight:400;line-height:1.4;margin-top:3px}
button:disabled{cursor:wait;filter:none;opacity:1;border-style:dashed}
.header-tools button{width:auto;font-size:.88rem;min-width:0;margin:0}
.scan-note{font-size:.88rem;color:var(--muted);overflow-wrap:anywhere}
dialog{max-width:min(620px,94vw);max-height:90vh;overflow:auto;border:2px solid var(--accent);border-radius:14px;background:var(--panel);color:var(--text);padding:20px}
dialog::backdrop{background:rgba(0,0,0,.65)}
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
#auftraege-karte{grid-column:1/-1}
.job-card{margin:12px 0;overflow-wrap:anywhere}
.job-card summary{display:block;min-height:44px;padding:8px 0;cursor:pointer;font-weight:700}
.job-card video{display:block;width:100%;max-width:640px;max-height:360px;margin:12px 0;background:#000}
.job-card button{white-space:normal;overflow-wrap:anywhere}
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
<section class="main-actions" aria-label="Wichtigste Aktionen">
<button data-ruhe onclick="aktion('prepare')" title="Fertige Quellen nach gespeicherter Scanwahl prüfen">Eingang prüfen · (i)</button>
<button data-ruhe onclick="aktion('batch')" title="Nur vorbereitete Songs verarbeiten">Videos erstellen · (i)</button>
<button class="warn" onclick="aktion('stop')" title="Eigenen Vorgang anhalten und Zustand sichern">Sicher stoppen · (i)</button>
<button onclick="beenden()" title="Daten sichern und den lokalen Server schließen">Speichern &amp; beenden · (i)</button>
</section>
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
<section class="flow" aria-label="Arbeitsablauf">
<div class="flow-step" id="schritt-1"><strong>1 · Quellen wählen</strong>Audio und Bilder getrennt</div>
<div class="flow-step" id="schritt-2"><strong>2 · Eingang prüfen</strong>Zuordnung und Vorschau</div>
<div class="flow-step" id="schritt-3"><strong>3 · Video erstellen</strong>Mit Schutz der Originale</div>
<div class="flow-step" id="schritt-4"><strong>4 · Prüfen &amp; ablegen</strong>Erst danach abgeschlossen</div>
</section>
<p id="naechster-schritt" class="next-step" role="status">Nächster Schritt: Ordner wählen und Quellen festlegen.</p>
<p id="hinweis" role="alert" aria-live="assertive"></p><div class="grid">
<article id="vorbereitung"><h2>1 · Songs vorbereiten</h2>
<p>WAV erkennen, Titel bereinigen, Bilder zuordnen.</p>
<details id="einrichtung" class="technical-details" open><summary id="einrichtung-titel">Ordner und erste Einrichtung</summary>
<ol aria-label="Erste Einrichtung"><li>Downloads- und eigenen Arbeitsordner wählen.</li><li>Einstellungen speichern und Systemprüfung ausführen.</li><li>WAV fertig herunterladen, Bilder im zugehörigen Songordner ablegen, dann vorbereiten.</li></ol>
<label for="downloads">Downloads-Ordner</label>
<div class="ordner"><input id="downloads" aria-label="Downloads-Ordnerpfad">
<button type="button" onclick="ordnerwahl('downloads')">📁 Ordner wählen</button></div>
<label for="arbeitsordner">Arbeitsordner</label>
<div class="ordner"><input id="arbeitsordner" aria-label="Arbeitsordnerpfad">
<button type="button" onclick="ordnerwahl('arbeitsordner')">📁 Ordner wählen</button></div>
<button id="ordner-einrichten" data-ruhe onclick="ordnerEinrichten()" title="Gewählte Ordner prüfen, fehlende Ordner sicher anlegen und Einstellungen speichern">Ordner prüfen &amp; anlegen · (i)</button>
<p id="ordner-status" class="scan-note" role="status">Ordner werden geprüft …</p>
</details><label class="scan-switch" for="audio_auto"><input id="audio_auto" type="checkbox" role="switch" checked onchange="scanModus()"><span>Audio automatisch suchen<small>Ein: fertige WAVs aus Downloads erkennen. Aus: WAV-Dateien selbst auswählen.</small></span></label>
<label class="scan-switch" for="bilder_auto"><input id="bilder_auto" type="checkbox" role="switch" checked onchange="scanModus()"><span>Bilder automatisch einlesen<small>Ein: Bilder aus dem zugehörigen Songordner. Aus: Bilder gezielt beim Song auswählen.</small></span></label>
<p id="scan-hinweis" class="scan-note">Automatik verarbeitet erst nach einem bewussten Start. Originale manueller Auswahlen bleiben erhalten.</p>
<button id="audio-waehlen" data-ruhe hidden onclick="audioAuswahl()" title="WAV-Dateien auswählen; nur geprüfte Arbeitskopien werden verarbeitet">WAV-Dateien auswählen · (i)</button>
<button id="fundliste-neu" data-ruhe onclick="resetFragen()" title="Fundliste sichern und neu einlesen; Originale und bearbeitete Aufträge bleiben erhalten">Fundliste zurücksetzen &amp; neu einlesen · (i)</button>
<label for="format">Videoformat</label><select id="format" onchange="formatHinweis()"></select><p class="format-hint" id="formatinfo">Format auswählen</p>
<label for="kategorie">Dateikategorie</label><select id="kategorie"></select>
<button onclick="speichern()">Einstellungen speichern</button>
<p><small>Während der Verarbeitung lässt sich nur das Farbschema speichern.</small></p>
<label for="resetgruppe">Ausgewählte Einstellungen zurücksetzen</label>
<select id="resetgruppe"><option value="ansicht">Nur Farbschema</option><option value="format">Nur Format und Kategorie</option><option value="bedienung">Farbschema, Format und Kategorie</option></select>
<button onclick="ruecksetzen(false)">Auswahl zurücksetzen · Sicherung anlegen</button>
<button onclick="ruecksetzen(true)">Letzte Rücksetzung zurücknehmen</button>
<p><small>Ordner, Medien und CPU-/RAM-Grenzen bleiben erhalten. Rücksetzen nur bei angehaltener Verarbeitung.</small></p>
<button data-ruhe onclick="aktion('prepare')">Songs vorbereiten</button>
<p><strong id="ready">0</strong> bereit · <strong id="wait">0</strong> warten</p>
</article><article id="stapel-karte"><h2>2 · Stapelverarbeitung</h2>
<p>Erst Bilder rückwärts und schnell, dann vorwärts mit sanften Kamerabewegungen.</p>
<button data-ruhe onclick="aktion('batch')">Stapel starten</button>
<button data-ruhe onclick="aktion('once')">Einmal alles ausführen</button>
<button data-ruhe onclick="aktion('watch')">Automatik einschalten</button>
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
</article>
<article id="auftraege-karte"><h2>Songs und nächste Schritte</h2>
<p class="card-subtitle">Song aufklappen. Die Vorschau zeigt die ersten bis zu zehn Sekunden; Originale und Produktionsstatus bleiben erhalten. Nach Medien- oder Formatänderungen die gespeicherte Vorschau neu erzeugen.</p>
<div id="auftragsliste"><p>Noch keine vorbereiteten Songs.</p></div>
</article>
<dialog id="fundreset-dialog" aria-labelledby="reset-titel"><h2 id="reset-titel">Fundliste neu aufbauen?</h2>
<p>Ungestartete Funde werden gesichert und neu eingelesen. Manuelle Auswahl, Originale, fertige Videos und bereits bearbeitete Aufträge bleiben erhalten.</p>
<p>Prüfsperren werden dadurch nicht aufgehoben. Bei laufender Verarbeitung zuerst sicher stoppen.</p>
<button type="button" onclick="resetStarten()">Fundliste sichern &amp; neu einlesen</button>
<button type="button" onclick="el('fundreset-dialog').close()">Abbrechen</button></dialog></div>
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
function ordnerAnzeige(info){
 if(!info)return;
 if(!el('einrichtung').dataset.bereit){
  el('einrichtung').open=!info.bereit;
  el('einrichtung').dataset.bereit='1';
 }
 el('einrichtung-titel').textContent=info.bereit?'Ordner und Einrichtung · bereit':'Ordner und Einrichtung · Handlung nötig';
 el('ordner-status').textContent=info.fehler||info.ordner.map(x=>x.name+': '+x.hinweis).join(' · ');
}
async function ordnerEinrichten(){try{const r=await api('/ordner',{cfg:formularCfg()});ordnerAnzeige(r.ordner);el('hinweis').textContent=r.meldung;}catch(e){el('hinweis').textContent=e.message;}}
function formularCfg(){
 const cfg={};for(let id of ['downloads','arbeitsordner','format','kategorie','theme'])cfg[id]=el(id).value;
 for(const id of ['audio_auto','bilder_auto'])cfg[id]=Boolean(el(id).checked);
 return cfg;
}
async function speichern(){try{
 const cfg=formularCfg();
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
let serverCfg=null,scanSpeichert=false,endeAngefordert=false;
function scanHinweise(gesperrt=false){
 const audio=Boolean(el('audio_auto').checked),bilder=Boolean(el('bilder_auto').checked);
 el('audio-waehlen').hidden=audio;
 el('audio_auto').disabled=el('bilder_auto').disabled=gesperrt||scanSpeichert;
 el('audio-waehlen').disabled=el('fundliste-neu').disabled=gesperrt;
 el('scan-hinweis').textContent='Audio: '+(audio?'automatisch aus Downloads':'manuell auswählen')+' · Bilder: '+(bilder?'automatisch aus dem Songordner':'manuell beim Song auswählen')+'. Originale manueller Auswahlen bleiben erhalten.';
 if(typeof document.querySelectorAll==='function')for(const button of document.querySelectorAll('[data-ruhe]'))button.disabled=gesperrt;
}
async function scanModus(){
 if(scanSpeichert)return;
 scanSpeichert=true;scanHinweise();
 try{
  const r=await api('/scanmodus',{audio_auto:Boolean(el('audio_auto').checked),bilder_auto:Boolean(el('bilder_auto').checked)});
  serverCfg=r.cfg;el('hinweis').textContent=r.meldung;
 }catch(e){
  if(serverCfg)for(const id of ['audio_auto','bilder_auto'])el(id).checked=serverCfg[id];
  el('hinweis').textContent=e.message;
 }finally{scanSpeichert=false;scanHinweise();}
}
async function audioAuswahl(){try{el('hinweis').textContent=(await api('/audioauswahl',{})).meldung;}catch(e){el('hinweis').textContent=e.message;}}
function resetFragen(){el('fundreset-dialog').showModal();}
async function resetStarten(){el('fundreset-dialog').close();await aktion('rescan');}
async function beenden(){
 try{
  await api('/einstellungen',{cfg:formularCfg()});
  el('hinweis').textContent=(await api('/beenden',{})).meldung;endeAngefordert=true;
 }catch(e){el('hinweis').textContent=e.message;}
}
function abfragePause(active){return document.hidden?15000:active?1500:5000;}
function arbeitsablauf(r){
 const jobs=r.jobs||{},phase=r.event.phase||'bereit';let step=1,text='Ordner und Quellen festlegen, dann Eingang prüfen.';
 if(r.active){
  step=phase==='archivieren'?4:['rendern','video_start','video_pruefen','video_fertig','vorschau'].includes(phase)?3:2;
  text=r.schliesst?'Anhalten, Daten sichern und Server beenden …':'Vorgang läuft. Bei Bedarf „Sicher stoppen“ wählen.';
 }else if(jobs.PRUEFEN||jobs.ARCHIV_WARTET){step=4;text='Betroffenen Song aufklappen. Ursache prüfen und danach bewusst erneut freigeben.';}
 else if(jobs.BEREIT){step=2;text='Bereite Songs: Vorschau ansehen oder Stapel starten.';}
 else if(jobs.WARTET){step=1;text=el('bilder_auto').checked?'Bilder im zugehörigen Songordner ablegen, danach Eingang prüfen.':'Beim wartenden Song „Bilder auswählen“ öffnen.';}
 else if(jobs.ARCHIVIERT){step=4;text='Videos geprüft und archiviert. Neue Quellen wählen oder sicher beenden.';}
 if(r.ordner&&!r.ordner.bereit){step=1;text='Ordner und Einrichtung öffnen, dann „Ordner prüfen & anlegen“ wählen.';}
 for(let i=1;i<=4;i++){if(i===step)el('schritt-'+i).setAttribute('aria-current','step');else el('schritt-'+i).removeAttribute('aria-current');}
 el('naechster-schritt').textContent='Nächster Schritt: '+text;
}
function fensterStarten(){
 const id=globalThis.crypto?.randomUUID?crypto.randomUUID():Date.now().toString(36)+Math.random().toString(36).slice(2);let seq=0;
 const melden=aktion=>{
  const data={id,seq:++seq,aktion,hidden:document.hidden};
  if(aktion==='weg'){data.cfg=formularCfg();data.base=serverCfg;}
  const blob=new Blob([JSON.stringify(data)],{type:'application/json'});
  navigator.sendBeacon('/fenster?token='+encodeURIComponent(token),blob);
 };
 melden('da');
 setInterval(()=>melden('da'),10000);
 document.addEventListener('visibilitychange',()=>melden('da'));
 window.addEventListener('pagehide',()=>melden('weg'));
}
const jobNodes=new Map();
const STATUSWORTE={BEREIT:'Bereit',WARTET:'Wartet',LAEUFT:'Video läuft',PRUEFEN:'Prüfung nötig',PAUSIERT:'Pausiert',FERTIG:'Video geprüft – Archiv offen',ARCHIV_WARTET:'Archivierung wartet',ARCHIVIERT:'Archiviert'};
async function auftragAktion(id,aktion){
 try{el('hinweis').textContent=(await api('/auftrag',{auftrag:id,aktion})).meldung;}
 catch(e){el('hinweis').textContent=e.message;}
}
function auftraegeAnzeigen(rows,gesperrt=false){
 const container=el('auftragsliste');
 if(!rows.length){container.textContent='Noch keine vorbereiteten Songs.';jobNodes.clear();return;}
 if(jobNodes.size===0)container.textContent='';
 const ids=new Set(rows.map(row=>row.id));
 for(const [id,node] of jobNodes){if(!ids.has(id)){node.box.remove();jobNodes.delete(id);}}
 for(const row of rows){
  let node=jobNodes.get(row.id);
  if(!node){
   const box=document.createElement('details');box.className='job-card technical-details';
   const title=document.createElement('summary'),hint=document.createElement('p');
   const previewButton=document.createElement('button'),releaseButton=document.createElement('button'),imagesButton=document.createElement('button');
   previewButton.type=releaseButton.type=imagesButton.type='button';
   imagesButton.textContent='Bilder auswählen · (i)';imagesButton.title='Bilder genau diesem Song als Arbeitskopien zuordnen.';
   imagesButton.addEventListener('click',()=>auftragAktion(row.id,'bilder'));
   previewButton.textContent='Vorschau erzeugen · (i)';previewButton.title='Erste bis zu zehn Sekunden, ohne Archivierung.';
   releaseButton.textContent='Nach Prüfung erneut freigeben · (i)';releaseButton.title='Unveränderte Quellen prüfen und automatische Versuche bewusst zurücksetzen.';
   previewButton.addEventListener('click',()=>auftragAktion(row.id,'vorschau'));
   releaseButton.addEventListener('click',()=>auftragAktion(row.id,'freigeben'));
   const preview=document.createElement('video');preview.controls=true;preview.preload='none';preview.hidden=true;
   preview.setAttribute('aria-label','Kurze Vorschau abspielen');
   box.append(title,hint,imagesButton,previewButton,releaseButton,preview);container.append(box);
   node={box,title,hint,imagesButton,previewButton,releaseButton,preview,source:''};jobNodes.set(row.id,node);
  }
  node.title.textContent=row.titel+' · '+(STATUSWORTE[row.status]||row.status)+' · '+row.format+' · '+row.bilder+' Bilder';
  node.hint.textContent=row.hinweis||'Vorschau ansehen oder den bereitstehenden Song im Stapel verarbeiten.';
  node.previewButton.disabled=gesperrt||!['BEREIT','PAUSIERT','PRUEFEN'].includes(row.status)||row.bilder<1;
  node.releaseButton.hidden=!['PAUSIERT','PRUEFEN'].includes(row.status);
  node.releaseButton.disabled=gesperrt;
  node.imagesButton.hidden=Boolean(el('bilder_auto').checked)||!['WARTET','BEREIT'].includes(row.status);
  node.imagesButton.disabled=gesperrt;
  node.preview.hidden=!row.vorschau;
  const source=row.vorschau?'/vorschau?token='+encodeURIComponent(token)+'&auftrag='+encodeURIComponent(row.id)+'&version='+encodeURIComponent(row.vorschau_id):'';
  if(source!==node.source){
   if(source)node.preview.src=source;else node.preview.removeAttribute('src');
   node.source=source;
  }
 }
}
let letzteEinzelmeldung="";
let statusLaeuft=false;
async function status(){
 if(statusLaeuft)return;
 statusLaeuft=true;let pause=5000,weiter=true;
 try{let r=await api('/status');
 pause=abfragePause(r.active);
 if(r.fehler)throw Error(r.fehler);
 serverCfg=r.cfg;
 ordnerAnzeige(r.ordner);
 if(r.schliesst)endeAngefordert=true;
 if(r.beenden_fehler){endeAngefordert=false;el('hinweis').textContent='Speichern fehlgeschlagen. Server bleibt geöffnet: '+r.beenden_fehler;}
 if(!scanSpeichert)for(const id of ['audio_auto','bilder_auto'])el(id).checked=r.cfg[id]!==false;
 scanHinweise(Boolean(r.active||r.andere_instanz||r.schliesst));
 arbeitsablauf(r);
 fortschrittAnzeigen('vorbereitungsbar','vorbereitung-wert',r.vorbereitung);
 fortschrittAnzeigen('stapelbar','stapel-wert',r.stapel);
 fortschrittAnzeigen('videobar','video-wert',r.video);
 if(r.einzelmeldung&&r.einzelmeldung.id!==letzteEinzelmeldung){el("hinweis").textContent=r.einzelmeldung.text;letzteEinzelmeldung=r.einzelmeldung.id;}
 auftragszahlen(r.jobs);
 auftraegeAnzeigen(r.liste||[],Boolean(r.active||r.andere_instanz));
 el('phase').textContent=(r.event.phase||'Bereit')+' · '+(r.event.titel||'');
 el('jobs').textContent=JSON.stringify(r.jobs,null,2);el('log').textContent=(r.messages||[]).join('\n');
 el('sensoren').textContent=JSON.stringify(r.sensoren||{},null,2);
 el('ready').textContent=r.jobs.BEREIT||0;el('wait').textContent=r.jobs.WARTET||0;
 if(!el('downloads').dataset.ready){
  for(let id of ['downloads','arbeitsordner','format','kategorie','theme'])el(id).value=r.cfg[id];
  themaWaehlen();formatHinweis();
  el('downloads').dataset.ready='1';
 }
 el('status').textContent=r.schliesst?'Wird gesichert und beendet':r.andere_instanz?'Arbeitet im anderen Fenster':r.active?'In Arbeit':'Bereit / pausiert';
}catch(e){
 if(endeAngefordert){el('status').textContent='Verbindung geschlossen';el('hinweis').textContent='Beenden wurde angefordert. Server ist nicht mehr erreichbar. Beim nächsten Start den gespeicherten Stand kontrollieren.';weiter=false;}
 else{el('status').textContent='Anzeige veraltet: '+e.message;pause=15000;}
 }
 finally{statusLaeuft=false;if(weiter)setTimeout(status,pause);}}
for(let [id,list] of [['format',['BREI','HOCH','QUAD','KLAS','4K']],
['kategorie',['PROVOWARE','CODING','THEMA']],
['theme',['cyan','violett','gruen','orange']]]){
 el(id).innerHTML=list.map(x=>'<option>'+x+'</option>').join('');
}
formatHinweis();status();diagnose();
if(location.protocol==='http:')fensterStarten();
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
        self.einzelmeldung = None
        self.schliesst = False
        self.beenden_fehler = None
        self.dialog_stop = threading.Event()
        self.lebenszyklus = None
        self._status_cache = None

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
            try:
                from .eingang import ordner_pruefen
                ordner = ordner_pruefen(self.cfg)
            except (OSError,ValueError,RuntimeError) as exc:
                ordner = {"bereit":False,"fehler":str(exc),"ordner":[]}
            return {"ordner":ordner,"cfg": self.cfg, "jobs": info["auftraege"], "liste": info.get("liste", []), "event": event, "fehler": fehler,
                    "vorbereitung": unbekannt if andere else self.vorbereitung,
                    "stapel": unbekannt if andere else self.stapel,
                    "video": unbekannt if andere else self.video,
                    "messages": list(self.messages), "sensoren": info.get("sensoren", {}),
                    "active": aktiv, "andere_instanz": andere, "einzelmeldung": self.einzelmeldung, "schliesst": self.schliesst,
                    "beenden_fehler": self.beenden_fehler, "scan_pause": info.get("scan_pause", self.cfg["intervall"])}

    def _gespeicherter_status(self):
        """Aktuellen Journalstand lesen, ohne Workflow/Ordner/Dateien anzulegen."""
        pfad = Path(self.cfg["arbeitsordner"]).expanduser().absolute() / "PROTOKOLLE" / "auftraege.json"
        if any(p.is_symlink() for p in (pfad, *pfad.parents)):
            raise RuntimeError("Unsicherer Journalpfad: symbolische Verknüpfung.")
        try:
            st = pfad.stat()
            signature = (str(pfad),st.st_ino,st.st_size,st.st_mtime_ns,st.st_ctime_ns)
        except FileNotFoundError:
            signature = (str(pfad),None)
        if self._status_cache is not None and self._status_cache[0] == signature:
            return self._status_cache[1]
        journal = lesen(pfad, {"schema": 1, "auftraege": {}})
        if journal.get("schema") != 1 or not isinstance(journal.get("auftraege"), dict):
            raise RuntimeError("Unbekanntes Auftragsjournal.")
        counts = {}
        for job in journal["auftraege"].values():
            if not isinstance(job, dict) or not isinstance(job.get("status"), str):
                raise RuntimeError("Ungültiger gespeicherter Auftrag.")
            key = job["status"]
            counts[key] = counts.get(key, 0) + 1
        from .auftraege import uebersicht
        value = {"auftraege": counts, "liste": uebersicht(journal["auftraege"], self.cfg)}
        self._status_cache = (signature,value)
        return value

    def einstellungen(self, data, beim_beenden=False):
        with self.lock:
            if self.schliesst and not beim_beenden:raise RuntimeError("Programm wird beendet; Einstellungen gesperrt.")
            if not (self.thread and self.thread.is_alive()) and self._anderer_schreiber():
                raise RuntimeError("Anderes Fenster verarbeitet diesen Arbeitsordner. Einstellungen dort ändern.")
            cfg = konfigurieren({**self.cfg, **data})
            medienaenderung = any(cfg[k] != self.cfg[k] for k in cfg if k != "theme")
            if self.thread and self.thread.is_alive() and medienaenderung:
                raise RuntimeError("Während der Verarbeitung nur das Farbschema ändern.")
            if not (self.thread and self.thread.is_alive()):
                from .eingang import ordner_pruefen
                ordner_pruefen(cfg,anlegen=True)
            json_sicher(self.config_path, cfg)
            self.cfg = cfg
            self._status_cache = None

    def ruecksetzen(self, modus, gruppe):
        with self.lock:
            if self.schliesst:raise RuntimeError("Programm wird beendet.")
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
            self._status_cache = None
            return {"cfg": {k:cfg[k] for k in ("theme","format","kategorie")}, "meldung": meldung}

    def _start_worker(self, funktion, text, *, eigene_sperre=True):
        with self.lock:
            if self.schliesst:raise RuntimeError("Programm wird bereits beendet.")
            if self.thread and self.thread.is_alive():
                raise RuntimeError("Verarbeitung läuft. Zuerst im aktiven Fenster sicher stoppen.")
            if self._anderer_schreiber():
                raise RuntimeError("Anderes Fenster: Verarbeitung läuft. Dort sicher stoppen; hier nur ansehen.")
            self.service = Workflow(self.cfg, self._meldung, self._fortschritt)
            service = self.service
            self.einzelmeldung = None
            self.event = {"phase": "auswahl", "titel": text, "prozent": None}
            def arbeit():
                meldung = "Vorgang erfolgreich abgeschlossen. Gespeicherter Stand ist aktuell."
                try:
                    if eigene_sperre:service.sperren()
                    try:funktion(service)
                    finally:
                        if eigene_sperre and service.lock_file is not None:
                            try:service.speichern()
                            finally:service.freigeben()
                except Exception as exc:
                    meldung = "Vorgang angehalten: " + str(exc)
                finally:
                    with self.lock:
                        self.einzelmeldung = {"id":secrets.token_hex(8),"text":meldung}
                        self._status_cache = None
                    self._meldung(meldung)
            self.thread = threading.Thread(target=arbeit,daemon=True,name='videozoom-auftrag')
            self.thread.start()
            return text

    def auftrag(self, key, aktion):
        if not isinstance(key,str) or not 1<=len(key)<=128:raise ValueError("Ungültiger Auftrag.")
        if aktion not in {"vorschau","freigeben","bilder"}:raise ValueError("Unbekannte Einzelaktion.")
        def arbeit(service):
            if key not in service.zustand["auftraege"]:raise ValueError("Auftrag nicht gefunden.")
            if aktion=="vorschau":
                from .vorschau import erzeugen
                erzeugen(service,key)
            elif aktion=="freigeben":
                from .auftraege import freigeben
                freigeben(service,key)
            else:
                from .eingang import dateien_waehlen,uebernehmen
                if service.cfg["bilder_auto"]:raise ValueError("Zuerst Bildauswahl auf Manuell stellen und speichern.")
                files=dateien_waehlen('bilder',service.downloads,service.stop)
                if files:uebernehmen(service,'bilder',files,key)
                else:service.melden("Bildauswahl abgebrochen; bisherige Auswahl bleibt erhalten.")
        return self._start_worker(arbeit,"Einzelauftrag wird bearbeitet.")

    def audio_waehlen(self):
        def arbeit(service):
            from .eingang import dateien_waehlen,uebernehmen
            if service.cfg["audio_auto"]:raise ValueError("Zuerst Audioauswahl auf Manuell stellen und speichern.")
            files=dateien_waehlen('audio',service.downloads,service.stop)
            if files:uebernehmen(service,'audio',files)
            else:service.melden("Audioauswahl abgebrochen; bisherige Auswahl bleibt erhalten.")
        return self._start_worker(arbeit,"WAV-Dateiauswahl wird geöffnet.")

    def vorschau_datei(self, key):
        from .vorschau import datei
        with self.lock:
            pfad = Path(self.cfg["arbeitsordner"]).expanduser().absolute() / "PROTOKOLLE" / "auftraege.json"
            if any(p.is_symlink() for p in (pfad, *pfad.parents)):
                raise RuntimeError("Unsicherer Journalpfad.")
            journal = lesen(pfad, {"schema": 1, "auftraege": {}})
            if journal.get("schema") != 1 or not isinstance(journal.get("auftraege"), dict):
                raise RuntimeError("Unbekanntes Auftragsjournal.")
            job = journal["auftraege"].get(key)
            if not isinstance(job, dict):
                raise ValueError("Auftrag nicht gefunden.")
            return datei(Path(self.cfg["arbeitsordner"]).expanduser().absolute(), job)

    def aktion(self, mode):
        if mode=="stop":
            with self.lock:
                if not (self.thread and self.thread.is_alive()):
                    if self._anderer_schreiber():raise RuntimeError("Anderes Fenster: Verarbeitung dort sicher stoppen.")
                    return "Keine laufende Verarbeitung in diesem Fenster."
                if self.service:self.service.stop.set()
                return "Stopp angefordert. Auftrag wird gesichert."
        if mode not in {"prepare","batch","once","watch","rescan"}:raise ValueError("Unbekannter Ablauf.")
        def arbeit(service):
            if mode=="watch":service.beobachten()
            elif mode=="rescan":
                from .eingang import fundliste_neu
                fundliste_neu(service)
            else:
                if mode in {"prepare","once"}:service.vorbereiten()
                if mode in {"batch","once"}:service.stapel()
        texte={"prepare":"Eingang wird geprüft.","batch":"Videostapel wird gestartet.",
               "once":"Eingang und Videos werden verarbeitet.","watch":"Automatik gestartet.",
               "rescan":"Fundliste wird gesichert und neu eingelesen."}
        return self._start_worker(arbeit,texte[mode],eigene_sperre=mode!="watch")



def starten(cfg, config_path, port=0, browser=True, bereit=None):
    bedienung = Bedienung(cfg, config_path)
    token = secrets.token_urlsafe(32)

    class Handler(BaseHTTPRequestHandler):
        def setup(self):
            super().setup()
            self.connection.settimeout(15)
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
            elif path=="/vorschau":
                try:
                    from .vorschau import senden
                    key = parse_qs(urlsplit(self.path).query).get("auftrag", [""])[0]
                    senden(self, bedienung.vorschau_datei(key))
                except (OSError, RuntimeError, ValueError, KeyError, TypeError) as exc:
                    self.antwort({"fehler": str(exc)}, 400)
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
                elif path=="/fenster":
                    leben.fenster(data.get("id"),data.get("aktion"),data.get("hidden",False),data.get("cfg"),data.get("base"),data.get("seq"))
                    value={"meldung":"Fensterstatus übernommen."}
                elif path=="/beenden":
                    leben.anfordern()
                    value={"meldung":"Anhalten und Speichern angefordert. Server beendet sich anschließend."}
                elif path=="/ordner":
                    if not isinstance(data.get("cfg"),dict):raise ValueError("Ordnerangaben fehlen.")
                    bedienung.einstellungen(data["cfg"])
                    from .eingang import ordner_pruefen
                    value={"meldung":"Ordner geprüft, fehlende sichere Ordner angelegt und Einstellungen gespeichert.","ordner":ordner_pruefen(bedienung.cfg)}
                elif path=="/scanmodus":
                    if set(data)!={"audio_auto","bilder_auto"}:raise ValueError("Nur die beiden Scan-Schalter ändern.")
                    bedienung.einstellungen(data)
                    value={"meldung":"Scanwahl gespeichert.","cfg":bedienung.cfg}
                elif path=="/audioauswahl":value={"meldung":bedienung.audio_waehlen()}
                elif path=="/auftrag": value={"meldung":bedienung.auftrag(data.get("auftrag"), data.get("aktion"))}
                elif path=="/ordnerwahl":
                    feld = data.get("feld")
                    if feld not in {"downloads", "arbeitsordner"}:
                        raise ValueError("Unbekannter Ordnerbereich.")
                    ziel = ordner_waehlen(feld, bedienung.cfg[feld],bedienung.dialog_stop)
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
    from .lebenszyklus import Lebenszyklus,abbruchsignale
    leben=Lebenszyklus(bedienung,server,browser=browser)
    bedienung.lebenszyklus=leben
    server.lebenszyklus=leben
    url=f"http://127.0.0.1:{server.server_port}/?token={token}"
    print("Lokale Bedienoberfläche: "+url,flush=True)
    if bereit is not None:
        bereit(server, url)
    leben.starten()
    if browser:webbrowser.open(url)
    with abbruchsignale(leben.angefordert):
        try:server.serve_forever(poll_interval=.3)
        finally:
            leben.abschliessen()
            server.server_close()
