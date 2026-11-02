"""Begrenzte Pipe-Abfrage und Stillstandsprüfung für eigene Renderprozesse."""
from __future__ import annotations
import os
from pathlib import Path
import selectors
import signal
import subprocess
import time


class ProduktionGestoppt(RuntimeError):
    """Bewusste Pause; verbraucht keinen technischen Fehlversuch."""


def cpu_arbeit(pid):
    """CPU-Zähler nur des gestarteten Prozesses und seiner aktuellen Kinder."""
    result = {}
    pending = [pid]
    while pending:
        current = pending.pop()
        if current in result:
            continue
        try:
            fields = Path(f"/proc/{current}/stat").read_text().rsplit(")", 1)[1].split()
            result[current] = int(fields[11]) + int(fields[12])
            pending.extend(map(int, Path(f"/proc/{current}/task/{current}/children").read_text().split()))
        except (OSError, ValueError, IndexError):
            continue
    return result


def beenden(proc, frist):
    """Eigene Sitzung beenden, danach gezielt erzwingen und aufräumen."""
    for sig in (signal.SIGTERM, signal.SIGKILL):
        try:
            os.killpg(proc.pid, sig)
        except ProcessLookupError:
            pass
        try:
            proc.wait(timeout=frist)
            # Auch verwaiste Kinder der eigenen Sitzung dürfen keine Pipes halten.
            if sig == signal.SIGTERM:
                try:
                    os.killpg(proc.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
            return
        except subprocess.TimeoutExpired:
            pass
    proc.wait(timeout=frist)


def rendern(command, stop, fortschritt, warnung, *, warnzeit=120,
            stillzeit=300, intervall=0.1, aufraeumfrist=5,
            uhr=time.monotonic, arbeit=cpu_arbeit):
    """Nur steigende Medienzeit ist Fortschritt; CPU-Arbeit verhindert Blindabbruch.

    Beide Pipes werden binär, nichtblockierend und pro Runde begrenzt geleert.
    stderr und unvollständige stdout-Zeilen bleiben auch bei defekten Kindern klein.
    """
    with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          start_new_session=True) as proc:
        try:
            with selectors.DefaultSelector() as selector:
                for stream in (proc.stdout, proc.stderr):
                    os.set_blocking(stream.fileno(), False)
                    selector.register(stream, selectors.EVENT_READ)
                rest = b""
                fehler = b""
                letztes_medium = 0
                zuletzt = uhr()
                aktiv = zuletzt
                gewarnt = False
                vorher = arbeit(proc.pid)
                while True:
                    if stop.is_set():
                        raise ProduktionGestoppt("Produktion angehalten; Auftrag bleibt gespeichert.")
                    for key, _ in selector.select(intervall):
                        data = os.read(key.fileobj.fileno(), 65536)
                        if not data:
                            selector.unregister(key.fileobj)
                        elif key.fileobj is proc.stderr:
                            fehler = (fehler + data)[-8192:]
                        else:
                            lines = (rest + data).split(b"\n")
                            rest = lines.pop()[-4096:]
                            for line in lines:
                                if line.startswith(b"out_time_ms="):
                                    try:
                                        wert = int(line.split(b"=", 1)[1])
                                    except ValueError:
                                        continue
                                    if wert > letztes_medium:
                                        letztes_medium = wert
                                        zuletzt = aktiv = uhr()
                                        gewarnt = False
                                        fortschritt(wert)
                    now = uhr()
                    aktuell = arbeit(proc.pid)
                    if any(value > vorher.get(pid, 0) for pid, value in aktuell.items()):
                        aktiv = now
                    vorher = aktuell
                    if now - zuletzt >= warnzeit and not gewarnt:
                        warnung("Seit 120 Sekunden kein neuer Medienfortschritt; Renderprozess wird geprüft.")
                        gewarnt = True
                    if now - zuletzt >= stillzeit and now - aktiv >= stillzeit:
                        raise RuntimeError("TIMEOUT: Kein Medienfortschritt und keine nachweisbare CPU-Arbeit; Auftrag bleibt erhalten.")
                    code = proc.poll()
                    if code is not None and not selector.get_map():
                        if code:
                            raise RuntimeError(f"FFmpeg Exitcode {code}: " + fehler.decode("utf-8", "replace")[-900:])
                        return
        finally:
            beenden(proc, aufraeumfrist)
