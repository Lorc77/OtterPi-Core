# OtterPi Core – Webstruktur

Stand: August 2026

## Übersicht

Die Weboberfläche des Heimservers besteht aus mehreren logisch getrennten
Bereichen.

Grundprinzip:

Portal
→ Auswahl der Dienste

Status
→ Diagnose des Servers

Dienste
→ eigentliche Anwendungen

## Service-Portal

Produktiver Pfad:

/var/www/makki/

Produktive Datei:

/var/www/makki/index.html

Backups:

/var/www/makki/backups/

Aktueller Stand:

Makki Services v1.0

Das Portal dient als zentraler Einstiegspunkt für die verschiedenen
Dienste des Heimservers.

## Portal-Design

Hintergrund:

otter2.png

Favicon:

favicon.svg

Bereiche:

- Makki Services
- Remote Access
- Monitoring & IoT
- System Services
- Projects

## Eingebundene Dienste

### MeshCentral

Adresse:

https://mesh.makki.route64.de

Anzeige:

MeshCentral

Kategorie:

Remote Access

### ZOOLOGY-Observer

Adresse:

https://thingspeak.mathworks.com/channels/2068639

Anzeige:

ZOOLOGY-Observer

Kennzeichnung:

extern

Kategorie:

Monitoring & IoT

### WeatherHub-Observer

Adresse:

https://www.wh-observer.de/Account/LogOn

Anzeige:

WeatherHub-Observer

Kennzeichnung:

extern

Kategorie:

Monitoring & IoT

### otterpi Status

Adresse:

https://status.makki.route64.de/

Anzeige:

🦦 otterpi System Status

Kennzeichnung:

LAN only

### Pi-hole

Adresse:

http://pihole.makki.route64.de

Anzeige:

Pi-hole

Kennzeichnung:

LAN only

## Status-Dashboard

Produktiver Pfad:

/var/www/status/cgi-bin/

Produktive Datei:

/var/www/status/cgi-bin/status.cgi

Aktuelle Version:

otterpi · Status Dashboard v3.3

Entwicklungsdatei:

~/status.cgi-dashboard-v3.3-dev

## Dashboard-Prinzip

Das Dashboard ist eine klassische Shell-CGI-Anwendung.

Es erzeugt bei jedem Aufruf eine vollständige HTML-Seite.

HTTP-Header:

Content-Type: text/html; charset=UTF-8

Cache-Control:

no-store

Damit wird keine zwischengespeicherte Statusseite als aktueller
Systemzustand angezeigt.

## Aktuelle Dashboard-Bereiche

### Systemstatus

Enthält:

- Gesamtstatus
- Hardwareintegrität
- Unterspannung
- Frequenzbegrenzung
- Drosselung
- Temperatur-Limit
- Root-Dateisystem
- Dienststatus
- Warnungen
- Fehler

### System

Enthält:

- Hostname
- Hardware
- CPU-Kerne
- RAM
- Betriebssystem
- Kernel
- letzter Start
- Uptime

### Netzwerk

Enthält:

- IPv4
- Gateway
- IPv6
- MAC-Adresse
- eth0-Status
- wlan0-Status

### Dienste

Überwacht aktuell:

- nginx
- MeshCentral
- pihole-FTL
- fcgiwrap
- ssh
- NetworkManager
- systemd-timesyncd

### Leistung

Enthält:

- CPU-Temperatur
- Load Average 1/5/15 Minuten
- aktuelle CPU-Frequenz
- maximale CPU-Frequenz
- Prozessanzahl

### RAM

Enthält:

- RAM gesamt
- RAM genutzt
- RAM verfügbar
- RAM-Auslastung
- zram-Swap
- Swap-Auslastung
- Swap-Gerät
- Swap-Typ
- Swap-Status

### Speicher

Enthält:

- Root-Dateisystem
- Dateisystemtyp
- Mountstatus
- Speichergröße
- belegter Speicher
- freier Speicher
- Speicherbelegung
- Inode-Belegung
- physisches Gerät
- Modell
- Typ
- Herstellungsdatum, sofern verfügbar

## Statusfarben

Grün:

OK bzw. normal

Gelb:

Warnung bzw. nicht kritischer auffälliger Zustand

Rot:

kritischer Zustand bzw. Fehler

Grau:

nicht aktiv, deaktiviert oder nicht verfügbar

## Design

Das Dashboard verwendet:

- dunklen, halbtransparenten Hintergrund
- otter2.png als Hintergrund
- Kartenlayout
- responsive Darstellung
- Statuslampen
- Fortschrittsbalken
- mobile Darstellung

Der visuelle Charakter soll bewusst eher einer kleinen Appliance als einem
Enterprise-Monitoring-System entsprechen.

## Ziel der nächsten Version

Die nächste Entwicklungsstufe soll nicht primär mehr Messwerte anzeigen.

Stattdessen soll das Dashboard aktiv prüfen:

- funktioniert das Netzwerk?
- funktioniert DNS?
- sind erwartete Dienste erreichbar?
- sind unerwartete Ports offen?
- gibt es aktuelle Journal-Fehler?
- sind Zertifikate gültig?
- gibt es erkennbare Sicherheitsprobleme?

Damit entwickelt sich das Dashboard vom reinen Statusanzeiger zu einem
Appliance Health Monitor.
