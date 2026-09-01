# OtterPi-Core – Systembasis

**Dokument:** 10-systembasis.md  
**Projekt:** OtterPi-Core  
**System:** otterpi  
**Stand:** August 2026  
**Status:** produktiv

---

## 1. Zweck dieses Dokuments

Dieses Dokument beschreibt die technische Basis des OtterPi-Systems.

Es dient als Referenz für:

- Hardware
- Betriebssystem
- Architektur
- Dateisystem
- Speicher
- Netzwerk-Grundkonfiguration
- Bootverhalten
- grundlegende Systemparameter

Das Dokument beschreibt den **Ist-Zustand** und ist kein Installationsleitfaden.

Änderungen am System sollen möglichst nachvollziehbar dokumentiert und bei relevanten Änderungen in einem neuen Snapshot festgehalten werden.

---

## 2. Host

Hostname:

```text
otterpi
```

Der Raspberry Pi stellt die zentrale Infrastruktur des privaten Heimservers bereit.

Das System ist als dauerhaft laufende Appliance ausgelegt.

Grundprinzip:

> möglichst wenig zusätzliche Software, möglichst wenig dauerhafte Schreiblast und möglichst einfache Wartbarkeit.

---

## 3. Hardware

Hardware:

```text
Raspberry Pi 4 Model B Rev 1.5
```

CPU:

```text
4 Kerne
```

Architektur:

```text
arm64
```

Arbeitsspeicher:

```text
1 GB RAM
```

Speicher:

```text
microSD-Karte
```

Aktueller erkannter Speicher:

```text
ca. 58 GB
```

---

## 4. Betriebssystem

Das System verwendet ein Linux-Betriebssystem auf Raspberry-Pi-Basis.

Die konkrete OS-Version wird vom Dashboard aus `/etc/os-release` ausgelesen.

Kernel-Version wird dynamisch über

```text
uname -r
```

ermittelt.

Damit zeigt das Dashboard immer den tatsächlich laufenden Kernel und nicht einen manuell eingetragenen Versionsstand.

---

## 5. Dateisystem

Root-Dateisystem:

```text
ext4
```

Das Root-Dateisystem befindet sich auf der microSD-Karte.

Die Mount-Konfiguration verwendet:

```text
noatime
```

### Zweck von `noatime`

Bei `noatime` werden Zugriffszeiten von Dateien nicht bei jedem Lesezugriff aktualisiert.

Dadurch werden unnötige Schreibzugriffe auf die SD-Karte reduziert.

Dies entspricht der grundsätzlichen OtterPi-Philosophie:

> Die SD-Karte soll möglichst wenig durch vermeidbare Hintergrundschreibvorgänge belastet werden.

---

## 6. Speicherzustand

Snapshot vom 05.08.2026:

```text
Filesystem      Size   Used   Avail
/dev/mmcblk0p2   58G    11G    46G
```

Belegung:

```text
19 %
```

Damit besteht aktuell ausreichend freier Speicher.

Das Dashboard überwacht sowohl:

- Speicherplatz
- freien Speicher
- Inode-Auslastung

Die Inode-Auslastung wird separat bewertet, da ein Dateisystem auch bei ausreichend freiem Speicherplatz durch erschöpfte Inodes problematisch werden kann.

---

## 7. Boot-Partition

Boot-Dateisystem:

```text
/dev/mmcblk0p1
```

Größe:

```text
ca. 505 MB
```

---

## 8. Relevante Verzeichnisse

### MeshCentral

```text
/opt/meshcentral/
```

Größe im Snapshot:

```text
ca. 773 MB
```

### Pi-hole

```text
/opt/pihole/
```

Größe im Snapshot:

```text
ca. 216 KB
```

### Scratch

```text
/opt/Scratch/
```

Größe im Snapshot:

```text
ca. 421 MB
```

### Widevine

```text
/opt/WidevineCdm/
```

Größe im Snapshot:

```text
ca. 9.9 MB
```

Die Größen dienen als Momentaufnahme und sind keine festen Sollwerte.

---

## 9. Netzwerk-Grundkonfiguration

Primäres LAN-Interface:

```text
eth0
```

IPv4-Adresse im lokalen Netz:

```text
192.168.178.100/24
```

Gateway:

```text
192.168.178.1
```

Das Gateway ist die lokale Fritz!Box.

---

## 10. IPv6

IPv6 ist auf dem System aktiviert.

Vorhanden sind:

- globale IPv6-Adressen
- ULA-IPv6-Adressen

Das System ist daher grundsätzlich IPv6-fähig.

Die externe Erreichbarkeit wird zusätzlich durch die eingesetzte Netzwerk- und CDN-Struktur bestimmt.

IPv6 ersetzt nicht vollständig die IPv4-Erreichbarkeit.

Insbesondere für:

- DS-Lite-Umgebungen
- IPv4-only-Netze
- Fremdnetze
- Universitätsnetze

bleibt der externe CDN-Zugang relevant.

---

## 11. WLAN

Das Interface

```text
wlan0
```

ist vorhanden.

Zum Zeitpunkt des Snapshots:

```text
Status: DOWN
```

Das System verwendet damit aktuell Ethernet als aktive Netzwerkverbindung.

WLAN ist vorhanden, wird aber nicht als primärer Netzwerkweg verwendet.

---

## 12. Netzwerk-Schnittstellen

Das Dashboard unterscheidet mindestens:

```text
LAN (eth0)
WLAN (wlan0)
```

Dabei wird nicht nur die Existenz eines Interfaces geprüft.

Für das Interface wird versucht zu unterscheiden zwischen:

- verbunden
- nicht verbunden
- deaktiviert
- blockiert
- nicht vorhanden

Beim WLAN wird zusätzlich `rfkill` berücksichtigt.

Dadurch kann ein blockiertes WLAN beispielsweise von einem lediglich nicht verbundenen WLAN unterschieden werden.

---

## 13. MAC-Adresse

Die MAC-Adresse des Ethernet-Interfaces wird dynamisch aus

```text
/sys/class/net/eth0/address
```

gelesen.

Sie wird nicht fest im Dashboard hinterlegt.

---

## 14. Systemstart

Das System startet grundsätzlich automatisch.

Nach einem Raspberry-Pi-Neustart wurden erfolgreich automatisch gestartet:

- MeshCentral
- nginx
- Zertifikatsmonitor
- Zertifikatsmonitor-Timer
- Pi-hole
- weitere systemrelevante Dienste

Der automatische Dienststart wurde im Rahmen der Systemtests geprüft.

---

## 15. Uptime

Die Systemlaufzeit wird direkt aus

```text
/proc/uptime
```

ermittelt.

Das Dashboard wandelt die Laufzeit in eine für Menschen lesbare Darstellung um, beispielsweise:

```text
14 Tage, 3 Stunden, 21 Minuten
```

Dadurch ist keine Speicherung historischer Uptime-Daten notwendig.

---

## 16. Letzter Systemstart

Der letzte Systemstart wird über `who -b` ermittelt.

Das Dashboard stellt ihn beispielsweise als

```text
07. August 2026, 02:14 Uhr
```

dar.

Auch diese Information wird nicht gespeichert, sondern bei jeder Dashboard-Anfrage direkt aus dem laufenden System ermittelt.

---

## 17. Ressourcen-Grundüberwachung

Das aktuelle Dashboard überwacht bereits:

- CPU-Temperatur
- Load Average
- CPU-Frequenz
- RAM
- Swap
- Root-Dateisystem
- Speicherplatz
- Inodes
- Prozessanzahl

Die Daten stammen direkt aus dem laufenden System.

Es gibt dafür keine zusätzliche Monitoring-Datenbank.

---

## 18. RAM

Das System verfügt über:

```text
1 GB RAM
```

Das Dashboard verwendet für die Speicherbewertung `MemAvailable` aus

```text
/proc/meminfo
```

Dadurch wird nicht einfach nur der momentan ungenutzte Speicher betrachtet.

Die RAM-Auslastung wird als Prozentwert dargestellt und in drei Zustände eingeteilt:

```text
OK
Warnung
Kritisch
```

Aktuelle Schwellenwerte:

```text
< 70 %      OK
70–85 %     Warnung
> 85 %      Kritisch
```

---

## 19. Swap / zram

Das System verwendet zram-Swap.

Das Dashboard erkennt das Swap-Gerät dynamisch über:

```text
/proc/swaps
```

Wird ein Gerät wie

```text
/dev/zram0
```

gefunden, wird es als

```text
zram
```

angezeigt.

Zusätzlich werden angezeigt:

- Gesamtgröße
- belegter Swap
- verfügbarer Swap
- prozentuale Nutzung
- Gerät
- Typ
- Status

---

## 20. CPU

Die CPU besteht aus:

```text
4 Kernen
```

Das Dashboard zeigt derzeit:

- Load Average 1 Minute
- Load Average 5 Minuten
- Load Average 15 Minuten
- aktuelle CPU-Frequenz
- maximale CPU-Frequenz
- CPU-Temperatur
- Anzahl laufender Prozesse

Eine echte prozentuale CPU-Auslastung ist für eine spätere Dashboard-Version vorgesehen.

---

## 21. Temperaturüberwachung

Die CPU-Temperatur wird über den Linux-Thermal-Subsystem-Pfad ausgelesen:

```text
/sys/class/thermal/thermal_zone0/temp
```

Der Wert wird in Grad Celsius umgerechnet.

Aktuelle Bewertung:

```text
< 65 °C       OK
65–80 °C      Warnung
>= 80 °C      Kritisch
```

Die Temperatur wird nicht dauerhaft gespeichert.

---

## 22. Raspberry-Pi-Hardwareintegrität

Auf Raspberry-Pi-Systemen wird zusätzlich versucht, den Hardwarestatus über

```text
vcgencmd get_throttled
```

zu ermitteln.

Damit können insbesondere Zustände wie folgende erkannt werden:

- Unterspannung
- Frequenzbegrenzung
- Drosselung
- Temperatur-Limit

Dabei wird zwischen momentan aktiven Problemen und Problemen unterschieden, die seit dem Start aufgetreten sind.

Beispiel:

```text
OK
seit Start aufgetreten
aktuell aktiv
```

Falls `vcgencmd` nicht verfügbar ist oder keine verwertbaren Daten liefert, wird der Hardwarestatus als unbekannt behandelt.

---

## 23. Gesamtstatus

Das Dashboard fasst die einzelnen Prüfungen zu einem Gesamtstatus zusammen.

Mögliche Zustände:

```text
OK
Warnung
Kritisch
```

Dabei gilt grundsätzlich:

```text
mindestens ein kritischer Befund
        ↓
Gesamtstatus Kritisch
```

ansonsten:

```text
mindestens eine Warnung
        ↓
Gesamtstatus Warnung
```

ansonsten:

```text
alles OK
        ↓
Gesamtstatus OK
```

Die Anzahl von Warnungen und Fehlern wird zusätzlich angezeigt.

---

## 24. Keine dauerhafte Monitoring-Datenbank

Das OtterPi-System verwendet bewusst keine Infrastruktur wie:

```text
InfluxDB
Grafana
Prometheus
```

für das Status-Dashboard.

Das Dashboard ist ausdrücklich kein historisches Monitoring-System.

Es ist ein:

> Appliance Health Monitor

Der Schwerpunkt liegt auf dem aktuellen Zustand und der Erkennung konkreter Probleme.

---

## 25. Schreiblast

Bei der Systemauslegung wurde bewusst auf geringe Schreiblast geachtet.

Bereits umgesetzt sind unter anderem:

- `noatime`
- deaktiviertes Pi-hole Query Logging
- kleines Journald
- Logrotate
- fstrim
- DynDNS-Aufruf ohne Logdatei
- keine Monitoring-Datenbank
- keine permanente Dashboard-Historie

Das Ziel ist eine möglichst langlebige und wartungsarme SD-Karte.

---

## 26. Systemphilosophie

Der OtterPi ist bewusst kein universeller Server für beliebig viele Anwendungen.

Die technische Leitlinie lautet:

> Wenige Dienste, klare Aufgaben, wenig Hintergrundaktivität und nachvollziehbare Zustände.

Neue Komponenten sollen deshalb nicht allein deshalb installiert werden, weil sie technisch möglich sind.

Vor jeder Erweiterung ist zu prüfen:

1. Wird die Funktion tatsächlich benötigt?
2. Kann sie ohne zusätzlichen dauerhaften Dienst umgesetzt werden?
3. Erzeugt sie zusätzliche Schreiblast?
4. Erhöht sie die Wartungskomplexität?
5. Ist sie für den Appliance-Charakter des Systems sinnvoll?

---

## 27. Aktueller Basisstatus

Zum dokumentierten Stand ist die Systembasis produktionsfähig.

Zusammenfassung:

```text
Hostname             otterpi
Hardware             Raspberry Pi 4 Model B Rev 1.5
CPU                  4 Kerne
RAM                  1 GB
Architektur          arm64
Speicher             ca. 58 GB microSD
Dateisystem           ext4
Mount-Optimierung     noatime
LAN                   eth0
IPv4                  192.168.178.100/24
Gateway               192.168.178.1
IPv6                  aktiv
WLAN                  vorhanden, aktuell DOWN
```

Die Systembasis bildet die Grundlage für:

- Service Portal
- Status Dashboard
- MeshCentral
- Pi-hole
- Netzwerkdienste
- weitere bewusst schlanke Heimserver-Funktionen

---

## 28. Dokumentationsregel

Dieses Dokument beschreibt den dokumentierten Basisstand.

Bei wesentlichen Änderungen sollen nicht einfach alte Werte überschrieben werden.

Stattdessen sollte ein neuer Snapshot mit Datum erstellt werden.

Beispiele:

```text
snapshot-2026-08-05.md
snapshot-2026-09-xx.md
```

Das Repository soll dadurch nicht nur eine Sammlung von Konfigurationsdateien sein, sondern gleichzeitig eine nachvollziehbare technische Dokumentation des OtterPi-Systems.

---

**OtterPi-Core**

> Kleine Infrastruktur. Klare Zustände. Wenig Magie. 🦦
