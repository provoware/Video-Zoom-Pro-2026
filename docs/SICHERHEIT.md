# Sicherheit und Abhängigkeiten

Python 3.11+, FFmpeg/FFprobe mit zoompan, xfade, concat, scale, pad, libx264 und AAC. Für Rendern ist systemd --user mit CPUQuota und MemoryMax erforderlich. Ohne echte Begrenzung keine automatische Videoberechnung. Kein Tk, Qt, Node, Docker oder Cloud erforderlich.

Startdiagnose prüft Komponenten. Eine FFmpeg-Nachinstallation ist nur optional und nach apt-get-Simulation plus Zustimmung möglich. Simulierte Paketentfernungen und Updates blockieren automatische Reparatur.

Die Oberfläche bindet 127.0.0.1 und nutzt einen zufälligen Schlüssel, Host- und Origin-Prüfung. Fremde Browser- und Netzwerkzugriffe sind nicht vorgesehen.

Originaldateien sind bis zur verifizierten MP4-Ausgabe geschützt. Die Archivierung verwendet SHA-256; vor Entfernen der Quelldatei ist eine verifizierte Kopie notwendig. Journalfehler werden nie automatisch durch einen leeren Zustand überschrieben.

Offen: reale CPU-Messung, erweiterte HTTP-Sicherheitstests, Crash-Fault-Injektion und finale Systemabnahme.
