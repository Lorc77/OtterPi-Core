# OtterPi Core – Status Dashboard v3.3

Stand: August 2026

## Produktiver Zustand

Das Status-Dashboard v3.3 ist produktiv.

Datei:

/var/www/status/cgi-bin/status.cgi

Entwicklungsstand:

~/status.cgi-dashboard-v3.3-dev

Das Dashboard läuft als Shell-CGI über fcgiwrap und nginx.

## Grundidee

Das Dashboard soll auf einen Blick beantworten:

„Ist otterpi gesund?“

Es sammelt deshalb ausschließlich Informationen, die für den aktuellen
Betriebszustand relevant sind.

Es gibt keine permanente Datenbank und keine historische Messwertspeicherung.

## HTTP-Verhalten

Das CGI liefert:

Content-Type: text/html; charset=UTF-8

und:

Cache-Control: no-store

Jeder Seitenaufruf erzeugt damit eine neue Messung.

Der angezeigte Zeitpunkt ist der Zeitpunkt der CGI-Ausführung.

## Erhobene Systemdaten

### Allgemein

- Hostname
- Datum/Uhrzeit
- Uptime
- letzter Boot
- Betriebssystem
- Kernel
- Hardwaremodell
- CPU-Kerne
- RAM-Größe

### CPU

- Temperatur
- Load Average 1 Minute
- Load Average 5 Minuten
- Load Average 15 Minuten
- aktuelle Frequenz
- maximale Frequenz
- Anzahl Prozesse

### RAM

- Gesamtspeicher
- verfügbarer Speicher
- genutzter Speicher
- prozentuale Auslastung

### Swap

- Swap-Gesamtgröße
- Swap-Nutzung
- Swap-Verfügbarkeit
- Swap-Prozent
- Swap-Gerät
- Swap-Typ
- Swap-Status

zram wird erkannt und entsprechend angezeigt.

### Speicher

Über `df`:

- Größe
- Nutzung
- verfügbarer Speicher
- prozentuale Belegung

Über `df -i`:

- Inodes gesamt
- Inodes genutzt
- Inodes frei
- prozentuale Belegung

Über `findmnt`:

- Root-Gerät
- Dateisystem
- Mountoptionen
- rw/ro-Zustand

Über `lsblk` und sysfs:

- physisches Elterngerät
- Modell bzw. Gerätebezeichnung
- Gerätetyp
- Herstellungsdatum, sofern vorhanden

## Hardwareintegrität

Auf Raspberry Pi wird `vcgencmd get_throttled` ausgewertet.

Geprüft werden:

- Unterspannung
- Frequenzbegrenzung
- Drosselung
- Temperatur-Limit

Dabei wird zwischen aktuellen Problemen und Problemen unterschieden,
die seit dem letzten Boot aufgetreten sind.

Beispiel:

OK

bedeutet:

Kein entsprechendes Ereignis erkannt.

seit Start aufgetreten

bedeutet:

Das Ereignis ist nicht aktuell aktiv, wurde aber seit dem Boot erkannt.

aktuell aktiv

bedeutet:

Das entsprechende Hardwareproblem besteht momentan.

## Statusberechnung

Das Dashboard verwendet drei Hauptzustände:

- ok
- warn
- critical

`unknown` wird grundsätzlich mindestens als Warnung behandelt.

Der Gesamtstatus wird aus den Einzelbefunden berechnet.

Priorität:

critical
→ Gesamtstatus kritisch

sonst warn/unknown
→ Gesamtstatus Warnung

sonst
→ Gesamtstatus OK

## Schwellwerte

### Temperatur

Unter 65 °C:

OK

65–79 °C:

Warnung

ab 80 °C:

kritisch

### RAM

unter 70 %:

OK

70–85 %:

Warnung

über 85 %:

kritisch

### Root-Dateisystem

rw:

OK

ro:

kritisch

unbekannt:

Warnung

### Speicher

unter 75 %:

OK

75–90 %:

Warnung

über 90 %:

kritisch

### Inodes

unter 80 %:

OK

80–90 %:

Warnung

über 90 %:

kritisch

### Swap

unter 50 %:

OK

50–80 %:

Warnung

über 80 %:

kritisch

Ist kein Swap aktiv, wird dies aktuell als Warnung bewertet.

Diese Entscheidung kann bei der späteren Überarbeitung geändert werden,
falls ein bewusst swap-loser Betrieb als normaler Zustand definiert wird.

## Netzwerk

Aktuell werden ermittelt:

- IPv4
- Gateway
- globale IPv6-Adresse
- MAC-Adresse von eth0
- Zustand eth0
- Zustand wlan0

Die Zustände der Interfaces sind:

- verbunden
- nicht verbunden
- blockiert
- deaktiviert
- nicht vorhanden

Eine echte Erreichbarkeitsprüfung findet in v3.3 noch nicht statt.

## Dienste

Über `systemctl is-active` werden aktuell sieben Dienste geprüft:

- nginx
- meshcentral
- pihole-FTL
- fcgiwrap
- ssh
- NetworkManager
- systemd-timesyncd

Status:

- active
- starting
- stopped
- failed
- unknown

Ein aktiver Dienst gilt als OK.

Ein fehlgeschlagener Dienst erzeugt einen kritischen Befund.

Andere nicht aktive bzw. unbekannte Zustände werden aktuell als Warnung
behandelt.

## Bewusste Grenzen von v3.3

v3.3 prüft noch nicht:

- ob ein Dienst tatsächlich über sein Protokoll erreichbar ist
- ob DNS tatsächlich antwortet
- ob das Gateway erreichbar ist
- ob das Internet erreichbar ist
- welche Ports tatsächlich offen sind
- ob unerwartete Ports existieren
- Journal-Fehler
- Dienst-Laufzeiten
- Restart-Zähler
- Zertifikatsablauf
- SSH-Sicherheit
- Paket-Updates
- Top-Prozesse
- Speicherhardware-Gesundheit
- SMART
- Raspberry-Pi-Firmware
- Bootloader-Version

Diese Punkte gehören zur geplanten Weiterentwicklung.

## Weiterentwicklung

Geplante nächste Stufe:

Dashboard v3.4

Schwerpunkt:

aktive Selbstdiagnose statt zusätzliche Datensammlung.

Priorität:

1. Netzwerk-Erreichbarkeit
2. Journal-Fehler
3. Dienst-Laufzeiten
4. Raspberry-Pi-Hardwareinformationen
5. Speicherhardware-Status

Danach:

6. CPU-Auslastung in Prozent
7. Top-Prozesse
8. Versionsinformationen
9. Netzwerkdetails

Spätere optionale Funktionen:

- Backupstatus
- kleine Historie
- Benachrichtigungen

## Architekturziel

Auch zukünftige Erweiterungen sollen ohne schweres Monitoring-System
auskommen.

Bevorzugt werden weiterhin:

- Shell
- sysfs
- procfs
- systemd
- Standard-Linux-Werkzeuge
- kleine einzelne Prüfskripte

Eine mögliche spätere Struktur wäre:

/opt/otterpi/
    checks/
        hardware.sh
        network.sh
        services.sh
        security.sh
        ports.sh
        certificates.sh

Das CGI würde die Prüfungen ausführen und die Ergebnisse darstellen.

Eine solche Aufteilung ist jedoch eine zukünftige Designentscheidung und
stellt noch keine Änderung des produktiven Systems dar.

## Produktiver Snapshot

Version:

otterpi Status Dashboard v3.3

Status:

produktiv

Charakter:

Appliance Health Monitor

Grundsatz:

Wenige aussagekräftige Werte statt eines vollständigen
Monitoring-Systems.
