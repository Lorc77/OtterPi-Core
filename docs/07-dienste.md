# OtterPi Core – Dienste und Ports

Stand: August 2026

## Aktive Dienste

### nginx

Zweck:

Zentraler Webserver und Reverse Proxy.

Aufgaben:

- HTTP
- HTTPS
- Service-Portal
- Status-Dashboard
- Reverse Proxy für MeshCentral
- zukünftige Virtual Hosts

Ports:

- TCP 80
- TCP 443

Öffentliche Erreichbarkeit:

- 80: öffentlich
- 443: öffentlich

## MeshCentral

Version:

MeshCentral v1.2.4

Zweck:

Fernwartung und Geräteverwaltung.

Betriebsmodus:

Hybrid LAN + WAN

Interne Ports:

- TCP 4430
- TCP 4433
- TCP 1024
- TCP 16989

Extern:

MeshCentral wird ausschließlich über Nginx veröffentlicht.

Backend:

https://127.0.0.1:4430

Hostname:

mesh.makki.route64.de

Zertifikatsquelle:

https://cert.makki.route64.de

## Pi-hole

Zweck:

DNS-Auflösung und DNS-Filterung im LAN.

Dienst:

pihole-FTL

Ports:

- TCP/UDP 53
- TCP 8080 für das Webinterface

Das Query Logging ist deaktiviert, um unnötige Schreiblast auf der
SD-Karte zu vermeiden.

## fcgiwrap

Zweck:

Ausführung der CGI-Anwendung des Status-Dashboards.

Das Dashboard wird als klassische Shell-CGI-Anwendung betrieben.

Produktive Dashboard-Datei:

/var/www/status/cgi-bin/status.cgi

## SSH

Zweck:

Administration des Raspberry Pi.

Port:

TCP 22

Der SSH-Dienst ist aktuell aktiv.

Die SSH-Konfiguration ist noch nicht vollständig gehärtet und soll zu
einem späteren Zeitpunkt überprüft werden.

Aktueller Stand:

- PermitRootLogin without-password
- PasswordAuthentication yes
- PubkeyAuthentication yes
- MaxAuthTries 6

SSH ist nicht öffentlich über das Internet erreichbar.

## NetworkManager

Zweck:

Verwaltung der Netzwerkverbindungen.

Dienst:

NetworkManager

## systemd-timesyncd

Zweck:

Zeitsynchronisation.

Dienst:

systemd-timesyncd

## Zertifikatsmonitor

Dienst:

meshcentral-cert-check.service

Timer:

meshcentral-cert-check.timer

Intervall:

ca. 10 Minuten

Aufgabe:

- CDN-Zertifikat prüfen
- MeshCentral-Zertifikat vergleichen
- bei Mismatch MeshCentral neu starten
- Ergebnis kontrollieren

Der Service ist als Type=oneshot ausgeführt.

Nach einem erfolgreichen Lauf ist der Service:

inactive (dead)

Das ist erwartetes Verhalten.

Der Timer bleibt:

active (waiting)

## rpcbind

Installiert:

rpcbind 1.2.7-1

Port:

TCP/UDP 111

Aktueller Zustand:

active

Aktuell ist außer dem Portmapper kein weiterer registrierter RPC-Dienst
bekannt.

Eine spätere Prüfung und gegebenenfalls Deaktivierung ist vorgesehen.

## Öffentliche Ports

Aktuell öffentlich:

- TCP 80 – nginx
- TCP 443 – nginx

## Nicht öffentlich erreichbare Ports

Unter anderem:

- TCP 22 – SSH
- TCP 53 – Pi-hole DNS
- TCP 1024 – MeshCentral Redirect
- TCP 4430 – MeshCentral
- TCP 4433 – Intel AMT

Die öffentliche Angriffsfläche soll damit bewusst klein bleiben.

## Grundsatz

Neue Dienste und Ports werden nicht automatisch als Bestandteil der
öffentlichen Infrastruktur betrachtet.

Vor jeder Veröffentlichung muss geprüft werden:

- benötigt der Dienst externe Erreichbarkeit?
- kann er hinter Nginx betrieben werden?
- kann der Port intern bleiben?
- entsteht dadurch unnötige Angriffsfläche?
