"""Kleine echte WAV-/PNG-Dateien für reproduzierbare Tests, nur Standardbibliothek."""
from __future__ import annotations
import math
from pathlib import Path
import struct
import wave
import zlib


def wav(datei: Path, sekunden=4, rate=8000):
    datei.parent.mkdir(parents=True,exist_ok=True)
    with wave.open(str(datei),"wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        samples=bytearray()
        for i in range(sekunden*rate):
            sample=int(11000*math.sin(2*math.pi*220*i/rate))
            samples.extend(struct.pack("<h",sample))
        w.writeframes(bytes(samples))
    return datei


def png(datei: Path, rgb=(190,30,90), breite=64, hoehe=48):
    def chunk(name,data):
        return struct.pack(">I",len(data))+name+data+struct.pack(">I",zlib.crc32(name+data)&0xffffffff)
    pixel=bytes(rgb)*breite
    raw=b"".join(b"\0"+pixel for _ in range(hoehe))
    output=(b"\x89PNG\r\n\x1a\n"
            +chunk(b"IHDR",struct.pack(">IIBBBBB",breite,hoehe,8,2,0,0,0))
            +chunk(b"IDAT",zlib.compress(raw))
            +chunk(b"IEND",b""))
    datei.parent.mkdir(parents=True,exist_ok=True)
    datei.write_bytes(output)
    return datei


if __name__ == "__main__":
    root=Path(__file__).resolve().parent
    wav(root/"TEST_SONG_suno-com-abc123_20261101.wav")
    png(root/"TEST_BILD_01.png")
    png(root/"TEST_BILD_02.png",(25,140,210))
    print("Drei Testdateien erzeugt:",root)
