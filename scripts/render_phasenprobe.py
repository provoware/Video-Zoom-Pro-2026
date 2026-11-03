#!/usr/bin/env python3
"""Nur Messprototyp: beide Bildphasen verlustfrei getrennt, danach gemeinsam kodieren.

Kein Produktpfad, keine Quellarchivierung, kein bereits freigegebener Renderer.
"""
import argparse
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from videozoom.core import ffmpeg_befehl, konfigurieren, zeitplan


def phase_command(command, count, target, phase, length):
    c = list(command)
    graph = c[c.index('-filter_complex')+1].split(';')
    if phase == 'schnell':
        selected = [g for g in graph if re.match(r'\[r\d+\]',g) or g.endswith('[anfang]')]
        graph = ';'.join(selected).replace('[anfang]', '[video]')
        for i in range(count):
            graph = graph.replace(f'[r{i}]', f'[{i}:v]')
    else:
        selected = [g for g in graph if re.match(r'\[(v\d+|vout\d+|uebergang\d+)\]',g)]
        graph = ';'.join(selected)
        for i in range(count):
            graph = graph.replace(f'[v{i}]', f'[{i}:v]')
        last = f'uebergang{count-1}' if count>1 else 'vout0'
        graph += f';[{last}]null[video]'
    c[c.index('-filter_complex')+1] = graph
    idx = c.index('-map', c.index('-map')+1)
    del c[idx:idx+2]
    for opt in ('-c:a','-b:a'):
        idx = c.index(opt); del c[idx:idx+2]
    c[c.index('-crf')+1] = '0'
    c[c.index('-preset')+1] = 'ultrafast'
    idx = len(c)-1-c[::-1].index('-t')
    c[idx+1] = str(length)
    c[-1] = str(target)
    return c


def rendern(data):
    audio = Path(data['audio']); images = [Path(p) for p in data['bilder']]
    out = Path(data['ziel']); length = float(data['laenge'])
    cfg = konfigurieren({'format':data['format']})
    command = ffmpeg_befehl(audio, images, out, length, cfg)
    schnell, _, _ = zeitplan(length, len(images), cfg['fps'], cfg['uebergang'])
    with tempfile.TemporaryDirectory(prefix='messphasen-',dir=out.parent) as tmp:
        folder = Path(tmp); first = folder/'rueck.mp4'; second = folder/'vor.mp4'
        for phase, target, seconds in [('schnell',first,len(images)*schnell),
                                       ('langsam',second,length-len(images)*schnell)]:
            subprocess.run(phase_command(command,len(images),target,phase,seconds),
                           check=True,stdout=subprocess.DEVNULL,timeout=60)
        listing = folder/'concat.txt'
        # Eigene feste Dateinamen; keine aus Dateinamen übernommenen Steuerzeichen.
        listing.write_text("file 'rueck.mp4'\nfile 'vor.mp4'\n")
        subprocess.run(['ffmpeg','-v','error','-nostdin','-n','-f','concat','-safe','1',
                        '-i',str(listing),'-i',str(audio),'-map','0:v:0','-map','1:a:0',
                        '-c:v','libx264','-preset','veryfast','-crf','21','-pix_fmt','yuv420p',
                        '-threads','2','-c:a','aac','-b:a','192k','-t',str(length),
                        '-movflags','+faststart',str(out)],check=True,stdout=subprocess.DEVNULL,timeout=60)


if __name__ == '__main__':
    p=argparse.ArgumentParser();p.add_argument('--auftrag',required=True)
    rendern(json.loads(p.parse_args().auftrag))
