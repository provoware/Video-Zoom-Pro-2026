"""Echte synthetische Unterprozesse statt nachgebauter Pipe-Mocks."""
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path
from unittest.mock import patch
from videozoom.render_watchdog import rendern, ProduktionGestoppt
from videozoom.core import Workflow


class WatchdogTests(unittest.TestCase):
    def run_child(self, code, **kwargs):
        events, warnings = [], []
        rendern([sys.executable, '-u', '-c', code], kwargs.pop('stop', threading.Event()),
                events.append, warnings.append, warnzeit=.08, stillzeit=.2,
                intervall=.01, aufraeumfrist=.1, **kwargs)
        return events, warnings

    def test_stummer_stdout_offen_zeitlich_begrenzt(self):
        start = time.monotonic()
        with self.assertRaisesRegex(RuntimeError, 'TIMEOUT'):
            self.run_child('import time; time.sleep(20)', arbeit=lambda _: {})
        self.assertLess(time.monotonic() - start, 2)

    def test_fortschritt_darf_gesamtbudget_ueberschreiten(self):
        events, _ = self.run_child('import time\nfor i in range(1,9):\n print("out_time_ms="+str(i)); time.sleep(.05)')
        self.assertEqual(events, list(range(1,9)))

    def test_wiederholte_oder_ruecklaeufige_medienzeit_ist_kein_fortschritt(self):
        with self.assertRaisesRegex(RuntimeError, 'TIMEOUT'):
            self.run_child('import time\nwhile True:\n print("out_time_ms=1\\nout_time_ms=0"); time.sleep(.01)', arbeit=lambda _: {})

    def test_voller_stderr_und_unvollstaendige_zeile(self):
        events, _ = self.run_child('import os\nos.write(2,b"x"*2000000)\nos.write(1,b"z"*2000000+b"\\n")\nprint("out_time_ms=4")')
        self.assertEqual(events, [4])

    def test_exitcode_mit_begrenzter_fehlerausgabe(self):
        with self.assertRaisesRegex(RuntimeError, 'Exitcode 7') as err:
            self.run_child('import sys; print("x"*100000,file=sys.stderr); sys.exit(7)')
        self.assertLess(len(str(err.exception)), 1000)

    def test_stop_auch_bei_sigterm_resistentem_kind(self):
        stop = threading.Event()
        timer = threading.Timer(.1, stop.set)
        timer.start()
        try:
            start = time.monotonic()
            with self.assertRaises(ProduktionGestoppt):
                self.run_child('import signal,time; signal.signal(signal.SIGTERM,signal.SIG_IGN); time.sleep(20)', stop=stop)
            self.assertLess(time.monotonic()-start, 2)
        finally:
            timer.cancel()

    def test_cpu_arbeit_verhindert_blinden_abbruch(self):
        counter = iter(range(10000))
        _, warnings = self.run_child('import time; time.sleep(.4)', arbeit=lambda _: {1: next(counter)})
        self.assertTrue(warnings)

    def test_stop_verbraucht_keinen_versuch_wiederanlauf(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            downloads = root/'Downloads'; downloads.mkdir()
            svc = Workflow({'downloads':str(downloads),'arbeitsordner':str(root/'Arbeit')},testmodus=True)
            job = {'titel':'pause','status':'BEREIT','versuche':2,'dateien':[],'laenge':1}
            svc.zustand['auftraege']['pause'] = job
            with patch.object(svc,'_render',side_effect=ProduktionGestoppt('Pause')):
                self.assertEqual(svc.stapel(), (0,1))
            self.assertEqual(job['versuche'],2)
            self.assertEqual(job['status'],'PAUSIERT')
            reloaded = Workflow(svc.cfg,testmodus=True)
            self.assertEqual(reloaded.zustand['auftraege']['pause']['versuche'],2)

    def test_timeout_sichert_teilvideo_und_originale(self):
        from videozoom.core import pruefsumme
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            downloads = root/'Downloads'; downloads.mkdir()
            svc = Workflow({'downloads':str(downloads),'arbeitsordner':str(root/'Arbeit')},testmodus=True)
            audio = root/'original.wav'; audio.write_bytes(b'original-audio')
            image = root/'original.png'; image.write_bytes(b'original-image')
            entries = [{'pfad':str(p),'sha256':pruefsumme(p)} for p in (audio,image)]
            job = {'titel':'still','status':'BEREIT','dateien':entries,'laenge':1}
            def command(a, images, teil, *args):
                return [sys.executable,'-u','-c',
                        'import pathlib,time; pathlib.Path('+repr(str(teil))+').write_bytes(b"partial"); time.sleep(20)']
            def kurz(*args):
                return rendern(*args,warnzeit=.05,stillzeit=.15,intervall=.01,
                               aufraeumfrist=.1,arbeit=lambda _: {})
            with patch('videozoom.core.ffmpeg_befehl',side_effect=command), patch('videozoom.core.rendern',side_effect=kurz):
                with self.assertRaisesRegex(RuntimeError,'TIMEOUT'):
                    svc._render(job)
            self.assertEqual(audio.read_bytes(),b'original-audio')
            self.assertEqual(image.read_bytes(),b'original-image')
            self.assertFalse(Path(job['video_ziel']).exists())
            self.assertTrue(any(p.read_bytes()==b'partial' for p in svc.ordner.rglob('*') if p.is_file()))
