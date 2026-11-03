#!/usr/bin/env python3
"""Begrenzte Vergleichsmessung mit ausschließlich selbst erzeugten Testmedien."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import resource
import statistics
import signal
import subprocess
import sys
import tempfile
import time
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tests.fixtures.generieren import wav, png
from videozoom.core import ffmpeg_befehl, konfigurieren, video_gueltig
from videozoom.render_watchdog import cpu_arbeit


def grenzen():
    """Isolierter Entwicklerlauf: vier CPU-Kerne, 60 s CPU. RAM separat im Elternprozess."""
    if hasattr(os, 'sched_getaffinity'):
        os.sched_setaffinity(0, set(sorted(os.sched_getaffinity(0))[:4]))
    resource.setrlimit(resource.RLIMIT_CPU, (60, 60))


def lauf(command, stats):
    start = time.monotonic()
    wrapper = ("import subprocess,sys,resource,pathlib; "
               "r=subprocess.run(sys.argv[2:]); "
               "pathlib.Path(sys.argv[1]).write_text(str(resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss)); "
               "sys.exit(r.returncode)")
    proc = subprocess.Popen([sys.executable, '-c', wrapper, str(stats), *command],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                            start_new_session=True, preexec_fn=grenzen)
    while True:
        try:
            _, err = proc.communicate(timeout=.1)
            return {'sekunden': round(time.monotonic()-start, 4),
                    'spitzen_ram_kib': int(stats.read_text()),
                    'exitcode': proc.returncode, 'fehler': err[-500:]}
        except subprocess.TimeoutExpired:
            resident = 0
            for pid in cpu_arbeit(proc.pid):
                try:
                    resident += int(Path(f'/proc/{pid}/statm').read_text().split()[1])*os.sysconf('SC_PAGE_SIZE')
                except (OSError, ValueError, IndexError):
                    pass
            if time.monotonic()-start > 60 or resident > 2*1024**3:
                os.killpg(proc.pid, signal.SIGKILL)
                proc.communicate(timeout=5)
                return {'exitcode': -1, 'fehler': 'Zeit-/2-GiB-RAM-Budget erreicht; eigene Prozessgruppe beendet'}



def vergleichen(ziel, wiederholungen=2, formate=('KLAS','BREI'), anzahl=(1,5,10),
                varianten=('bestand','filter_1','zweiphasig')):
    rows = []
    source = {str(p.relative_to(Path(__file__).resolve().parents[1])):hashlib.sha256(p.read_bytes()).hexdigest()
              for p in (Path(__file__).resolve(),Path(__file__).with_name('render_phasenprobe.py'),
                        Path(__file__).resolve().parents[1]/'videozoom/core.py',
                        Path(__file__).resolve().parents[1]/'tests/fixtures/generieren.py')}
    dirty = subprocess.check_output(['git','status','--porcelain'],text=True).splitlines()
    ffmpeg_version = subprocess.check_output(['ffmpeg','-version'],text=True).splitlines()[0]
    with tempfile.TemporaryDirectory(prefix='videozoom-vergleich-') as tmp:
        root = Path(tmp); audio = wav(root/'synthetisch.wav', sekunden=8)
        images = [png(root/f'{i}.png', (20+i*20, 80+i*9, 190-i*13), breite=512, hoehe=384)
                  for i in range(10)]
        for formatcode in formate:
            cfg = konfigurieren({'format':formatcode})
            for count in anzahl:
                # Reihenfolge wechselt, damit Aufwärmen nicht nur einer Variante hilft.
                for repeat in range(wiederholungen):
                    variants = varianten if repeat%2 == 0 else tuple(reversed(varianten))
                    for variant in variants:
                        out = root/f'{formatcode}-{count}-{repeat}-{variant}.mp4'
                        command = ffmpeg_befehl(audio, images[:count], out, 8, cfg)
                        if variant == 'filter_1':
                            command[1:1] = ['-filter_complex_threads', '1']
                        if variant == 'zweiphasig':
                            command = [sys.executable, str(Path(__file__).with_name('render_phasenprobe.py')),
                                       '--auftrag',json.dumps({'audio':str(audio),'bilder':[str(p) for p in images[:count]],
                                       'ziel':str(out),'laenge':8,'format':formatcode})]
                        row = {'format':formatcode, 'bilder':count, 'lauf':repeat+1, 'variante':variant}
                        row.update(lauf(command, root/'zeit.txt'))
                        if row['exitcode'] == 0:
                            try:
                                row['gueltig'] = video_gueltig(out, 8, cfg, testmodus=True)
                                frames = subprocess.run(['ffmpeg','-v','error','-i',str(out),
                                    '-map','0:v:0','-f','framemd5','-'],capture_output=True,
                                    timeout=30,check=True,preexec_fn=grenzen)
                                row['bildfolge_sha256'] = hashlib.sha256(frames.stdout).hexdigest()
                            except (RuntimeError, subprocess.SubprocessError) as exc:
                                row['gueltig'] = False; row['fehler'] = str(exc)[-500:]
                        out.unlink(missing_ok=True)
                        rows.append(row)
                        print(json.dumps(row,ensure_ascii=False),flush=True)
                        ziel.write_text(json.dumps({'status':'LAEUFT','messungen':rows},indent=2))
    summary = []
    for formatcode in formate:
        for count in anzahl:
            subset = [r for r in rows if r['format']==formatcode and r['bilder']==count]
            item = {'format':formatcode,'bilder':count}
            for variant in varianten:
                measured = [r for r in subset if r['variante']==variant and r.get('gueltig')]
                item[variant] = {'gueltige_laeufe':len(measured),
                    'median_sekunden':statistics.median(r['sekunden'] for r in measured) if measured else None,
                    'median_ram_kib':statistics.median(r['spitzen_ram_kib'] for r in measured) if measured else None}
            hashes = {r.get('bildfolge_sha256') for r in subset if r.get('gueltig')}
            item['identische_decodierte_bildfolge'] = len(hashes)==1 and len(subset)==len(varianten)*wiederholungen and all(r.get('gueltig') for r in subset)
            summary.append(item)
    report = {'schema':1,'status':'ABGESCHLOSSEN','quellcommit':os.environ.get('GITHUB_SHA') or subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
        'datei_sha256':source,'arbeitskopie_aenderungen':dirty,'ffmpeg':ffmpeg_version,
        'testdaten':'synthetische WAV 8s / eigene farbige PNG 512x384',
        'grenzen':'4 zugängliche CPU-Kerne, 2 GiB residente Prozessbaumgrenze (100-ms-Abfrage), 60 s pro Renderlauf; Entwicklerlauf ohne Produktivdaten',
        'scope':{'formate':formate,'bilder':anzahl,'varianten':varianten,'grenzen':'kein 4K-, Langsong- oder Kubuntu-Nachweis'},
        'zusammenfassung':summary,'messungen':rows}
    ziel.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    return report


if __name__ == '__main__':
    p=argparse.ArgumentParser();p.add_argument('--bericht',type=Path,required=True)
    p.add_argument('--wiederholungen',type=int,choices=(1,2,3),default=2)
    p.add_argument('--formate',nargs='+',choices=('KLAS','BREI'),default=('KLAS','BREI'))
    p.add_argument('--bilder',nargs='+',type=int,choices=(1,5,10),default=(1,5,10))
    p.add_argument('--varianten',nargs='+',choices=('bestand','filter_1','zweiphasig'),default=('bestand','filter_1','zweiphasig'))
    args=p.parse_args();args.bericht.parent.mkdir(parents=True,exist_ok=True)
    vergleichen(args.bericht,args.wiederholungen,args.formate,args.bilder,args.varianten)
