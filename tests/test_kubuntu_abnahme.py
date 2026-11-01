"""Der Kubuntu-Pruefer darf nicht ohne belegte Grenzen gruene Ergebnisse liefern."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import kubuntu_abnahme as abnahme


class Grenzen(unittest.TestCase):
    def cfg(self):
        return {"cpu_prozent": 30, "ram_mb": 2048}

    def test_cgroup_v2_cpu_und_ram_verifiziert(self):
        messung = {
            "cpu_max": "120000 100000",
            "memory_max": str(2048 * 1024 * 1024),
            "gemessene_cpu_kerne": 1.16,
        }
        result = abnahme.grenzen_auswerten(messung, self.cfg(), 4)
        self.assertEqual(result["status"], "BESTANDEN")
        self.assertTrue(result["regel_aktiv"])

    def test_unbegrenzter_scope_niemals_bestanden(self):
        messung = {"cpu_max": "max 100000", "memory_max": "max",
                   "gemessene_cpu_kerne": 0.01}
        self.assertEqual(
            abnahme.grenzen_auswerten(messung, self.cfg(), 4)["status"],
            "NICHT_BESTANDEN",
        )

    def test_falsche_cpu_quote_nicht_bestanden(self):
        messung = {"cpu_max": "30000 100000",
                   "memory_max": str(2048 * 1024 * 1024),
                   "gemessene_cpu_kerne": .25}
        result = abnahme.grenzen_auswerten(messung, self.cfg(), 4)
        self.assertEqual(result["status"], "PRUEFEN")
        self.assertFalse(result["regel_aktiv"])

    def test_zu_hohe_messung_ist_nicht_gruen(self):
        messung = {"cpu_max": "120000 100000",
                   "memory_max": str(2048 * 1024 * 1024),
                   "gemessene_cpu_kerne": 2.5}
        self.assertEqual(
            abnahme.grenzen_auswerten(messung, self.cfg(), 4)["status"],
            "PRUEFEN",
        )

    def test_systemd_fehlt_fuehrt_zu_pruefung_offen(self):
        with patch("kubuntu_abnahme.shutil.which", return_value=None):
            result = abnahme.cpu_scope_pruefen(self.cfg(), 4)
        self.assertEqual(result["status"], "NICHT_VERFUEGBAR")

    def test_scope_ist_wirklich_die_renderquote(self):
        sample = {
            "cpu_max": "120000 100000",
            "memory_max": str(2048 * 1024 * 1024),
            "gemessene_cpu_kerne": 1.15,
            "sekunden": 2.5,
        }
        with patch("kubuntu_abnahme.shutil.which", return_value="/usr/bin/systemd-run"), \
             patch("videozoom.core.os.sched_getaffinity", return_value=set(range(4)), create=True), \
             patch("kubuntu_abnahme.subprocess.run",
                   return_value=subprocess.CompletedProcess([], 0, json.dumps(sample), "")) as called:
            result = abnahme.cpu_scope_pruefen(self.cfg(), 4)
        self.assertEqual(result["status"], "BESTANDEN")
        self.assertIn("CPUQuota=120%", called.call_args.args[0])
        self.assertIn("MemoryMax=2048M", called.call_args.args[0])

    def test_sichtpruefung_niemals_automatisch_freigegeben(self):
        with patch("kubuntu_abnahme.desktop_info", return_value={
            "logische_cpu_zugaenglich": 4
        }), patch("kubuntu_abnahme.cpu_scope_pruefen",
                  return_value={"status": "BESTANDEN"}):
            report = abnahme.abnahmebericht(cpu_test=True)
        self.assertFalse(report["stable_freigabe"])
        self.assertTrue(all(v == "OFFEN" for v in report["sichtpruefung"].values()))


if __name__ == "__main__":
    unittest.main()
