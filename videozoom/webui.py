"""Sichere lokale Browser-Oberfläche: kein Tk, kein Netzwerkdienst nach außen."""
from __future__ import annotations
import json
import secrets
import threading
import webbrowser
from collections import deque
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from .core import Workflow, konfigurieren, json_sicher
from .diagnose import pruefen

HTML = r'''<!doctype html><html lang="de"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>PROVOWARE · Video Zoom Pro</title>
<style>
:root{font:18px/1.5 system-ui,sans-serif;color-scheme:dark;background:#111825;color:#f5f8fc}
*{box-sizing:border-box}body{max-width:1190px;margin:auto;padding:clamp(12px,3vw,30px)}
h1{margin:0;font-size:clamp(1.6rem,4vw,2.5rem)}h2{font-size:1.22rem;margin:0 0 12px}
small{color:#cad6e5}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,310px),1fr));gap:14px;margin:16px 0}
article{border:1px solid #5c718f;border-radius:14px;background:#1b293c;padding:18px}
input,select,button{display:block;width:100%;padding:10px;margin:8px 0;border-radius:9px;
 border:2px solid #8da7c1;background:#0d192a;color:#fff;font:inherit;min-height:45px}
label{display:block;margin-top:12px;font-weight:650}
button{background:#245f96;border-color:#80baff;font-weight:700;cursor:pointer}
button:hover{background:#3576ac}button:focus-visible,input:focus-visible,select:focus-visible{outline:4px solid #ffdb7a;outline-offset:2px}
button.warn{background:#873c40}progress{width:100%;height:24px;accent-color:#6ee3b2}
pre{font:0.82rem/1.4 monospace;white-space:pre-wrap;overflow:auto;word-break:break-word;
 max-height:200px;padding:12px;background:#0a1524;border-radius:9px}
#status{display:inline-block;padding:5px 12px;border-radius:10px;background:#29573c;margin:10px 0}
@media(max-width:520px){article{padding:12px}}
</style></head><body>
<h1>🎬 PROVOWARE · Video Zoom Pro</h1><small>Lokal · offline · ohne Tk · zwei getrennte Workflows</small>
<p id="status">Bereit</p><div class="grid">
<article><h2>1 · Songs vorbereiten</h2>
<p>WAV erkennen, Titel bereinigen, Bilder zuordnen.</p>
<label for="downloads">Downloads-Ordner</label><input id="downloads">
<label for="arbeitsordner">Arbeitsordner</label><input id="arbeitsordner">
<label for="format">Videoformat</label><select id="format"></select>
<label for="kategorie">Dateikategorie</label><select id="kategorie"></select>
<button onclick="speichern()">Einstellungen speichern</button>
<button onclick="aktion('prepare')">Songs vorbereiten</button>
<p><strong id="ready">0</strong> bereit · <strong id="wait">0</strong> warten</p>
</article><article><h2>2 · Stapelverarbeitung</h2>
<p>Erst Bilder rückwärts und schnell, dann vorwärts mit sanften Kamerabewegungen.</p>
<button onclick="aktion('batch')">Stapel starten</button>
<button onclick="aktion('once')">Einmal alles ausführen</button>
<button onclick="aktion('watch')">Automatik einschalten</button>
<button class="warn" onclick="aktion('stop')">Sicher stoppen</button>
<label for="bar">Fortschritt des aktuellen Vorgangs</label><progress id="bar" value="0" max="100"></progress>
<p id="phase">Kein Vorgang aktiv</p>
</article><article><h2>3 · Diagnose</h2>
<p>CPU-Ziel: maximal 30 % der zugänglichen Prozessorkapazität. Ohne nachgewiesene Grenze kein Rendern.</p>
<button onclick="diagnose()">Systemprüfung ausführen</button><pre id="diagnose">Noch nicht geprüft</pre>
<p><small>Die Vorbereitung kann unabhängig von der CPU-Grenze weiterlaufen.</small></p>
</article><article><h2>4 · Protokoll</h2><pre id="jobs">Noch keine Aufträge.</pre><pre id="log">Bereit.</pre>
</article></div>
<script>
const token=new URL(location.href).searchParams.get('token');
const el=id=>document.getElementById(id);
async function api(path,data){
 const r=await fetch(path+'?token='+encodeURIComponent(token),{method:data?'POST':'GET',
 headers:data?{'Content-Type':'application/json'}:{},body:data?JSON.stringify(data):undefined,cache:'no-store'});
 const v=await r.json();if(!r.ok)throw Error(v.fehler||'Aktion fehlgeschlagen');return v;
}
async function aktion(mode){try{let r=await api('/aktion',{mode});el('status').textContent=r.meldung;}
catch(e){el('status').textContent=e.message;}}
async function speichern(){try{
 const cfg={};for(let id of ['downloads','arbeitsordner','format','kategorie'])cfg[id]=el(id).value;
 el('status').textContent=(await api('/einstellungen',{cfg})).meldung;
}catch(e){el('status').textContent=e.message;}}
async function diagnose(){try{el('diagnose').textContent=JSON.stringify(await api('/diagnose'),null,2);}
catch(e){el('diagnose').textContent=e.message;}}
async function status(){try{let r=await api('/status');
 el('bar').value=r.event.prozent||0;el('phase').textContent=(r.event.phase||'Bereit')+' · '+(r.event.titel||'');
 el('jobs').textContent=JSON.stringify(r.jobs,null,2);el('log').textContent=(r.messages||[]).join('\n');
 el('ready').textContent=r.jobs.BEREIT||0;el('wait').textContent=r.jobs.WARTET||0;
 if(!el('downloads').dataset.ready){
  for(let id of ['downloads','arbeitsordner','format','kategorie'])el(id).value=r.cfg[id];
  el('downloads').dataset.ready='1';
 }
 el('status').textContent=r.active?'In Arbeit':'Bereit / pausiert';
}catch(e){el('status').textContent=e.message;}}
for(let [id,list] of [['format',['BREI','HOCH','QUAD','KLAS','4K']],
['kategorie',['PROVOWARE','CODING','THEMA']]]){
 el(id).innerHTML=list.map(x=>'<option>'+x+'</option>').join('');
}
status();setInterval(status,1500);
</script></body></html>'''


class Bedienung:
    def __init__(self, cfg, config_path):
        self.cfg = konfigurieren(cfg)
        self.config_path = Path(config_path)
        self.service = None
        self.thread = None
        self.messages = deque(maxlen=20)
        self.event = {"phase": "bereit", "prozent": 0}
        self.lock = threading.RLock()

    def _meldung(self, msg):
        with self.lock:
            self.messages.appendleft(str(msg))

    def _fortschritt(self, value):
        with self.lock:
            self.event = value

    def status(self):
        with self.lock:
            info = self.service.status() if self.service else {"auftraege": {}}
            return {"cfg": self.cfg, "jobs": info["auftraege"], "event": self.event,
                    "messages": list(self.messages), "active": bool(self.thread and self.thread.is_alive())}

    def einstellungen(self, data):
        with self.lock:
            if self.thread and self.thread.is_alive():
                raise RuntimeError("Während der Verarbeitung keine Einstellungen ändern.")
            cfg = konfigurieren({**self.cfg, **data})
            if not Path(cfg["downloads"]).expanduser().is_dir():
                raise ValueError("Downloads-Ordner existiert nicht.")
            json_sicher(self.config_path, cfg)
            self.cfg = cfg

    def aktion(self, mode):
        with self.lock:
            if mode == "stop":
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


def starten(cfg, config_path, port=0, browser=True):
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
            elif path=="/diagnose": self.antwort(pruefen())
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
    if browser: webbrowser.open(url)
    try: server.serve_forever(poll_interval=.3)
    finally:
        if bedienung.service: bedienung.service.stop.set()
        server.server_close()
