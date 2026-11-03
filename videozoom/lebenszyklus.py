"""Kooperatives Beenden, Fenster-Anwesenheit und letzter bestätigter Datenstand."""
from contextlib import contextmanager
import signal
import threading
import time


@contextmanager
def abbruchsignale(stop):
    old={}
    if threading.current_thread() is threading.main_thread():
        for sig in (signal.SIGINT,signal.SIGTERM,signal.SIGHUP):
            old[sig]=signal.getsignal(sig)
            signal.signal(sig,lambda *_: stop.set())
    try:
        yield
    finally:
        for sig,handler in old.items():signal.signal(sig,handler)


class Lebenszyklus:
    """Kein Prozesskill: Auftrag kooperativ anhalten, unter Schreibsperre sichern."""
    def __init__(self,bedienung,server,*,browser=False,uhr=time.monotonic):
        self.ui,self.server,self.uhr=bedienung,server,uhr
        self.clients={}
        self.sequenzen={}
        self.lock=threading.Lock()
        self.angefordert=threading.Event()
        self.fertig=threading.Event()
        self.grund=''
        self.pending_cfg=None
        self.pending_base=None
        self.erster_start=self.uhr() if browser else None
        self.fenster_frueher=False
        self.last_exit=None
        self.thread=threading.Thread(target=self._lauf,daemon=True,name='videozoom-beenden')

    def fenster(self,key,aktion,hidden=False,cfg=None,base=None,seq=None):
        if not isinstance(key,str) or not 1<=len(key)<=80 or not all(c.isalnum() or c in '-_' for c in key):
            raise ValueError('Ungültige Fensterkennung.')
        if aktion not in {'da','weg'}:raise ValueError('Unbekannte Fensteraktion.')
        with self.lock:
            if seq is not None:
                if not isinstance(seq,int) or isinstance(seq,bool) or seq<0:raise ValueError('Ungültige Fensterfolge.')
                if seq<=self.sequenzen.get(key,-1):return
                self.sequenzen[key]=seq
                if len(self.sequenzen)>256:
                    for oldkey in list(self.sequenzen):
                        if oldkey not in self.clients and oldkey!=key:
                            del self.sequenzen[oldkey];break
            self.fenster_frueher=True
            if aktion=='da':
                self.pending_cfg=None;self.pending_base=None
                if key not in self.clients and len(self.clients)>=32:raise ValueError('Zu viele Fenster.')
                self.clients[key]=(self.uhr(),bool(hidden));self.last_exit=None
            else:
                self.clients.pop(key,None)
                if not self.clients:self.last_exit=self.uhr()
                if isinstance(cfg,dict) and base==self.ui.cfg and not self.clients:
                    self.pending_cfg=cfg;self.pending_base=dict(base)

    def anfordern(self,grund='Bewusstes Beenden'):
        self.grund=grund
        with self.ui.lock:
            self.ui.beenden_fehler=None
            self.ui.schliesst=True
            self.ui.dialog_stop.set()
            if self.ui.service:self.ui.service.stop.set()
        self.angefordert.set()

    def fenster_verlassen(self):
        now=self.uhr()
        with self.lock:
            for key,(last,hidden) in list(self.clients.items()):
                # Hintergrundtimer werden von Browsern stark gedrosselt.
                if now-last>(600 if hidden else 90):del self.clients[key]
            if self.clients:return False
            if self.last_exit is not None:return now-self.last_exit>=8
            if self.fenster_frueher:return True
            # Öffnen fehlgeschlagen: keine endlos verwaiste lokale Bedienoberfläche.
            return self.erster_start is not None and now-self.erster_start>=120

    def sichern(self):
        worker=self.ui.thread
        if worker and worker is not threading.current_thread():
            # Kopier-/Archivgrenze sicher abschließen; niemals Thread/Quelldaten abwürgen.
            while worker.is_alive():worker.join(.2)
        service=self.ui.service
        if service and not self.ui._anderer_schreiber():
            service.sperren()
            try:service.speichern()
            finally:service.freigeben()
        if self.pending_cfg is not None and self.pending_base==self.ui.cfg:
            try:self.ui.einstellungen(self.pending_cfg,beim_beenden=True)
            except (ValueError,RuntimeError) as exc:
                self.ui._meldung('Ungespeicherte ungültige Eingabe verworfen; letzte gültige Einstellungen bleiben: '+str(exc))
        self.ui._meldung('Daten gesichert. Lokaler Server wird beendet.')

    def _lauf(self):
        while not self.fertig.is_set():
            if not self.angefordert.wait(1):
                if not self.fenster_verlassen():continue
                self.anfordern('Letztes Browserfenster geschlossen oder Verbindung abgebrochen')
            if not self.ui.schliesst:self.anfordern('Betriebssystemsignal')
            try:
                self.sichern()
            except Exception as exc:
                self.ui._meldung('Speichern fehlgeschlagen; Server bleibt geöffnet: '+str(exc))
                with self.ui.lock:
                    self.ui.schliesst=False
                    self.ui.dialog_stop.clear()
                    self.ui.beenden_fehler=str(exc)
                self.angefordert.clear()
                # Keine automatische Fehlerschleife nach einem Speicherausfall.
                with self.lock:
                    self.fenster_frueher=False;self.last_exit=None;self.erster_start=None
                continue
            self.server.shutdown()
            self.fertig.set()

    def starten(self):
        self.thread.start()

    def abschliessen(self):
        if not self.fertig.is_set():self.anfordern('Serverende')
        # Auch externes server.shutdown() (z. B. Tests) räumt den eigenen Worker auf.
        self.thread.join(timeout=125)
        if self.thread.is_alive():
            raise RuntimeError('Speicherung noch nicht abgeschlossen; keine erfolgreiche Beendigung bestätigt.')
