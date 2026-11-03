"""Bewusste Medienauswahl, verlustfreie Arbeitskopien und sicherer Fundlisten-Neuaufbau."""
import hashlib
import os
from pathlib import Path
import secrets
import shutil
import subprocess
import time


def auswahl(workflow):
    value = workflow.zustand.setdefault('auswahl', {'audio': [], 'bilder': {}})
    if (not isinstance(value, dict) or not isinstance(value.get('audio'), list)
            or not isinstance(value.get('bilder'), dict)):
        raise RuntimeError('Gespeicherte Medienauswahl beschädigt; keine Änderung.')
    return value


def audio_erlaubt(path, downloads, work):
    p = Path(path)
    staged = Path(work) / 'AUSWAHL' / 'AUDIO'
    return (p.suffix.lower() == '.wav' and
            (p.parent == Path(downloads) or
             (p.parent.parent == staged and len(p.parent.name) == 16
              and all(c in '0123456789abcdef' for c in p.parent.name))))


def audio_dateien(workflow, alle=False):
    from .core import stabil
    registry=auswahl(workflow)
    manual=[Path(p) for p in registry['audio']]
    if any(not audio_erlaubt(p,workflow.downloads,workflow.ordner) for p in manual):
        raise RuntimeError('Unsichere gespeicherte Audioauswahl.')
    auto=[p for p in workflow.downloads.iterdir() if p.suffix.lower()=='.wav'] if alle or workflow.cfg['audio_auto'] else []
    return sorted(set(p for p in [*auto,*manual] if stabil(p)))


def sicher(path):
    p = Path(path).expanduser().absolute()
    if any(x.is_symlink() for x in (p, *p.parents)):
        raise RuntimeError('Verknüpfte Medienpfade sind nicht erlaubt.')
    return p


def dateien_waehlen(art, start, stop):
    """Systemdialog; nur eigene Kindprozesse stoppen, keine Shell und kein Tk."""
    if art not in {'audio', 'bilder'}:
        raise ValueError('Unbekannte Medienart.')
    if not (os.environ.get('DISPLAY') or os.environ.get('WAYLAND_DISPLAY')):
        raise RuntimeError('Dateiauswahl benötigt einen grafischen Desktop. Dateien im vorgesehenen Eingangsordner ablegen.')
    title = 'WAV-Dateien auswählen' if art == 'audio' else 'Bilder für diesen Song auswählen'
    pattern = '*.wav *.WAV' if art == 'audio' else '*.png *.jpg *.jpeg *.webp *.bmp *.PNG *.JPG'
    if shutil.which('kdialog'):
        cmd = ['kdialog','--getopenfilename',str(start),pattern,'--multiple','--separate-output','--title',title]
    elif shutil.which('zenity'):
        cmd = ['zenity','--file-selection','--multiple','--separator=\n','--filename='+str(start)+'/',
               '--title='+title,'--file-filter='+pattern]
    else:
        raise RuntimeError('Kein Dateidialog vorhanden. kdialog oder zenity über die Systemverwaltung installieren.')
    with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) as p:
        deadline = time.monotonic()+120
        try:
            while True:
                try:
                    out, _ = p.communicate(timeout=.2)
                    return [Path(x) for x in out.splitlines() if x] if p.returncode == 0 else []
                except subprocess.TimeoutExpired:
                    if stop.is_set() or time.monotonic() >= deadline:
                        return []
        finally:
            if p.poll() is None:
                p.terminate()
                try: p.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    p.kill(); p.wait(timeout=3)


def kopie(source, folder, stop):
    from .core import pruefsumme, regulaer, speicher_pruefen
    source, folder = sicher(source), sicher(folder)
    if not regulaer(source):
        raise ValueError('Ausgewählte Datei fehlt oder ist unsicher.')
    before = source.stat()
    digest = pruefsumme(source)
    folder.mkdir(parents=True, exist_ok=True)
    target = folder / source.name
    if target.exists() and (not regulaer(target) or pruefsumme(target) != digest):
        target = folder / (source.stem+'_'+digest[:12]+source.suffix)
    if target.exists():
        if target.is_symlink() or pruefsumme(target) != digest:
            raise RuntimeError('Dateikonflikt; keine vorhandene Datei überschrieben.')
        after = source.stat()
        if (before.st_size,before.st_mtime_ns,before.st_ctime_ns) != (after.st_size,after.st_mtime_ns,after.st_ctime_ns):
            raise RuntimeError('Original während der Auswahl verändert; erneut auswählen.')
        return target
    speicher_pruefen(folder, before.st_size)
    part = folder / ('.import-'+secrets.token_hex(16)+'.teil')
    try:
        with source.open('rb') as src, part.open('xb') as dst:
            while block := src.read(1024*1024):
                if stop.is_set():
                    raise RuntimeError('Auswahlkopie angehalten; Original bleibt erhalten.')
                dst.write(block)
            dst.flush();os.fsync(dst.fileno())
        after = source.stat()
        if (before.st_size,before.st_mtime_ns) != (after.st_size,after.st_mtime_ns) or pruefsumme(part) != digest or pruefsumme(source) != digest:
            raise RuntimeError('Datei während der Auswahl verändert; Original erneut auswählen.')
        os.link(part,target,follow_symlinks=False)
        os.utime(target,(time.time()-10,)*2)  # Die bestätigte eigene Kopie ist vollständig.
        return target
    finally:
        part.unlink(missing_ok=True)


def uebernehmen(workflow, art, files, key=None):
    from .core import (vollstaendig,dauer,medieninfo,pruefsumme,BILDTYPEN,slug,stabil)
    if len(files)>40:
        raise ValueError('Höchstens 40 Dateien auf einmal auswählen.')
    registry = auswahl(workflow)
    if art == 'bilder':
        job = workflow.zustand['auftraege'].get(key)
        if not job or job.get('status') not in {'WARTET','BEREIT'} or job.get('versuche',0):
            raise ValueError('Bilder nur für einen noch nicht bearbeiteten Song auswählen.')
        folder = workflow.ordner/'EINGANG'/slug(job['titel'])/'BILDER'
    elif art == 'audio':
        folder = workflow.ordner/'AUSWAHL'/'AUDIO'
    else:
        raise ValueError('Unbekannte Auswahl.')
    # Gesamte Auswahl vor der ersten Kopie prüfen. Originale werden niemals bewegt.
    for file in files:
        file=sicher(file)
        if not stabil(file):
            raise ValueError('Datei noch nicht vollständig angekommen. Kurz warten und erneut auswählen.')
        if art == 'audio':
            if file.suffix.lower() != '.wav':raise ValueError('Nur WAV-Dateien auswählen.')
            vollstaendig(file);dauer(file)
        else:
            if file.suffix.lower() not in BILDTYPEN:raise ValueError('Nur unterstützte Bilder auswählen.')
            info=medieninfo(file)
            video=next((s for s in info.get('streams',[]) if s.get('codec_type')=='video'),{})
            if not 1<=int(video.get('width',0))<=16384 or not 1<=int(video.get('height',0))<=16384:
                raise ValueError('Bild unlesbar oder zu groß.')
    imported=[]
    for file in files:
        targetfolder=folder/pruefsumme(Path(file))[:16] if art=='audio' else folder
        imported.append(str(kopie(file,targetfolder,workflow.stop)))
        if art=='audio':
            registry['audio']=list(dict.fromkeys([*registry['audio'],imported[-1]]))
        else:
            registry['bilder'][key]=list(dict.fromkeys(imported))
            job=workflow.zustand['auftraege'][key]
            job.update(status='WARTET',hinweis='Neue Bildauswahl wird geprüft.')
            job.pop('vorschau',None)
        workflow.speichern()  # Jede vollständig geprüfte Auswahlkopie bleibt wiederaufnehmbar.
    workflow.vorbereiten()
    return len(imported)


def fundliste_neu(workflow):
    from .core import json_sicher
    backup=sicher(workflow.ordner/'PROTOKOLLE'/'SICHERUNGEN')
    backup.mkdir(parents=True,exist_ok=True)
    json_sicher(backup/('fundliste-'+secrets.token_hex(12)+'.json'),workflow.zustand)
    jobs=workflow.zustand['auftraege']
    remove=[k for k,j in jobs.items() if j.get('status') in {'WARTET','BEREIT'}
            and not j.get('versuche',0) and not any(j.get(x) for x in ('video','render_hash','video_ziel'))]
    for k in remove:del jobs[k]
    workflow._scan_cache.clear()
    workflow.speichern()  # Neustart zwischen Reset und Neuscan ist sicher.
    workflow.melden(f'Fundliste zurückgesetzt: {len(remove)} ungestartete Einträge. Auswahl und bearbeitete Aufträge bleiben erhalten.')
    return workflow.vorbereiten()


def signatur(paths):
    result=[]
    for p in paths:
        p=sicher(p);s=p.stat()
        result.append((str(p),s.st_size,s.st_mtime_ns,s.st_ctime_ns))
    return tuple(result)


def ordner_pruefen(cfg,anlegen=False):
    """Nur ausdrücklich konfigurierte Ordner; kein stiller Ersatzpfad."""
    downloads=sicher(cfg['downloads']);work=sicher(cfg['arbeitsordner'])
    if work==downloads or downloads in work.parents:
        raise ValueError('Arbeitsordner muss außerhalb der Downloads liegen.')
    if downloads==Path('/') or work in {Path('/'),Path.home()}:
        raise ValueError('Bitte einen eigenen Unterordner wählen, nicht das gesamte System oder Benutzerverzeichnis.')
    for p in (downloads,work):
        if p.exists() and not p.is_dir():raise ValueError('Als Ordner ist eine Datei eingestellt: '+str(p))
        ancestor=next((x for x in (p,*p.parents) if x.exists()),None)
        if ancestor is None or not ancestor.is_dir() or not os.access(ancestor,os.R_OK|os.W_OK|os.X_OK):
            raise ValueError('Ordner nicht lesbar oder beschreibbar: '+str(p))
    for name in ('PROTOKOLLE','EINGANG','BILDER','FERTIG','VERWENDET','AUSWAHL'):
        p=sicher(work/name)
        if p.exists() and not p.is_dir():raise ValueError('Arbeitsunterordner ist durch eine Datei blockiert: '+name)
    if anlegen:
        for p in (downloads,work):
            p.mkdir(parents=True,exist_ok=True);sicher(p)
    result=[]
    for name,p in (('Downloads',downloads),('Arbeitsordner',work)):
        present=p.is_dir();ok=present and os.access(p,os.R_OK|os.W_OK|os.X_OK)
        result.append({'name':name,'pfad':str(p),'vorhanden':present,'ok':ok,
                       'hinweis':'Vorhanden und verwendbar.' if ok else 'Fehlt. Über „Ordner prüfen & anlegen“ einrichten.'})
    return {'bereit':all(x['ok'] for x in result),'ordner':result}
