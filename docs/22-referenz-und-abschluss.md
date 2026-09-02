# OtterPi – Referenz und Abschluss

**Projekt:** Makki Heimserver / OtterPi  
**Dokument:** Gesamtübersicht und Referenz  
**Stand:** August 2026  
**Produktionsstand:** Version 1.0 / Dashboard v3.3

---

## 1. Zweck dieses Dokuments

Dieses Dokument ist der abschließende Referenzpunkt innerhalb der OtterPi-Dokumentation.

Es beschreibt:

- den dokumentierten Gesamtstand
- die wichtigsten Komponenten
- die vorhandenen Dokumente
- die produktiven Pfade
- die wesentlichen Abhängigkeiten
- die geplante Weiterentwicklung

Die Datei soll insbesondere als Einstieg dienen, wenn die Arbeit am Projekt nach längerer Pause oder in einem neuen Chat wieder aufgenommen wird.

---

## 2. Projektname

```text
OtterPi
```

Der OtterPi ist der Raspberry-Pi-basierte Heimserver des Makki-Projekts.

Er stellt mehrere klar getrennte Funktionen bereit:

```text
Internet / LAN
      |
      v
     Nginx
      |
      +---- Service-Portal
      |
      +---- Status Dashboard
      |
      +---- MeshCentral
      |
      +---- weitere Webdienste
```

Pi-hole arbeitet zusätzlich als lokaler DNS-Dienst.

---

## 3. Projektphilosophie

Der OtterPi ist bewusst keine möglichst große Serverplattform.

Grundprinzipien:

- möglichst wenig Komplexität
- möglichst wenige Dienste
- klare Zuständigkeiten
- einfache Wartbarkeit
- geringe Schreiblast
- keine unnötigen Datenbanken
- statische Weboberflächen bevorzugen
- automatische Wiederherstellung dort, wo sie sinnvoll ist
- gute Dokumentation
- nachvollziehbare Änderungen

Das System soll eher eine kleine Appliance als ein allgemeines Homelab sein.

---

## 4. Hardware

System:

```text
Raspberry Pi 4 Model B Rev 1.5
```

CPU:

```text
4 Kerne
```

RAM:

```text
1 GB
```

Speicher:

```text
SD-Karte
58 GB
```

Dateisystem:

```text
ext4
```

Mount-Optimierung:

```text
noatime
```

Hostname:

```text
otterpi
```

---

## 5. Netzwerk

LAN:

```text
eth0
IPv4: 192.168.178.100/24
Gateway: 192.168.178.1
```

WLAN:

```text
wlan0
```

WLAN ist im dokumentierten Zustand nicht aktiv.

IPv6 ist grundsätzlich aktiviert.

Der Raspberry Pi befindet sich hinter einer Fritz!Box.

---

## 6. Öffentliche Architektur

Öffentlich erreichbar sind grundsätzlich:

```text
TCP 80
TCP 443
```

Die öffentlichen Webzugriffe werden über Nginx verarbeitet.

MeshCentral selbst wird nicht direkt über seine internen Ports veröffentlicht.

Interne MeshCentral-Ports:

```text
4430
4433
1024
```

Die genaue öffentliche Erreichbarkeit wird durch die vorgeschaltete Netzwerk-/Routerkonfiguration bestimmt.

---

## 7. MeshCentral

Version:

```text
MeshCentral v1.2.4
```

Installationspfad:

```text
/opt/meshcentral/
```

Konfiguration:

```text
/opt/meshcentral/meshcentral-data/config.json
```

Betriebsmodus:

```text
Hybrid (LAN + WAN)
```

Interner Backend-Port:

```text
4430
```

Intel AMT:

```text
4433
```

HTTP Redirect:

```text
1024
```

Öffentliche Domain:

```text
mesh.makki.route64.de
```

---

## 8. MeshCentral-Zertifikatskonzept

MeshCentral verwendet:

```text
certUrl=https://cert.makki.route64.de
```

Der Zertifikats-Endpunkt stellt das Zertifikat bereit, das auch am CDN-Frontend verwendet wird.

Damit soll verhindert werden, dass CDN und MeshCentral unterschiedliche Zertifikate verwenden.

Der Zertifikatsmonitor überprüft regelmäßig:

```text
CDN-Zertifikat
        =
MeshCentral-Zertifikat
```

Bei einem Unterschied wird MeshCentral automatisch neu gestartet.

---

## 9. Zertifikatsmonitor

Script:

```text
/usr/local/sbin/check-mesh-cert.sh
```

Version:

```text
2.0
```

Systemd:

```text
/etc/systemd/system/meshcentral-cert-check.service
/etc/systemd/system/meshcentral-cert-check.timer
```

Statusspeicher:

```text
/var/lib/meshcentral-cert-check/
```

Der Timer läuft ungefähr alle zehn Minuten.

Der Fehlerfall wurde mit:

```sh
sudo /usr/local/sbin/check-mesh-cert.sh --simulate-mismatch
```

erfolgreich getestet.

---

## 10. MeshCentral AutoBackup

Backupziel:

```text
/opt/meshcentral/meshcentral-backups/
```

Intervall:

```text
24 Stunden
```

Aufbewahrung:

```text
10 Tage
```

Backups:

```text
verschlüsselt
passwortgeschützt
```

Ein Backup wurde erfolgreich mit 7-Zip getestet.

---

## 11. Pi-hole

Installationspfad:

```text
/opt/pihole
```

Dienst:

```text
pihole-FTL
```

DNS:

```text
Port 53
```

Webinterface:

```text
Port 8080
```

Query Logging wurde zur Reduzierung der Schreiblast deaktiviert.

Aktueller DNS-Upstream:

* `9.9.9.9`
* `149.112.112.112`
* `2620:fe::fe`
* `2620:fe::9`

Die verwendeten Quad9-Upstreams gehören zur gefilterten Quad9-Konfiguration. ECS wird nicht verwendet; die DNSSEC-Validierung erfolgt nicht lokal durch Pi-hole.

Pi-hole-Konfiguration:

* DNSSEC: deaktiviert
* EDNS0 ECS: deaktiviert
* Query Logging: deaktiviert
* Blocking: aktiviert

Aktuelle Blocklisten:

* StevenBlack Hosts
* HaGeZi Multi Pro
* HaGeZi Threat Intelligence

Gravity:

* ca. 2,48 Millionen Einträge

Die produktive DNS-Kette wurde erfolgreich getestet:

`LAN-Client → Pi-hole → Quad9`

Dabei wurden externe DNS-Auflösung, lokale `pi.hole`-Auflösung, IPv4/IPv6 sowie Pi-hole-Blocking verifiziert.

Unbound ist aktuell nicht installiert.

Die Einführung eines lokalen rekursiven Resolvers wurde bewusst zurückgestellt, da die zusätzliche Komplexität aktuell keinen ausreichenden Mehrwert gegenüber dem bestehenden Quad9-Upstream bietet.

---

## 12. Nginx

Nginx ist der zentrale Webserver und Reverse Proxy.

Er übernimmt insbesondere:

- öffentliche HTTP-/HTTPS-Anfragen
- Reverse Proxy zu MeshCentral
- Webauslieferung des Service-Portals
- Webauslieferung des Status Dashboards
- weitere Virtual Hosts

Bei Änderungen gilt:

```sh
sudo nginx -t
```

vor dem Reload.

---

## 13. Service-Portal

Pfad:

```text
/var/www/makki/
```

Produktive Startseite:

```text
/var/www/makki/index.html
```

Backupverzeichnis:

```text
/var/www/makki/backups/
```

Aktueller Stand:

```text
Makki Services v1.0
```

Das Portal trennt externe Dienste von lokalen Systemdiensten.

---

## 14. Status Dashboard

Produktiver Pfad:

```text
/var/www/status/cgi-bin/status.cgi
```

Aktuelle Version:

```text
otterpi Status Dashboard v3.3
```

Das Dashboard ist eine stateless CGI-Anwendung.

Es speichert keine historische Monitoring-Datenbank.

Die Seite ermittelt den Zustand bei jedem Aufruf direkt aus dem laufenden System.

---

## 15. Dashboard-Funktionen

Aktuell werden unter anderem angezeigt:

### System

- Hostname
- Hardware
- Betriebssystem
- Kernel
- letzter Start
- Uptime

### Hardware

- CPU-Temperatur
- Unterspannung
- Frequenzbegrenzung
- Drosselung
- Temperatur-Limit

### Ressourcen

- CPU Load
- CPU-Frequenz
- RAM
- zram-Swap
- SD-Karte
- Inodes
- Prozessanzahl

### Netzwerk

- IPv4
- Gateway
- IPv6
- MAC-Adresse
- eth0
- wlan0

### Dienste

- nginx
- MeshCentral
- Pi-hole FTL
- fcgiwrap
- ssh
- NetworkManager
- systemd-timesyncd

---

## 16. Dashboard-Entwicklungsrichtung

Die nächste geplante Ausbaustufe soll nicht einfach weitere Messwerte hinzufügen.

Ziel ist:

```text
Statusanzeige
        ↓
aktive Diagnose
        ↓
verständliche Fehlererklärung
```

Geplante Themen:

- Netzwerk-Erreichbarkeit
- Gateway-Prüfung
- DNS-Prüfung
- Dienst-Erreichbarkeit
- erwartete Ports
- Zertifikatsprüfung
- Journalfehler
- Dienst-Laufzeiten
- Raspberry-Pi-Hardwareinformationen
- Speicherhardware

Dabei soll der Appliance-Charakter erhalten bleiben.

---

## 17. Bewusst keine Monitoring-Plattform

Nicht vorgesehen sind derzeit:

```text
InfluxDB
Grafana
Prometheus
Kubernetes
große Containerlandschaften
dauerhafte Metrikhistorien
```

Der OtterPi soll keine eigene Monitoring-Infrastruktur betreiben müssen, nur um seinen eigenen Zustand anzuzeigen.

---

## 18. Schreiblast

Zur Schonung der SD-Karte wurden verschiedene Maßnahmen umgesetzt:

```text
ext4
noatime
kleines Journald
Logrotate
fstrim
Pi-hole Query Logging deaktiviert
DynDNS-Ausgabe verworfen
keine historische Dashboard-Datenbank
```

Der Grundsatz lautet:

**Daten sollen nur dauerhaft gespeichert werden, wenn sie tatsächlich benötigt werden.**

---

## 19. DynDNS

Die DynDNS-Aktualisierung erfolgt regelmäßig über:

```text
ipv64.net
```

Die Ausgabe wird verworfen:

```text
>/dev/null 2>&1
```

Dadurch entstehen keine unnötigen Logdateien durch den Cronjob.

Der eigentliche Schlüssel beziehungsweise das Secret gehört nicht in diese Dokumentation.

---

## 20. Firewall

Im dokumentierten Stand ist keine lokale `ufw`-Firewall installiert.

Bewertung:

```text
bewusst
```

Die Fritz!Box übernimmt derzeit die Edge-Firewall-Funktion.

Eine spätere lokale Firewall kann eingeführt werden, wenn sich durch zusätzliche Dienste ein konkreter Bedarf ergibt.

---

## 21. SSH

SSH läuft auf:

```text
TCP 22
```

Der dokumentierte Zustand ist noch nicht vollständig gehärtet.

Aktuell:

```text
PermitRootLogin without-password
PasswordAuthentication yes
PubkeyAuthentication yes
MaxAuthTries 6
```

Eine spätere Härtung ist vorgesehen.

---

## 22. rpcbind

Installiert:

```text
rpcbind 1.2.7-1
```

Port:

```text
111 TCP/UDP
```

Zum dokumentierten Stand war außer dem Portmapper kein weiterer RPC-Dienst registriert.

Vor einer Deaktivierung soll geprüft werden, ob zukünftig ein Dienst davon abhängig ist.

---

## 23. Systemd und Autostart

Wichtige Dienste werden automatisch gestartet.

Besonders relevant:

```text
nginx
meshcentral
pihole-FTL
fcgiwrap
NetworkManager
systemd-timesyncd
meshcentral-cert-check.timer
```

Der automatische Start nach einem Raspberry-Pi-Reboot wurde erfolgreich getestet.

---

## 24. Wiederanlauf

Der produktive Wiederanlauf wurde praktisch getestet.

Nach einem Neustart:

```text
System startet
      ↓
Dienste starten
      ↓
MeshCentral erreichbar
      ↓
Agent zunächst offline
      ↓
Agent verbindet sich automatisch
      ↓
Normalbetrieb
```

Auch der Zertifikatsmonitor startet automatisch wieder.

---

## 25. Dokumentationsprinzip

Die Repository-Dokumentation soll nicht nur erklären, wie das System geplant ist.

Sie soll vor allem dokumentieren:

```text
was tatsächlich installiert ist
was tatsächlich läuft
wo Dateien liegen
welche Ports verwendet werden
welche Tests erfolgreich waren
welche Entscheidungen bewusst getroffen wurden
```

Planungen und tatsächlicher Produktionsstand sollen klar voneinander getrennt bleiben.

---

## 26. Änderungsprinzip

Größere Änderungen sollen möglichst:

1. dokumentiert
2. gesichert
3. einzeln durchgeführt
4. getestet
5. anschließend erneut dokumentiert

werden.

Ein funktionierender Produktionsstand soll nicht unnötig verändert werden.

---

## 27. Wiederherstellung

Die wichtigsten Wiederherstellungspunkte sind:

```text
MeshCentral AutoBackup
config.json Backups
Portal Backups
dokumentierte Nginx-Konfiguration
dokumentierte systemd-Konfiguration
Git-Repository
```

Das Repository selbst ist dabei eine Dokumentations- und Versionsquelle.

Es ersetzt kein externes Datenbackup.

---

## 28. Git-Repository

Das Repository ist als:

```text
OtterPi-Core
```

gedacht.

Es soll den bekannten Systemstand reproduzierbar dokumentieren.

Der aktuelle Aufbau umfasst:

```text
OtterPi-Core/
├── README.md
└── docs/
    ├── 01-...
    ├── 02-...
    ├── 03-...
    ├── ...
    ├── 19-...
    ├── 20-backup-und-recovery.md
    └── 21-referenz-und-abschluss.md
```

Die exakten Dateinamen der ersten Dokumente ergeben sich aus dem tatsächlich verwendeten Repository-Stand.

---

## 29. Wichtigster Wiedereinstiegspunkt

Für eine spätere Weiterarbeit genügt grundsätzlich folgende Kurzbeschreibung:

```text
Wir arbeiten am OtterPi / Makki Heimserver.

Der Raspberry Pi otterpi ist produktiv.
MeshCentral v1.2.4 läuft hinter Nginx.
Das MeshCentral-Zertifikat wird über certUrl von
cert.makki.route64.de bezogen.

Ein systemd-Zertifikatsmonitor prüft regelmäßig,
ob CDN- und MeshCentral-Zertifikat identisch sind,
und startet MeshCentral bei einem Wechsel automatisch neu.

Das Service-Portal ist produktiv.
Das Status Dashboard v3.3 ist produktiv.

Das Dashboard arbeitet stateless und ohne Datenbank.
Die nächste geplante Entwicklung ist eine schlanke aktive
Selbstdiagnose mit Netzwerk-, Dienst-, Journal-,
Zertifikats- und Hardwarechecks.

Der Appliance-Charakter soll erhalten bleiben:
wenig Dienste, wenig Schreiblast, keine unnötige
Monitoring-Infrastruktur.
```

---

## 30. Aktueller Gesamtstatus

Der dokumentierte Produktionsstand ist:

```text
Raspberry Pi              OK
Betriebssystem            OK
Netzwerk                  OK
Nginx                     OK
MeshCentral               OK
MeshCentral Agent         OK
Pi-hole                   OK
Service-Portal            OK
Status Dashboard          OK
certUrl                   OK
Zertifikatsmonitor        OK
systemd Timer             OK
AutoBackup                OK
Reboot-Test               OK
Recovery-Test             OK
```

---

## 31. Abschluss

Der OtterPi ist aktuell kein unfertiger Versuchsaufbau mehr.

Er ist eine kleine produktive Infrastruktur mit:

- dokumentierter Architektur
- funktionierendem Autostart
- funktionierender Remoteverwaltung
- automatischer Zertifikatsüberwachung
- Backupmechanismus
- Service-Portal
- Status Dashboard
- definiertem Recovery-Weg

Die zukünftige Entwicklung soll daher kontrolliert erfolgen.

Der nächste sinnvolle Schritt ist nicht möglichst viel neue Software, sondern die Verbesserung der Diagnosefähigkeit des bestehenden Systems.

---

## 32. Leitgedanke

> **Der OtterPi soll Probleme erkennen und verständlich erklären – nicht selbst zum Problem werden.**

🦦
