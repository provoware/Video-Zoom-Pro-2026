"""Lokale Linux-Sensorik ohne zusätzliche Pakete oder Netzwerkzugriff."""
from __future__ import annotations
import os
from pathlib import Path
import shutil
import threading


class Sensoren:
    """Messwerte sind Beobachtungen, keine Garantie für CPUQuota oder GPU-Last."""

    def __init__(self):
        self._vorher = None
        self._lock = threading.Lock()

    def _cpu(self):
        try:
            values=[int(x) for x in Path("/proc/stat").read_text().splitlines()[0].split()[1:]]
            total=sum(values)
            idle=values[3] + (values[4] if len(values)>4 else 0)
        except (OSError, ValueError, IndexError):
            return None
        with self._lock:
            previous=self._vorher
            self._vorher=(total,idle)
        if previous is None:
            return None
        difference=total-previous[0]
        if difference<=0:
            return None
        return round(max(0,min(100,100*(1-(idle-previous[1])/difference))),1)

    def _mem(self):
        info={}
        try:
            for line in Path("/proc/meminfo").read_text().splitlines():
                if line.startswith(("MemTotal:","MemAvailable:")):
                    key,val=line.split(":",1)
                    info[key]=int(val.strip().split()[0])//1024
        except (OSError, ValueError, IndexError):
            return {}
        return {"ram_gesamt_mb":info.get("MemTotal"),"ram_verfuegbar_mb":info.get("MemAvailable")}

    def _prozess_ram(self):
        try:
            data=Path("/proc/self/status").read_text()
            value=next(line.split()[1] for line in data.splitlines() if line.startswith("VmRSS:"))
            return round(int(value)/1024,1)
        except (OSError, StopIteration, ValueError, IndexError):
            return None

    def lesen(self, ordner: Path):
        try:
            frei=round(shutil.disk_usage(ordner).free/1024**3,2)
        except OSError:
            frei=None
        kerne=len(os.sched_getaffinity(0)) if hasattr(os,"sched_getaffinity") else os.cpu_count()
        return {"cpu_system_auslastung_prozent":self._cpu(),"cpu_logische_kerne":kerne,
                "ram_prozess_mb":self._prozess_ram(),"freier_speicher_gb":frei,**self._mem()}
