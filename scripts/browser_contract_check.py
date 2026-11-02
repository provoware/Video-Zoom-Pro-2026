#!/usr/bin/env python3
"""Echte JavaScript-Verträge; Chromium in CI, optional Node als lokale Vorprüfung."""
import argparse
import html
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from videozoom.webui import HTML
from layout_check import browser_finden, browser_aufruf

HARNESS = r'''
const timers=new Map(); let nummer=0;
globalThis.setTimeout=(fn,ms)=>{const id=++nummer;timers.set(id,{fn,ms});return id;};
globalThis.clearTimeout=id=>timers.delete(id);
function assert(wert,msg){if(!wert)throw Error(msg);}
function timer(ms){return [...timers.values()].find(t=>t.ms===ms);}
function fire(ms){const entry=[...timers].find(([id,t])=>t.ms===ms);assert(entry,'Zeitbudget fehlt '+ms);timers.delete(entry[0]);entry[1].fn();}
function blockFetch(){globalThis.fetch=(url,options)=>new Promise((resolve,reject)=>{
 options.signal.addEventListener('abort',()=>reject(new DOMException('Abbruch','AbortError')));
});}
(async()=>{
 let tests=0;
 blockFetch();let p=api('/status');assert(timer(10000),'Standardbudget');fire(10000);
 try{await p;throw Error('Kein Timeout');}catch(e){assert(e.message.includes('Zeitlimit erreicht'),'Zeitlimittext');}
 assert(timers.size===0,'Timer nach Abbruch');tests++;
 globalThis.fetch=async(url,options)=>({ok:true,json:()=>new Promise((resolve,reject)=>{
  options.signal.addEventListener('abort',()=>reject(new DOMException('Abbruch','AbortError')));
 })});
 p=api('/status');await Promise.resolve();fire(10000);
 try{await p;throw Error('JSON hängt');}catch(e){assert(e.message.includes('Zeitlimit'),'JSON-Budget');}tests++;
 globalThis.fetch=async()=>({ok:false,json:async()=>({fehler:'Abgelehnt'})});
 try{await api('/aktion',{});throw Error('HTTP-Fehler verschluckt');}catch(e){assert(e.message==='Abgelehnt','HTTP-Fehlertext');}
 assert(timers.size===0,'Timer nach HTTP-Fehler');tests++;
 const data={jobs:{BEREIT:2},event:{phase:'bereit'},cfg:{downloads:'/tmp/d',arbeitsordner:'/tmp/a',theme:'cyan',format:'KLAS',kategorie:'THEMA'}};
 let calls=0,release;
 globalThis.fetch=()=>{calls++;return new Promise(resolve=>{release=()=>resolve({ok:true,json:async()=>data});});};
 p=status();for(let i=0;i<10;i++)await status();assert(calls===1,'Status parallel');release();await p;
 assert(timers.size===1&&timer(1500),'Genau eine Folgeabfrage');assert(el('kpi-bereit').textContent==2,'Auftragszahl');tests++;
 timers.clear();blockFetch();p=status();fire(10000);await p;
 assert(el('status').textContent.startsWith('Anzeige veraltet:'),'Veraltete Anzeige fehlt');
 assert(timer(1500),'Wiederanlauf fehlt');tests++;
 timers.clear();globalThis.fetch=async()=>({ok:true,json:async()=>data});await status();
 assert(!el('status').textContent.includes('veraltet'),'Keine Erholung');tests++;
 timers.clear();blockFetch();p=ordnerwahl('downloads');assert(timer(125000),'Manueller Dialog zu kurz');fire(125000);await p;tests++;
 timers.clear();blockFetch();p=diagnose();assert(timer(60000),'Diagnosebudget');fire(60000);await p;tests++;
 fortschrittAnzeigen('videobar','video-wert',{});assert(el('video-wert').textContent==='Noch unbekannt','Unbekannter Fortschritt');
 fortschrittAnzeigen('videobar','video-wert',{prozent:0});assert(el('videobar').value===0&&el('video-wert').textContent==='0 %','Echte Null');tests++;
 const text=diagnoseText({startbereit:false,pruefungen:[{name:'Test',ok:false,hinweis:'Ursache',handlung:'Lösung'}]});
 assert(text.includes('HANDLUNG NÖTIG')&&text.includes('Nächster Schritt: Lösung')&&text.includes('Technische Einzelheiten'),'Diagnoseführung');tests++;
 globalThis.fetch=async(url,options)=>{const body=JSON.parse(options.body);assert(body.modus==='zuruecksetzen'&&body.gruppe==='ansicht','Rücksetzauswahl');return {ok:true,json:async()=>({cfg:{theme:'cyan',format:'BREI',kategorie:'PROVOWARE'},meldung:'Gesichert'})};};
 el('resetgruppe').value='ansicht';await ruecksetzen(false);assert(el('theme').value==='cyan'&&el('hinweis').textContent==='Gesichert','Rücksetzmeldung');tests++;
 globalThis.fetch=async()=>({ok:false,json:async()=>({fehler:'Erst stoppen'})});await ruecksetzen(true);
 assert(el('hinweis').textContent==='Erst stoppen'&&el('theme').value==='cyan','Rücksetzfehler erhält Anzeige');tests++;
 timers.clear();globalThis.fetch=async()=>({ok:true,json:async()=>({...data,andere_instanz:true})});
 await status();assert(el('status').textContent==='Arbeitet im anderen Fenster','Fremde Verarbeitung sichtbar');tests++;
 const report={bestanden:true,tests};
 if(typeof process!=='undefined')console.log(JSON.stringify(report));
 else document.getElementById('contract-check').textContent=JSON.stringify(report);
})().catch(e=>{
 if(typeof process!=='undefined'){console.error(e);process.exitCode=1;}
 else document.getElementById('contract-check').textContent=JSON.stringify({bestanden:false,fehler:String(e)});
});
'''


def pruefen(node=False):
    script = HTML.split('<script>',1)[1].split('</script>',1)[0]
    script = script.replace('formatHinweis();status();diagnose();','')
    with tempfile.TemporaryDirectory(prefix='videozoom-js-') as tmp:
        root=Path(tmp)
        if node:
            prefix = """const document={body:{dataset:{}},getElementById:id=>elements[id]||(elements[id]={dataset:{},value:'',textContent:'',innerHTML:'',removeAttribute:function(name){delete this[name];}})};const elements={};const location={href:'http://127.0.0.1/?token=test'};\n"""
            target=root/'contract.cjs';target.write_text(prefix+script+HARNESS)
            result=subprocess.run(['node',str(target)],capture_output=True,text=True,timeout=30,check=True)
            report=json.loads(result.stdout)
            report['engine']='Node – lokale JavaScript-Vorprüfung, kein Browsernachweis'
        else:
            target=root/'contract.html'
            target.write_text(HTML.split('<script>',1)[0]+'<output id="contract-check"></output><script>'+script+HARNESS+'</script></body></html>')
            dom=browser_aufruf(browser_finden(),target.as_uri(),root/'profile',(800,600))
            match=re.search(r'<output[^>]*id="contract-check"[^>]*>(.*?)</output>',dom,re.S)
            if not match:raise RuntimeError('Kein JavaScript-Nachweis aus Chromium')
            report=json.loads(html.unescape(match.group(1)))
            report['engine']='Chromium'
        if not report.get('bestanden') or report.get('tests')!=13:
            raise RuntimeError(str(report))
        report['commit']=os.environ.get('GITHUB_SHA')
        return report

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--node',action='store_true')
    p.add_argument('--bericht',type=Path)
    args=p.parse_args();report=pruefen(args.node)
    if args.bericht:
        args.bericht.parent.mkdir(parents=True,exist_ok=True)
        args.bericht.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report,ensure_ascii=False))
