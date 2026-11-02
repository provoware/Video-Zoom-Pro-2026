"""WAV-Container vor Verarbeitung auf vollständig vorhandene Blöcke prüfen."""
import os
from pathlib import Path
import stat
import struct


class DownloadWartet(ValueError):
    """Noch unvollständiger oder während der Prüfung geänderter Eingang."""


def vollstaendig(pfad: Path):
    fd = os.open(pfad, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, 'rb') as stream:
        before = os.fstat(stream.fileno())
        if not stat.S_ISREG(before.st_mode):
            raise ValueError('WAV ist keine reguläre Datei.')
        header = stream.read(12)
        if len(header) < 12:
            raise DownloadWartet('WAV-Kopf noch unvollständig; Download abwarten.')
        kind = header[:4]
        if kind not in (b'RIFF', b'RIFX', b'RF64') or header[8:] != b'WAVE':
            raise ValueError('Ungültiger WAV-Dateikopf; Original prüfen.')
        endian = '>' if kind == b'RIFX' else '<'
        size = struct.unpack(endian+'I', header[4:8])[0]
        end = size+8
        rf_data = None
        if kind == b'RF64':
            chunk = stream.read(8)
            if len(chunk) != 8 or chunk[:4] != b'ds64':
                raise ValueError('RF64 benötigt einen gültigen ds64-Block.')
            length = struct.unpack('<I',chunk[4:])[0]
            content = stream.read(28)
            if length < 28 or len(content) != 28:
                raise DownloadWartet('RF64-Kopf noch unvollständig.')
            riffsize, rf_data = struct.unpack('<QQ',content[:16])
            end = riffsize+8
        if end > before.st_size or size == 0:
            raise DownloadWartet('WAV-Daten noch unvollständig; Download abwarten.')
        if end < 12 or end != before.st_size:
            raise ValueError('WAV-Größenangabe widerspricht dem Dateiinhalt.')
        offset=12
        fmt = data = False
        for _ in range(10000):
            if offset == end:
                break
            if offset+8 > end:
                raise ValueError('Ungültige WAV-Blockgrenze.')
            stream.seek(offset)
            chunk=stream.read(8)
            if len(chunk)!=8:
                raise DownloadWartet('WAV wurde während der Prüfung verkürzt.')
            name=chunk[:4]
            length=struct.unpack(endian+'I',chunk[4:])[0]
            if kind == b'RF64' and name == b'data' and length == 0xffffffff:
                length=rf_data
            limit=offset+8+length
            if limit>end:
                raise DownloadWartet('WAV-Nutzdaten noch unvollständig.')
            if name==b'fmt ':
                if length<16:
                    raise ValueError('WAV-Formatblock ist beschädigt.')
                fmt=True
            if name==b'data':
                if length==0:
                    raise DownloadWartet('WAV enthält noch keine vollständigen Tondaten.')
                data=True
            # Ein letzter ungerader Datenblock darf ohne Padding enden.
            offset=limit+(length%2 if limit<end else 0)
        else:
            raise ValueError('Zu viele WAV-Blöcke; Original prüfen.')
        after=os.fstat(stream.fileno())
        current=pfad.stat(follow_symlinks=False)
        fingerprint=lambda s:(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
        if fingerprint(before)!=fingerprint(after) or fingerprint(after)!=fingerprint(current):
            raise DownloadWartet('WAV wird noch verändert; später erneut prüfen.')
        if not fmt or not data:
            raise ValueError('WAV benötigt Format- und Tondatenblock.')
