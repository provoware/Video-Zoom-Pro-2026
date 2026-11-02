"""Ausgewählte Bedienwerte mit Original-Sicherung zurücksetzen und zurückholen."""
import hashlib
import json
import os
from pathlib import Path
import re
import secrets
import stat
from .core import konfigurieren, konfiguration, json_sicher, lesen

GRUPPEN = {'ansicht': ('theme',), 'format': ('format', 'kategorie'),
           'bedienung': ('theme', 'format', 'kategorie')}


def sicher(pfad):
    pfad = Path(pfad).absolute()
    if any(p.is_symlink() for p in (pfad, *pfad.parents)):
        raise RuntimeError('Unsicherer Einstellungspfad; keine Änderung.')
    if pfad.exists() and not pfad.is_file():
        raise RuntimeError('Einstellungsdatei ist keine reguläre Datei.')
    return pfad


def _bytes(pfad):
    sicher(pfad)
    fd = os.open(pfad, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, 'rb') as stream:
        if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
            raise ValueError('Sicherung ist keine reguläre Datei.')
        data = stream.read(1024*1024+1)
    if len(data)>1024*1024:
        raise ValueError('Einstellungssicherung ist zu groß; keine Änderung.')
    return data


def _sync_ordner(pfad):
    fd=os.open(pfad,os.O_RDONLY|os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def zuruecksetzen(pfad, cfg, gruppe):
    if not isinstance(gruppe,str) or gruppe not in GRUPPEN:
        raise ValueError('Nur Farbschema, Format/Kategorie oder beide zurücksetzen.')
    pfad=sicher(pfad)
    marker=sicher(pfad.with_name(pfad.name+'.ruecksetzung.json'))
    defaults=konfiguration()
    neu=konfigurieren({**cfg, **{k:defaults[k] for k in GRUPPEN[gruppe]}})
    # Exakten alten Dateiinhalt erhalten, nicht nur neu serialisierte Werte.
    raw = _bytes(pfad) if pfad.exists() else (json.dumps(cfg,ensure_ascii=False)+'\n').encode()
    original=json.loads(raw)
    if not isinstance(original,dict):
        raise ValueError('Bestehende Einstellungen sind beschädigt; keine Änderung.')
    # Fremde Änderungen seit dem Laden niemals still überschreiben.
    if konfigurieren(original)!=konfigurieren(cfg):
        raise RuntimeError('Einstellungen wurden außerhalb dieser Oberfläche geändert. Oberfläche neu starten.')
    pfad.parent.mkdir(parents=True,exist_ok=True)
    sicher(pfad)
    backup=pfad.with_name(pfad.name+'.sicherung-'+secrets.token_hex(8)+'.json')
    fd=os.open(backup, os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
    with os.fdopen(fd,'wb') as stream:
        stream.write(raw);stream.flush();os.fsync(stream.fileno())
    json_sicher(marker,{'schema':1,'gruppe':gruppe,'datei':backup.name,
                        'sha256':hashlib.sha256(raw).hexdigest()})
    _sync_ordner(pfad.parent)  # Sicherung und Verweis vor der Änderung dauerhaft machen.
    json_sicher(pfad,neu)
    _sync_ordner(pfad.parent)
    return neu,backup.name


def wiederherstellen(pfad,cfg):
    pfad=sicher(pfad)
    marker=sicher(pfad.with_name(pfad.name+'.ruecksetzung.json'))
    beleg=lesen(marker,{})
    if beleg.get('schema')!=1 or not isinstance(beleg.get('gruppe'),str) or beleg.get('gruppe') not in GRUPPEN:
        raise ValueError('Keine gültige Rücksetzungssicherung vorhanden.')
    name=beleg.get('datei')
    if not isinstance(name,str) or not re.fullmatch(re.escape(pfad.name)+r'\.sicherung-[0-9a-f]{16}\.json',name):
        raise ValueError('Ungültiger Sicherungsname; keine Änderung.')
    raw=_bytes(pfad.with_name(name))
    if hashlib.sha256(raw).hexdigest()!=beleg.get('sha256'):
        raise ValueError('Sicherung wurde verändert; keine Wiederherstellung.')
    alt=json.loads(raw)
    if not isinstance(alt,dict):
        raise ValueError('Sicherung beschädigt; keine Änderung.')
    if not all(k in alt for k in GRUPPEN[beleg['gruppe']]):
        raise ValueError('Sicherung enthält die gewählten Werte nicht.')
    aktuell=lesen(pfad,cfg)
    if konfigurieren(aktuell)!=konfigurieren(cfg):
        raise RuntimeError('Einstellungen wurden außerhalb dieser Oberfläche geändert. Oberfläche neu starten.')
    # Nur damals zurückgesetzte Werte wiederherstellen, keine Pfade/Ressourcen.
    neu=konfigurieren({**cfg,**{k:alt[k] for k in GRUPPEN[beleg['gruppe']]}})
    json_sicher(pfad,neu)
    return neu
