# OtterPi Core – Architektur

Stand: August 2026

## Zweck

OtterPi ist eine bewusst klein gehaltene private Server-Infrastruktur auf
Basis eines Raspberry Pi 4 Model B.

Der Server stellt wenige, klar getrennte Dienste bereit und verfolgt
insbesondere folgende Ziele:

- geringe Komplexität
- einfache Wartbarkeit
- geringe Schreiblast auf der SD-Karte
- möglichst wenige zusätzliche Hintergrunddienste
- nachvollziehbare Konfiguration
- automatische Wiederherstellung wichtiger Dienste
- lokale Diagnose ohne externes Monitoring-System

OtterPi ist keine klassische Monitoring-Plattform. Das Status-Dashboard
dient primär der aktuellen Zustands- und Selbstdiagnose.

## Hardware

- Raspberry Pi 4 Model B Rev 1.5
- 4 CPU-Kerne
- 1 GB RAM
- 58 GB SD-Karte
- Architektur: arm64

## Netzwerk

LAN:

- Interface: eth0
- IPv4: 192.168.178.100/24
- Gateway: 192.168.178.1
- globale IPv6-Konnektivität vorhanden
- ULA IPv6 vorhanden

WLAN:

- Interface wlan0 vorhanden
- aktuell nicht aktiv

## Netzwerkarchitektur

Der Raspberry Pi befindet sich hinter einer Fritz!Box.

Öffentlich erreichbar sind ausschließlich:

- TCP 80
- TCP 443

MeshCentral selbst wird nicht direkt aus dem Internet exponiert.

Der externe Zugriff erfolgt über:

Internet
→ CDN / Frontend
→ Nginx
→ MeshCentral

Im LAN existiert zusätzlich eine interne DNS-Auflösung für MeshCentral.
Dadurch können lokale Geräte die MeshCentral-Instanz direkt erreichen.

## DNS-Architektur

Pi-hole stellt den zentralen DNS-Dienst des LANs bereit.

Der aktuelle Datenfluss ist:

    LAN-Client
        |
        v
    Fritz!Box / LAN
        |
        v
    Pi-hole FTL
    192.168.178.100:53
        |
        v
    Quad9
    9.9.9.9
    149.112.112.112
    2620:fe::fe
    2620:fe::9

Pi-hole übernimmt:

* DNS-Anfragen der LAN-Clients
* DNS-Filterung
* lokalen DNS-Cache
* lokale DNS-Einträge

Quad9 übernimmt die externe rekursive DNS-Auflösung.

Die verwendeten Quad9-Upstreams gehören zur gefilterten Quad9-Konfiguration. ECS wird nicht verwendet; die DNSSEC-Validierung erfolgt nicht lokal durch Pi-hole.

Pi-hole verwendet aktuell:

* DNSSEC: deaktiviert
* EDNS0 ECS: deaktiviert
* Query Logging: deaktiviert

Die DNS-Funktion wurde praktisch getestet:

* externe Namensauflösung über Pi-hole funktioniert
* lokale Auflösung von `pi.hole` funktioniert
* IPv4- und IPv6-DNS-Anfragen funktionieren
* eine blockierte Testdomain wird durch Pi-hole geblockt

## DNS-Entscheidung September 2026

Der OtterPi verwendet Pi-hole als zentralen DNS-Dienst und Quad9 als
externen Upstream-Resolver.

Unbound wurde geprüft, aber zunächst bewusst nicht eingeführt.

Grund:

Der OtterPi soll eine kleine, übersichtliche und wartbare Appliance
bleiben. Ein lokaler rekursiver Resolver würde einen zusätzlichen
permanenten Dienst sowie zusätzliche Konfiguration und Wartungsaufwand
einführen. Der daraus entstehende Nutzen ist für den aktuellen
Einsatzzweck nicht groß genug.

Die Entscheidung ist bewusst reversibel und kann bei veränderten
Anforderungen erneut bewertet werden.

ECS wurde untersucht. Die verwendeten Quad9-Endpunkte arbeiten ohne
ECS; außerdem lieferten die getesteten Clients keine ECS-Informationen
an Pi-hole. Daher ist EDNS0 ECS in Pi-hole deaktiviert.

Der produktive Zustand wurde anschließend mit externen, lokalen und
geblockten DNS-Anfragen über IPv4 und IPv6 verifiziert.

## Webserver

Nginx übernimmt die Rolle des zentralen HTTP-/HTTPS-Einstiegspunkts.

Geplante und vorhandene Webbereiche:

- Service-Portal
- Status-Dashboard
- MeshCentral-Reverse-Proxy
- zukünftig statische Placeholder-/Willkommensseite

Die einzelnen Webanwendungen werden über getrennte Nginx-Virtual-Hosts
bzw. Locations voneinander getrennt.

## MeshCentral

MeshCentral läuft intern und wird über Nginx veröffentlicht.

Interne Ports:

- TCP 4430 – MeshCentral HTTP
- TCP 4433 – Intel AMT
- TCP 1024 – HTTP Redirect
- TCP 16989 – Agent-Kommunikation

Extern wird MeshCentral ausschließlich über HTTPS bereitgestellt.

## Zertifikatsarchitektur

MeshCentral verwendet:

certUrl=https://cert.makki.route64.de

Damit übernimmt MeshCentral das produktive Zertifikat vom definierten
Zertifikats-Endpunkt.

Ein separater systemd-Timer überwacht regelmäßig den Zertifikats-Hash.

Ablauf:

CDN-Zertifikat
→ Hash bilden
→ MeshCentral geladenen Zertifikats-Hash aus Journal lesen
→ vergleichen

Bei einem Unterschied:

1. Mismatch erkennen
2. MeshCentral neu starten
3. neues Zertifikat laden lassen
4. Hash erneut prüfen
5. Erfolg protokollieren

Dadurch ist kein manueller Eingriff bei einem normalen
CDN-Zertifikatswechsel erforderlich.

## Backup

MeshCentral besitzt ein eigenes AutoBackup.

Aktuell:

- Intervall: 24 Stunden
- Aufbewahrung: 10 Tage
- verschlüsselte ZIP-Archive
- Backupziel: /opt/meshcentral/meshcentral-backups/

Zusätzlich existieren manuelle Konfigurations-Backups.

## Schreiblast

OtterPi ist bewusst auf geringe Schreiblast ausgelegt.

Aktiv:

- ext4
- noatime
- reduziertes Journald
- Logrotate
- fstrim
- Pi-hole Query Logging deaktiviert
- DynDNS ohne Logausgabe
- keine permanente Monitoring-Datenbank

Bewusst nicht vorgesehen:

- InfluxDB
- Grafana
- Kubernetes
- umfangreiche Containerlandschaft
- permanente Messwert-Historien

## Diagnoseprinzip

Das Status-Dashboard soll nicht möglichst viele Daten sammeln.

Stattdessen soll es aktuelle Probleme erkennen und verständlich darstellen.

Prinzip:

Nicht:

„Wie sah der Server vor drei Tagen aus?“

Sondern:

„Ist der Server jetzt gesund und wenn nicht, warum?“

## Zukünftige Erweiterung

Die nächste sinnvolle Entwicklungsstufe des Dashboards ist eine aktive
Selbstdiagnose.

Priorität:

1. Netzwerk-Erreichbarkeit
2. Journal-Fehler
3. Dienst-Laufzeiten
4. Raspberry-Pi-Hardwareinformationen
5. Speicherhardware
6. CPU-Auslastung
7. Top-Prozesse
8. Versionsinformationen
9. Netzwerkdetails
10. optional Backupstatus
11. optional Historie
12. optional Benachrichtigungen
