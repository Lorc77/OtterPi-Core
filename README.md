# 🦦 OtterPi-Core

Dokumentations- und Referenzrepository für den privaten Heimserver **otterpi**.

Stand: September 2026

## Zweck

Dieses Repository dokumentiert den vollständigen technischen Stand des OtterPi-Heimservers.

Es dient insbesondere als:

- technischer Snapshot
- Wiederanlaufpunkt für zukünftige Arbeiten
- Dokumentation der aktuellen Architektur
- Referenz für Konfiguration und Betriebszustand
- Ablage des produktiven Status-Dashboards
- Grundlage für zukünftige Ausbaustufen

Das Repository ist zunächst als **Dokumentationsquelle** gedacht.

Es beschreibt den bestehenden produktiven Zustand und enthält keine Aufforderung, bestehende Konfigurationen ohne vorherige Prüfung zu verändern.

---

# Aktueller Gesamtstand

Der OtterPi-Heimserver ist aktuell produktiv, stabil und vollständig getestet.

Hardware:

- Raspberry Pi 4 Model B Rev 1.5
- 4 CPU-Kerne
- 1 GB RAM
- 58 GB SD-Karte
- arm64

Hostname:

`otterpi`

---

# Aktive Kernkomponenten

Der Server betreibt unter anderem:

- nginx
- MeshCentral
- Pi-hole FTL mit lokalem DNS- und Filterdienst
- fcgiwrap
- SSH
- NetworkManager
- systemd-timesyncd

Zusätzlich existiert ein statisches Service-Portal sowie ein CGI-basiertes Status-Dashboard.

---

# Webstruktur

## Service-Portal

Produktiver Pfad:

`/var/www/makki/`

Produktive Datei:

`/var/www/makki/index.html`

Das Portal dient als zentrale Einstiegseite für die verschiedenen Heimserver-Dienste.

---

## Status-Dashboard

Produktiver Pfad:

`/var/www/status/cgi-bin/status.cgi`

Aktuelle Version:

**otterpi Status Dashboard v3.3**

Das Dashboard ist bewusst als leichtgewichtiger Appliance Health Monitor aufgebaut.

Es verwendet:

- Shell/CGI
- HTML
- CSS
- lokale Linux-Systeminformationen

Es verwendet bewusst keine Datenbank und kein dauerhaft laufendes Monitoring-System.

---

# MeshCentral

Version:

`1.2.4`

Betriebsmodus:

Hybrid LAN + WAN

Interner Backend-Port:

`4430`

Intel AMT:

`4433`

Extern:

nginx übernimmt HTTPS auf Port 443.

MeshCentral selbst ist nicht direkt öffentlich erreichbar.

---

# Zertifikatsmanagement

Das produktive MeshCentral-Zertifikat wird über einen definierten Zertifikats-Endpunkt bezogen:

`https://cert.makki.route64.de`

MeshCentral verwendet dafür `certUrl`.

Ein eigener systemd-basierter Zertifikatsmonitor vergleicht regelmäßig:

- externes CDN-Zertifikat
- von MeshCentral geladenes Zertifikat

Bei einem Zertifikatswechsel wird MeshCentral automatisch neu gestartet.

Der Mechanismus wurde erfolgreich getestet.

---

# Backup

MeshCentral AutoBackup ist aktiviert.

Backupintervall:

`24 Stunden`

Aufbewahrung:

`10 Tage`

Backupziel:

`/opt/meshcentral/meshcentral-backups/`

Die Backups sind passwortgeschützt und wurden erfolgreich auf Integrität geprüft.

---

# Speicheroptimierung

Der Server ist auf geringe Schreiblast ausgelegt.

Aktiv sind unter anderem:

- ext4 mit `noatime`
- deaktiviertes Pi-hole Query Logging
- kleines Journald
- Logrotate
- fstrim
- DynDNS ohne lokale Logdatei

Grundprinzip:

So wenig dauerhafte Schreiblast wie sinnvoll.

---

# Netzwerk

LAN:

`eth0`

IPv4:

`192.168.178.100/24`

Gateway:

`192.168.178.1`

WLAN:

`wlan0`

Derzeit nicht aktiv.

IPv6 ist aktiviert.

---

# DNS

Pi-hole ist der zentrale DNS-Dienst für das LAN.

Die Clients verwenden Pi-hole direkt als DNS-Server. Die DNS-Auflösung wurde praktisch über IPv4 und IPv6 getestet.

Pi-hole verwendet derzeit Quad9 als externe Upstream-Resolver:

* 9.9.9.9
* 149.112.112.112
* 2620:fe::fe
* 2620:fe::9

Verwendet wird die Quad9-Konfiguration mit Filterung und DNSSEC, ohne ECS.

Pi-hole Query Logging ist deaktiviert, um unnötige dauerhafte Schreiblast auf der SD-Karte zu vermeiden.

Unbound ist derzeit bewusst nicht installiert. Der zusätzliche rekursive Resolver würde zusätzliche Komplexität und einen weiteren permanenten Dienst einführen, ohne für den aktuellen Einsatzzweck einen ausreichenden Mehrwert gegenüber Quad9 zu liefern.

Diese Entscheidung kann bei zukünftigen Anforderungen erneut bewertet werden.

---

# Öffentliche Erreichbarkeit

Öffentlich vorgesehen sind:

- TCP 80
- TCP 443

MeshCentral läuft ausschließlich hinter nginx.

Interne Dienste und Verwaltungsports werden nicht direkt öffentlich veröffentlicht.

---

# Projektphilosophie

OtterPi ist bewusst keine allgemeine Server-Spielwiese.

Ziel ist eine:

- kleine
- übersichtliche
- wartbare
- ressourcenschonende
- dokumentierbare

private Infrastruktur.

Das Dashboard soll nicht zu einem vollständigen Monitoring-System ausgebaut werden.

Der bevorzugte Ansatz lautet:

> Wenige aussagekräftige Werte statt möglichst vieler Messwerte.

---

# Nächster geplanter Entwicklungsschritt

Das Status-Dashboard soll schrittweise von einer reinen Zustandsanzeige zu einem **Selbstdiagnose-System** weiterentwickelt werden.

Nicht:

> „Ich sammle historische Daten.“

Sondern:

> „Ich erkenne aktuelle Probleme und erkläre sie.“

Geplante nächste Ausbaustufe:

**Status Dashboard v3.4**

Priorität:

1. Dienst-Erreichbarkeit
2. Netzwerkchecks
3. Prüfung erwarteter Ports
4. Zertifikatsprüfung
5. Sicherheitschecks

Spätere Komfortfunktionen können unter anderem sein:

- CPU-Auslastung in Prozent
- Top-Prozesse
- Versionsinformationen
- Dienst-Laufzeiten
- Raspberry-Pi-Hardwareinformationen
- Speicherhardwarezustand

Bewusst nicht vorgesehen sind derzeit:

- Datenbank
- InfluxDB
- Grafana
- Kubernetes
- große Containerlandschaft
- permanente historische Datenspeicherung

---

# Wichtiger Grundsatz

Vor jeder größeren Änderung wird ein Snapshot des funktionierenden Zustands erstellt.

Damit bleibt jederzeit ein klarer Rückkehrpunkt erhalten.

Der Stand dieses Repositorys beschreibt den dokumentierten Produktionszustand des OtterPi-Systems und soll bei zukünftigen Arbeiten als Referenz dienen.
