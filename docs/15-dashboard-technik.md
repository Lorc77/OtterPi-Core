# OtterPi-Core – Dashboard Technik

**Dokument:** 15-dashboard-technik.md  
**Projekt:** OtterPi-Core  
**Dashboard:** otterpi Status Dashboard v3.3  
**Produktivdatei:** `/var/www/status/cgi-bin/status.cgi`  
**Stand:** August 2026

---

## 1. Zweck

Das OtterPi Status Dashboard ist eine bewusst schlanke CGI-Anwendung.

Es dient nicht als historisches Monitoring-System, sondern als direkte Zustandsanzeige des laufenden Systems.

Ziel:

> Aktuelle Systemzustände erfassen, bewerten und verständlich darstellen.

Das Dashboard soll insbesondere dabei helfen, Probleme schnell zu erkennen, ohne dafür zusätzliche Monitoring-Infrastruktur zu benötigen.

---

## 2. Technische Architektur

Der aktuelle Aufbau besteht aus:

```text
Browser
   |
   v
nginx
   |
   v
fcgiwrap
   |
   v
status.cgi
   |
   +-- /proc
   +-- /sys
   +-- systemd
   +-- Netzwerkbefehle
   +-- Raspberry-Pi-Hardwareinformationen
   |
   v
HTML-Ausgabe
```

Die CGI-Datei erzeugt die komplette HTML-Seite dynamisch bei jedem Aufruf.

Es gibt keine separate Backend-Anwendung und keine Datenbank.

---

## 3. Produktive Datei

Die produktive Dashboard-Datei befindet sich unter:

```text
/var/www/status/cgi-bin/status.cgi
```

Aktueller Stand:

```text
otterpi Status Dashboard v3.3
```

Die Datei enthält sowohl:

- Systemabfragen
- Statusberechnung
- HTML
- CSS

Die aktuelle Version ist damit bewusst als einzelnes, leicht verständliches Artefakt aufgebaut.

---

## 4. Entwicklungsdatei

Während der Entwicklung wurde zusätzlich mit einer separaten Version gearbeitet:

```text
~/status.cgi-dashboard-v3.3-dev
```

Nach Abschluss der Änderungen wurde der getestete Stand nach

```text
/var/www/status/cgi-bin/status.cgi
```

übernommen.

---

## 5. HTTP-Header

Die CGI-Anwendung sendet:

```text
Content-Type: text/html; charset=UTF-8
```

und:

```text
Cache-Control: no-store
```

### Bedeutung

`no-store` verhindert, dass Browser oder zwischengeschaltete Komponenten die Statusseite als zwischengespeicherte Momentaufnahme verwenden.

Bei einem Health Dashboard ist dies wichtig, weil nach einem Fehler oder Neustart möglichst immer der aktuelle Zustand angezeigt werden soll.

---

## 6. Systemzeit / Messzeitpunkt

Zu Beginn der CGI-Ausführung wird die aktuelle Systemzeit ermittelt:

```text
date '+%d.%m.%Y %H:%M:%S'
```

Die Ausgabe wird aktuell als

```text
Letzte Prüfung: ...
```

angezeigt.

Diese Zeit beschreibt den Zeitpunkt, zu dem die CGI-Seite erzeugt wurde.

Sie ist damit ein Mess- bzw. Prüfzeitpunkt und keine dauerhaft gespeicherte Historie.

---

## 7. Datenquellen

Das Dashboard verwendet bevorzugt direkte Linux-Systeminformationen.

Verwendete Quellen sind unter anderem:

```text
/proc/uptime
/proc/loadavg
/proc/meminfo
/proc/swaps
/proc/device-tree/model
/sys/class/thermal/
/sys/devices/system/cpu/
/sys/class/block/
/sys/class/net/
```

Zusätzlich werden Systemwerkzeuge verwendet, beispielsweise:

```text
hostname
uname
nproc
df
findmnt
lsblk
ip
systemctl
ps
free
vcgencmd
rfkill
who
```

Dadurch werden die Werte direkt vom laufenden System ermittelt.

---

## 8. Systeminformationen

Das Dashboard ermittelt aktuell:

- Hostname
- Hardwaremodell
- CPU-Kernzahl
- RAM-Größe
- Betriebssystem
- Kernel
- letzter Systemstart
- Uptime

Beispiel:

```text
Hostname:
otterpi

Hardware:
Raspberry Pi 4 Model B Rev 1.5
(4 Kerne, 1 GB RAM)

OS:
...

Kernel:
...

Letzter Start:
...

Uptime:
...
```

---

## 9. CPU-Temperatur

Die Temperatur wird aus:

```text
/sys/class/thermal/thermal_zone0/temp
```

gelesen.

Der Kernel liefert den Wert in Milligrad Celsius.

Beispielsweise:

```text
52000
```

wird zu:

```text
52.0 °C
```

Die Bewertung erfolgt über drei Zustände.

```text
< 65 °C       OK
65–80 °C      Warnung
>= 80 °C      Kritisch
```

---

## 10. CPU Load

Die drei Load-Werte werden aus:

```text
/proc/loadavg
```

gelesen.

Angezeigt werden:

```text
1 Minute
5 Minuten
15 Minuten
```

Zusätzlich besitzt jeder Wert eine visuelle Auslastungsanzeige.

Die aktuelle Skalierung orientiert sich an:

```text
Load 0        = 0 %
Load 4        = 100 %
```

Die Statusbewertung lautet:

```text
Load < 2.0       OK
Load < 3.5       Warnung
Load >= 3.5      Kritisch
```

Die Werte werden nicht mit der Anzahl der CPU-Kerne normalisiert.

---

## 11. CPU-Frequenz

Die aktuelle Frequenz wird aus:

```text
/sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq
```

gelesen.

Die maximale Frequenz wird aus:

```text
/sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_max_freq
```

ermittelt.

Die Werte werden von kHz in MHz beziehungsweise GHz umgerechnet.

Beispiel:

```text
CPU-Frequenz:
1800 MHz aktuell / 1.8 GHz max.
```

---

## 12. Prozessanzahl

Die Anzahl der laufenden Prozesse wird mit:

```text
ps -e --no-headers | wc -l
```

ermittelt.

Aktuell wird nur die Gesamtzahl angezeigt.

Eine spätere Version kann zusätzlich die CPU- und RAM-intensivsten Prozesse anzeigen.

---

## 13. RAM

Der Arbeitsspeicher wird über:

```text
/proc/meminfo
```

ermittelt.

Verwendet werden insbesondere:

```text
MemTotal
MemAvailable
```

Der verwendete Speicher wird berechnet als:

```text
MemTotal - MemAvailable
```

Die prozentuale Auslastung wird daraus berechnet.

Statusgrenzen:

```text
< 70 %       OK
70–85 %      Warnung
> 85 %       Kritisch
```

---

## 14. Swap

Die Swap-Nutzung wird über:

```text
free -m
```

ermittelt.

Zusätzlich wird:

```text
/proc/swaps
```

ausgewertet.

Damit kann das Dashboard erkennen:

- ob Swap vorhanden ist
- welches Gerät verwendet wird
- welcher Typ vorliegt
- ob der Swap aktiv ist

Ein Gerät wie:

```text
/dev/zram0
```

wird als:

```text
zram
```

dargestellt.

---

## 15. Swap-Bewertung

Bei aktivem Swap gelten:

```text
< 50 %       OK
50–80 %      Warnung
> 80 %       Kritisch
```

Ist kein Swap aktiv, wird der Zustand derzeit als Warnung behandelt.

Grund:

Das Dashboard erwartet beim aktuellen Systemaufbau zram-Swap.

---

## 16. Dateisystem

Die Root-Partition wird über:

```text
findmnt -rn -o SOURCE,FSTYPE,OPTIONS /
```

ermittelt.

Damit werden gleichzeitig erkannt:

- Quelle
- Dateisystem
- Mountoptionen

Beispiel:

```text
/dev/mmcblk0p2
ext4
rw,noatime,...
```

---

## 17. Root-Mountstatus

Das Dashboard prüft insbesondere, ob das Root-Dateisystem schreibbar ist.

Erwarteter Zustand:

```text
rw
```

Anzeige:

```text
beschreibbar (rw)
```

Wird das Root-Dateisystem unerwartet nur lesbar eingebunden:

```text
ro
```

wird dies als kritischer Zustand bewertet.

Dies ist relevant, weil ein Wechsel zu `ro` beispielsweise auf Dateisystemprobleme hinweisen kann.

---

## 18. Speicherplatz

Die Root-Dateisystembelegung wird mit:

```text
df -P -B1 /
```

ermittelt.

Angezeigt werden:

- Gesamtgröße
- verwendeter Speicher
- freier Speicher
- prozentuale Belegung

Bewertung:

```text
< 75 %       OK
75–90 %      Warnung
> 90 %       Kritisch
```

---

## 19. Inodes

Zusätzlich zur normalen Speicherbelegung wird die Inode-Nutzung über:

```text
df -i /
```

ermittelt.

Angezeigt werden:

- gesamte Inodes
- verwendete Inodes
- freie Inodes
- prozentuale Nutzung

Bewertung:

```text
< 80 %       OK
80–90 %      Warnung
> 90 %       Kritisch
```

Damit erkennt das Dashboard auch das Problem eines inodearmen Dateisystems.

---

## 20. Physisches Speichermedium

Ausgehend von der Root-Partition wird über:

```text
lsblk -nro PKNAME "$ROOT_DEVICE"
```

das physische Elterngerät ermittelt.

Anschließend werden Informationen aus dem entsprechenden sysfs-Pfad gelesen.

Aktuell werden nach Möglichkeit ermittelt:

```text
Modell
Typ
Herstellungsdatum
```

Fehlen diese Informationen, wird:

```text
nicht verfügbar
```

angezeigt.

---

## 21. Netzwerk

Aktuell werden ermittelt:

```text
IPv4
Gateway
IPv6
MAC-Adresse
```

Die IPv4-Adresse wird aktuell über:

```text
hostname -I
```

ermittelt.

Das Standard-Gateway wird aus:

```text
ip route
```

ermittelt.

Die globale IPv6-Adresse wird über:

```text
ip -6 addr show scope global
```

ermittelt.

---

## 22. Interface-Status

Aktuell überwacht das Dashboard:

```text
eth0
wlan0
```

Mögliche Zustände:

```text
verbunden
nicht verbunden
blockiert
deaktiviert
nicht vorhanden
```

Beim WLAN wird zusätzlich `rfkill` berücksichtigt.

Dadurch wird beispielsweise ein explizit blockiertes WLAN als:

```text
blockiert
```

dargestellt.

---

## 23. Netzwerkbewertung

Die aktuelle Version bewertet die Interfaces selbstständig.

Beispiel:

```text
LAN (eth0)
🟢 verbunden

WLAN (wlan0)
🔴 blockiert
```

Diese Bewertung beschreibt derzeit den Zustand des Interfaces.

Eine tatsächliche Ende-zu-Ende-Erreichbarkeitsprüfung von Gateway, DNS oder Internet ist noch nicht Bestandteil von v3.3.

Diese Funktion ist für eine spätere Dashboard-Version vorgesehen.

---

## 24. Dienste

Das Dashboard überwacht aktuell sieben systemd-Dienste:

```text
nginx
meshcentral
pihole-FTL
fcgiwrap
ssh
NetworkManager
systemd-timesyncd
```

Für jeden Dienst wird:

```text
systemctl is-active
```

ausgeführt.

---

## 25. Dienstzustände

Die systemd-Zustände werden für die Darstellung übersetzt.

Intern:

```text
active
activating
inactive
failed
```

Darstellung:

```text
aktiv
startet
gestoppt
fehlgeschlagen
```

Unbekannte Zustände werden als:

```text
unbekannt
```

angezeigt.

---

## 26. Dienstbewertung

Aktive Dienste werden als:

```text
🟢 aktiv
```

dargestellt.

Startende Dienste erzeugen eine Warnung.

Fehlgeschlagene Dienste erzeugen einen kritischen Zustand.

Gestoppte oder unbekannte Dienste werden aktuell nicht als kritischer Fehler eingestuft, sondern als Warnung beziehungsweise neutraler Zustand entsprechend der Gesamtbewertung behandelt.

---

## 27. Dienst-Gesamtstatus

Das Dashboard zählt:

```text
SERVICE_OK
SERVICE_TOTAL
SERVICE_WARNINGS
SERVICE_ERRORS
```

Beispiel:

```text
Dienste
7 / 7 aktiv
```

Der Dienststatus fließt außerdem in den globalen Gesamtstatus ein.

---

## 28. Raspberry-Pi-Hardwareintegrität

Die Raspberry-Pi-spezifische Hardwareprüfung verwendet:

```text
vcgencmd get_throttled
```

Der daraus gelesene Hexwert wird auf relevante Bitflags geprüft.

Überwacht werden:

- Unterspannung
- Frequenzbegrenzung
- Drosselung
- Temperatur-Limit

Dabei werden sowohl aktuell aktive als auch seit dem Boot aufgetretene Zustände berücksichtigt.

---

## 29. Gesamtstatus

Die einzelnen Prüfergebnisse werden über eine gemeinsame Statuslogik zusammengeführt.

Mögliche Zustände:

```text
ok
warn
critical
```

Zusätzlich existiert:

```text
unknown
```

Unbekannte Zustände werden bei der Gesamtbewertung grundsätzlich als Warnung behandelt.

---

## 30. Statuspriorität

Die Priorität lautet:

```text
critical
    >
warn / unknown
    >
ok
```

Damit kann beispielsweise ein einziger kritischer Fehler den Gesamtstatus auf:

```text
Kritisch
```

setzen.

Wenn kein kritischer Fehler existiert, aber mindestens eine Warnung vorhanden ist:

```text
Warnung
```

Nur wenn alle relevanten Prüfungen erfolgreich sind:

```text
OK
```

---

## 31. Warnungs- und Fehlerzähler

Das Dashboard zählt einzelne Befunde.

Angezeigt werden:

```text
Warnungen
Fehler
```

Die Zähler dienen dazu, den Gesamtstatus nachvollziehbarer zu machen.

Dabei wird eine fehlende Hardwareabfrage nicht mehrfach als vier identische Fehler gezählt.

Wenn die gesamte `vcgencmd`-Abfrage nicht verfügbar ist, wird dies als ein unbekannter Befund behandelt.

---

## 32. Darstellung

Die Benutzeroberfläche verwendet:

- HTML
- CSS
- CSS Grid
- responsive Layouts
- halbtransparente Karten
- farbige Statuslampen
- Fortschrittsbalken

Das Design ist bewusst eher eine Appliance-Oberfläche als ein klassisches Monitoring-Dashboard.

---

## 33. Hintergrund

Das Dashboard verwendet:

```text
/otter2.png
```

als Hintergrundbild.

Der Hintergrund wird durch eine dunkle transparente Ebene abgedunkelt, damit die Statusinformationen lesbar bleiben.

---

## 34. Responsive Verhalten

Für kleinere Displays wird das Layout angepasst.

Unterhalb von ungefähr:

```text
700px
```

werden unter anderem:

- zweispaltige Bereiche
- Dashboard-Grids

auf eine Spalte reduziert.

Damit bleibt das Dashboard auch auf Smartphones und Tablets verwendbar.

---

## 35. Keine Datenhaltung

Die CGI-Anwendung speichert selbst keine Messwerte.

Es existieren keine:

```text
Dashboard-Datenbank
History-Dateien
CSV-Messprotokolle
RRD-Dateien
```

für die Statuswerte.

Jeder Seitenaufruf erzeugt eine neue Momentaufnahme.

---

## 36. Vorteile dieses Ansatzes

Die direkte Abfrage hat mehrere Vorteile:

- keine zusätzliche Datenbank
- keine zusätzlichen Dienste
- minimale Schreiblast
- keine Wartung einer Monitoring-Infrastruktur
- geringe Ressourcenanforderungen
- einfache Fehlersuche
- leichtes Backup
- einfaches Wiederherstellen

Das passt zum Appliance-Charakter des OtterPi.

---

## 37. Bewusst nicht Bestandteil von v3.3

Die aktuelle Version prüft noch nicht systematisch:

- Gateway-Erreichbarkeit
- DNS-Funktion
- Internet-Erreichbarkeit
- Dienst-Erreichbarkeit über Netzwerk
- erwartete offene Ports
- TLS-Zertifikatsablauf
- SSH-Sicherheitsstatus
- Update-Status
- Dienst-Laufzeiten
- Restart-Zähler
- Top-Prozesse
- detaillierte Hardware-/Firmware-Versionen
- Speichermedien-Temperatur
- SMART-Gesundheit

Diese Punkte gehören zur geplanten Weiterentwicklung.

---

## 38. Ziel für v3.4

Die nächste Entwicklungsstufe soll das Dashboard stärker von einer reinen Zustandsanzeige zu einem echten Selbstdiagnose-System entwickeln.

Leitgedanke:

> Nicht nur anzeigen, dass ein Dienst läuft, sondern möglichst feststellen, ob die Funktion tatsächlich erreichbar ist.

Geplante erste Erweiterungen:

1. Dienst-Erreichbarkeit
2. Gateway-Prüfung
3. DNS-Prüfung
4. optionale Internet-Prüfung
5. erwartete Portprüfung
6. Zertifikatsprüfung

---

## 39. Entwicklungsprinzip

Neue Prüfungen sollen möglichst:

- direkt auf dem vorhandenen System arbeiten
- keine zusätzliche Datenbank benötigen
- keine dauerhaften Dateien erzeugen
- keine unnötigen Dienste installieren
- keine permanente Schreiblast verursachen

Das Dashboard soll dadurch schlank bleiben.

---

## 40. Aktueller technischer Status

Produktiv:

```text
CGI                         OK
HTML-Ausgabe                OK
Responsive Layout           OK
Systeminformationen         OK
Ressourcenanzeige           OK
Netzwerkstatus              OK
Dienststatus                OK
Hardwareintegrität          OK
Gesamtstatus                OK
Cache-Control               no-store
```

Version:

```text
otterpi Status Dashboard v3.3
```

Produktive Datei:

```text
/var/www/status/cgi-bin/status.cgi
```

---

## 41. Leitlinie für die weitere Entwicklung

Das Dashboard soll kein vollständiges Enterprise-Monitoring-System werden.

Es soll ein kleines, zuverlässiges Diagnosewerkzeug für den OtterPi bleiben.

Die gewünschte Entwicklung lautet daher:

```text
v3.3
Statusanzeige
    ↓
v3.4
aktive Integritätsprüfung
    ↓
v4.x
ausgewählte zusätzliche Gesundheitsinformationen
```

Nicht geplant ist:

```text
vollständiges Monitoring-System
```

---

**OtterPi-Core**

> Aktuellen Zustand sehen. Probleme erkennen. Keine unnötige Infrastruktur bauen. 🦦
