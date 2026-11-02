#!/usr/bin/env python3
"""Echte Tab-Eingaben und berechnete Kontraste in isoliertem Chromium, ohne Pakete."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import secrets
import socket
import struct
import subprocess
import sys
import tempfile
import time
from urllib.request import urlopen
from urllib.parse import urlsplit
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from videozoom.webui import HTML
from videozoom.render_watchdog import beenden
from layout_check import browser_finden


class CDP:
    def __init__(self,url):
        u=urlsplit(url);self.sock=socket.create_connection((u.hostname,u.port),timeout=5)
        self.buffer=b'';self.n=0
        key=base64.b64encode(secrets.token_bytes(16)).decode()
        self.sock.sendall((f'GET {u.path} HTTP/1.1\r\nHost: {u.hostname}:{u.port}\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n').encode())
        response=b''
        while b'\r\n\r\n' not in response:
            chunk=self.sock.recv(4096)
            if not chunk or len(response)>16384:raise RuntimeError('CDP-Verbindung fehlgeschlagen')
            response+=chunk
        header,self.buffer=response.split(b'\r\n\r\n',1)
        expected=base64.b64encode(hashlib.sha1((key+'258EAFA5-E914-47DA-95CA-C5AB0DC85B11').encode()).digest())
        if b' 101 ' not in header or expected.lower() not in header.lower():
            raise RuntimeError('CDP-Handshake ungültig')

    def read(self,n):
        while len(self.buffer)<n:
            chunk=self.sock.recv(max(4096,n-len(self.buffer)))
            if not chunk:raise RuntimeError('CDP-Verbindung beendet')
            self.buffer+=chunk
        value,self.buffer=self.buffer[:n],self.buffer[n:]
        return value

    def send(self,data,opcode=1):
        mask=secrets.token_bytes(4);n=len(data)
        size=bytes([0x80|n]) if n<126 else b'\xfe'+struct.pack('!H',n) if n<65536 else b'\xff'+struct.pack('!Q',n)
        self.sock.sendall(bytes([0x80|opcode])+size+mask+bytes(b^mask[i%4] for i,b in enumerate(data)))

    def call(self,method,params=None):
        self.n+=1;ident=self.n;self.send(json.dumps({'id':ident,'method':method,'params':params or {}}).encode())
        deadline=time.monotonic()+10
        while time.monotonic()<deadline:
            self.sock.settimeout(max(.1,deadline-time.monotonic()))
            head=self.read(2);opcode=head[0]&15
            if not head[0]&128:raise RuntimeError('Fragmentierte CDP-Antwort nicht unterstützt')
            size=head[1]&127
            if size==126:size=struct.unpack('!H',self.read(2))[0]
            elif size==127:size=struct.unpack('!Q',self.read(8))[0]
            if size>10*1024**2:raise RuntimeError('CDP-Antwort zu groß')
            mask=self.read(4) if head[1]&128 else None
            raw=self.read(size)
            if mask:raw=bytes(b^mask[i%4] for i,b in enumerate(raw))
            if opcode==9:self.send(raw,10);continue
            if opcode==8:raise RuntimeError('CDP geschlossen')
            if opcode!=1:continue
            message=json.loads(raw)
            if message.get('id')==ident:
                if 'error' in message:raise RuntimeError(str(message['error']))
                return message.get('result',{})
        raise RuntimeError('CDP-Zeitbudget überschritten')

    def js(self,expression):
        result=self.call('Runtime.evaluate',{'expression':expression,'returnByValue':True,'awaitPromise':True})
        if result.get('exceptionDetails'):raise RuntimeError(str(result['exceptionDetails']))
        return result['result'].get('value')


MESSUNG=r'''(()=>{
 const rgba=s=>{const a=(s.match(/[\d.]+/g)||[]).map(Number);return [a[0]||0,a[1]||0,a[2]||0,a.length>3?a[3]:1];};
 const bg=e=>{if(!e)return [11,21,29];const p=bg(e.parentElement),c=rgba(getComputedStyle(e).backgroundColor);return c.slice(0,3).map((x,i)=>x*c[3]+p[i]*(1-c[3]));};
 const lum=c=>c.slice(0,3).map(x=>{x/=255;return x<=.04045?x/12.92:((x+.055)/1.055)**2.4;}).reduce((s,x,i)=>s+x*[.2126,.7152,.0722][i],0);
 const ratio=(a,b)=>{let x=lum(a),y=lum(b);return (Math.max(x,y)+.05)/(Math.min(x,y)+.05);};
 const errors=[];let min=100;
 for(const e of document.querySelectorAll('button,input,select,label,small,summary,.phase-nav a,#status')){
  if(!e.getClientRects().length)continue;
  const c=rgba(getComputedStyle(e).color),back=bg(e),r=ratio(c,back);min=Math.min(min,r);
  if(r<4.5)errors.push({element:e.id||e.tagName,text:e.textContent.slice(0,55),kontrast:r});
 }
 const active=document.activeElement,style=getComputedStyle(active);
 const focus=ratio(rgba(style.outlineColor),bg(active.parentElement));
 return {fehler:errors,minText:min,fokusKontrast:focus,fokusBreite:parseFloat(style.outlineWidth)||0};
})()'''

FOCUSABLE="[...document.querySelectorAll('a[href],button,input,select,summary')].filter(e=>!e.disabled&&e.getClientRects().length)"


def pruefen(ziel):
    ziel.mkdir(parents=True,exist_ok=True);start=time.monotonic();results=[]
    with tempfile.TemporaryDirectory(prefix='videozoom-bedienung-') as tmp:
        root=Path(tmp);profile=root/'profil';fixture=root/'pruefung.html'
        fixture.write_text(HTML.replace('formatHinweis();status();diagnose();','formatHinweis();'),encoding='utf-8')
        log=(root/'chrome.log').open('w')
        proc=subprocess.Popen([browser_finden(),'--headless=new','--no-sandbox','--disable-gpu',
            '--disable-background-networking','--disable-dev-shm-usage','--no-first-run',
            '--no-default-browser-check','--remote-debugging-address=127.0.0.1',
            '--remote-debugging-port=0',f'--user-data-dir={profile}',fixture.as_uri()],
            stdout=subprocess.DEVNULL,stderr=log,start_new_session=True)
        cdp=None
        try:
            portfile=profile/'DevToolsActivePort'
            while not portfile.exists():
                if proc.poll() is not None or time.monotonic()-start>10:
                    raise RuntimeError('Chromium-Start fehlgeschlagen: '+(root/'chrome.log').read_text()[-500:])
                time.sleep(.05)
            port=int(portfile.read_text().splitlines()[0])
            with urlopen(f'http://127.0.0.1:{port}/json/list',timeout=5) as response:tabs=json.load(response)
            page=next(t for t in tabs if t.get('type')=='page')
            cdp=CDP(page['webSocketDebuggerUrl']);cdp.call('Page.enable')
            while cdp.js('document.readyState')!='complete':
                if time.monotonic()-start>15:raise RuntimeError('Testseite nicht bereit')
                time.sleep(.05)
            for width,height,zoom in ((800,600,100),(800,600,125),(800,600,150),(800,600,200),(1280,720,100)):
                cdp.call('Emulation.setDeviceMetricsOverride',{'width':width,'height':height,'deviceScaleFactor':1,'mobile':False})
                for theme in ('cyan','violett','gruen','orange'):
                    if time.monotonic()-start>110:raise RuntimeError('Browser-Gesamtbudget überschritten')
                    cdp.js(f"document.documentElement.style.zoom={zoom/100};document.body.dataset.theme={json.dumps(theme)};window.scrollTo(0,0)")
                    count=cdp.js(f'window.tabListe={FOCUSABLE};tabListe[0].focus();tabListe.length')
                    for i in range(1,count):
                        cdp.call('Input.dispatchKeyEvent',{'type':'keyDown','key':'Tab','code':'Tab','windowsVirtualKeyCode':9})
                        cdp.call('Input.dispatchKeyEvent',{'type':'keyUp','key':'Tab','code':'Tab','windowsVirtualKeyCode':9})
                        if not cdp.js(f'document.activeElement===tabListe[{i}]'):
                            raise RuntimeError(f'Tabfolge fehlerhaft: {theme}/{width}/{zoom}, Position {i}')
                    measured=cdp.js(MESSUNG)
                    if measured['fehler'] or measured['fokusKontrast']<3 or measured['fokusBreite']<2:
                        raise RuntimeError(f'Kontrast/Fokus fehlerhaft {theme}/{width}/{zoom}: '+json.dumps(measured))
                    # Native Aufklappzeilen wirklich mit der Leertaste öffnen/schließen.
                    for index in range(cdp.js("document.querySelectorAll('summary').length")):
                        cdp.js(f"window.zusammenfassung=document.querySelectorAll('summary')[{index}];zusammenfassung.focus();window.vorher=zusammenfassung.parentElement.open")
                        for typ in ('keyDown','keyUp'):
                            cdp.call('Input.dispatchKeyEvent',{'type':typ,'key':' ','code':'Space','windowsVirtualKeyCode':32})
                        if not cdp.js('zusammenfassung.parentElement.open!==vorher'):raise RuntimeError('Aufklappzeile per Tastatur nicht bedienbar')
                        cdp.js('zusammenfassung.parentElement.open=vorher')
                    # Deaktivierte Knöpfe und echte Maus-Hoverfarbe ebenfalls messen.
                    cdp.js("window.knopfZustand=[...document.querySelectorAll('button')].map(e=>[e,e.disabled]);knopfZustand.forEach(([e])=>e.disabled=true)")
                    disabled=cdp.js(MESSUNG)
                    cdp.js("knopfZustand.forEach(([e,v])=>e.disabled=v)")
                    if disabled['fehler']:raise RuntimeError('Kontrast deaktivierter Knöpfe: '+json.dumps(disabled))
                    xy=cdp.js("(()=>{const e=document.querySelector('button');e.scrollIntoView({block:'center'});const r=e.getBoundingClientRect();return {x:r.x+r.width/2,y:r.y+r.height/2};})()")
                    cdp.call('Input.dispatchMouseEvent',{'type':'mouseMoved',**xy})
                    hover=cdp.js(MESSUNG)
                    cdp.call('Input.dispatchMouseEvent',{'type':'mouseMoved','x':0,'y':0})
                    if hover['fehler']:raise RuntimeError('Hover-Kontrast: '+json.dumps(hover))
                    measured.update(theme=theme,breite=width,hoehe=height,cssZoom=zoom,tabStopps=count,
                                    minDeaktiviert=disabled['minText'],minHover=hover['minText'])
                    results.append(measured)
            report={'schema':1,'commit':os.environ.get('GITHUB_SHA'),'bestanden':True,'faelle':len(results),'werte':results,
                    'methode':'Echte CDP-Tab-/Leertasten; berechnete Text-/Fokusfarben mit Alpha-Hintergründen. CSS-Zoomsimulation, kein echter KDE-Zoom.',
                    'grenzen':'Pixelreferenz und manuelle Sichtprüfung OFFEN; Verlaufspixel und Farbsehschwächen nicht vollständig durch Farbrechnung geprüft.',
                    'stable':False}
            (ziel/'bedienung_bericht.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
            return report
        except Exception as exc:
            (ziel/'bedienung_bericht.json').write_text(json.dumps({'bestanden':False,'commit':os.environ.get('GITHUB_SHA'),'fehler':str(exc),'bisherige_faelle':results},ensure_ascii=False,indent=2)+'\n')
            raise
        finally:
            if cdp:cdp.sock.close()
            beenden(proc,2);log.close()


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--ziel',type=Path,required=True);args=parser.parse_args()
    result=pruefen(args.ziel);print(json.dumps({'faelle':result['faelle'],'bestanden':result['bestanden'],'commit':result['commit']}))
