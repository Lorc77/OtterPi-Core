# 🦦 OtterPi – Wiedereinstiegspunkt

Stand: August 2026

Dieses Dokument dient als kompakter Einstiegspunkt für zukünftige Arbeiten am OtterPi-Projekt.

---

# Projekt

**Makki Heimserver / OtterPi**

Hostname:

`otterpi`

Hardware:

Raspberry Pi 4 Model B Rev 1.5

Architektur:

`arm64`

RAM:

1 GB

Speicher:

58 GB SD-Karte

---

# Aktueller Entwicklungsstand

Der Server ist produktiv und stabil.

Die grundlegenden Funktionen wurden erfolgreich getestet.

Dazu gehören:

- automatischer MeshCentral-Start
- automatischer Agent-Reconnect
- nginx Reverse Proxy
- TLS
- Zertifikatsmonitor
- systemd-Timer
- Raspberry-Pi-Reboot
- Agent-Reboot
- Zertifikatswechsel-Simulation
- automatische Recovery

---

# Produktive Webkomponenten

## Service-Portal

Pfad:

`/var/www/makki/`

Produktive Datei:

`/var/www/makki/index.html`

Aktueller Stand:

`Makki Services v1.0`

---

## Status-Dashboard

Produktiver Pfad:

`/var/www/status/cgi-bin/status.cgi`

Aktuelle Version:

`otterpi Status Dashboard v3.3`

Das Dashboard ist CGI-basiert und arbeitet ohne Datenbank.

---

# Portal

Das Portal verwendet aktuell:

```text
otter2.png
favicon.svg
```

Bereiche:

```text
🦦 Makki Services

🌐 Remote Access

📡 Monitoring & IoT

🛡 System Services

🚧 Projects
```

---

# Portal-Dienste

## MeshCentral

```text
https://mesh.makki.route64.de
```

Anzeige:

```text
MeshCentral
```

---

## ZOOLOGY-Observer

```text
https://thingspeak.mathworks.com/channels/2068639
```

Anzeige:

```text
ZOOLOGY-Observer
(extern)
```

---

## WeatherHub-Observer

```text
https://www.wh-observer.de/Account/LogOn
```

Anzeige:

```text
WeatherHub-Observer
(extern)
```

---

## OtterPi Status

```text
http://status.makki.route64.de/
```

Anzeige:

```text
🦦 otterpi System Status
(LAN only)
```

---

## Pi-hole

```text
http://pihole.makki.route64.de
```

Anzeige:

```text
Pi-hole
(LAN only)
```

---

# MeshCentral

Version:

`1.2.4`

Installationspfad:

`/opt/meshcentral/`

Konfiguration:

`/opt/meshcentral/meshcentral-data/config.json`

Interner HTTP-Port:

`4430`

Intel AMT:

`4433`

HTTP Redirect:

`1024`

Öffentlich:

nginx auf Port 443

---

# Zertifikatskonzept

MeshCentral verwendet:

```text
certUrl=https://cert.makki.route64.de
```

Der Zertifikatsmonitor befindet sich unter:

```text
/usr/local/sbin/check-mesh-cert.sh
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

Prüfintervall:

ca. 10 Minuten

Zweck:

CDN-Zertifikat und MeshCentral-Zertifikat vergleichen und bei einem Wechsel automatisch MeshCentral neu starten.

---

# MeshCentral Backups

Backupverzeichnis:

```text
/opt/meshcentral/meshcentral-backups/
```

Intervall:

24 Stunden

Aufbewahrung:

10 Tage

Backups:

verschlüsselte ZIP-Dateien

---

# Pi-hole

Installationspfad:

`/opt/pihole`

Dienst:

`pihole-FTL`

DNS:

Port 53

Webinterface:

Port 8080

Query Logging:

deaktiviert

---

# Netzwerk

LAN:

`eth0`

IPv4:

`192.168.178.100/24`

Gateway:

`192.168.178.1`

IPv6:

global und ULA aktiv

WLAN:

`wlan0`, aktuell DOWN

---

# Öffentliche Ports

Aktuell öffentlich vorgesehen:

```text
TCP 80
TCP 443
```

MeshCentral wird ausschließlich über nginx öffentlich bereitgestellt.

Interne Ports:

```text
22
53
1024
4430
4433
8080
16989
```

Die genaue öffentliche Erreichbarkeit einzelner Ports muss bei zukünftigen Änderungen erneut geprüft werden.

---

# Sicherheit

Aktuell:

- keine lokale ufw-Firewall
- Fritz!Box übernimmt die Edge-Firewall
- SSH ist noch nicht vollständig gehärtet
- Root-Login steht auf `without-password`
- Passwortauthentifizierung ist derzeit aktiviert

Diese Punkte sind dokumentiert und sollen bei einer späteren Sicherheitsausbaustufe erneut bewertet werden.

---

# Schreiblast

Der Server ist bewusst auf geringe SD-Karten-Schreiblast ausgelegt.

Aktiv:

```text
ext4 noatime
reduziertes Journald
Pi-hole Query Logging deaktiviert
Logrotate
fstrim
DynDNS ohne Logdatei
```

Das Dashboard selbst verwendet keine Datenbank und speichert keine historischen Messwerte.

---

# Dashboard v3.3

Das produktive Dashboard zeigt derzeit unter anderem:

## Systemstatus

- Gesamtstatus
- Hardwareintegrität
- Unterspannung
- Frequenzbegrenzung
- Drosselung
- Temperatur-Limit
- Root-Dateisystem
- aktive Dienste

## Ressourcen

- CPU-Temperatur
- Load Average
- RAM
- zram-Swap
- SD-Karte
- Inodes

## Systeminformationen

- Hostname
- Hardware
- Betriebssystem
- Kernel
- letzter Start
- Uptime

## Netzwerk

- IPv4
- Gateway
- IPv6
- MAC-Adresse
- Interface-Zustände

## Dienste

- nginx
- MeshCentral
- Pi-hole FTL
- fcgiwrap
- SSH
- NetworkManager
- systemd-timesyncd

## Leistung

- CPU-Temperatur
- CPU-Last
- CPU-Frequenz
- Prozessanzahl

---

# Nächster Entwicklungsschritt

Geplant ist zunächst eine Weiterentwicklung des Dashboards.

Arbeitsrichtung:

**Status Dashboard v3.4**

Priorität:

1. Dienst-Erreichbarkeit
2. Netzwerkchecks
3. erwartete Ports
4. Zertifikatsprüfung
5. Sicherheitschecks

Danach:

6. Update-Status
7. weitere Hardwareinformationen
8. Komfortinformationen

---

# Wichtige Designentscheidung

Nicht möglichst viele Informationen anzeigen.

Das Dashboard soll ein:

> Appliance Health Monitor

bleiben.

Die wichtigste Frage lautet:

> Gibt es aktuell ein Problem und kann das Dashboard erklären, wo es liegt?

---

# Nicht vorgesehen

Derzeit ausdrücklich nicht geplant:

- Kubernetes
- große Containerlandschaft
- Grafana
- InfluxDB
- unnötige Datenbanken
- permanente Messwerthistorie
- komplexe Monitoring-Infrastruktur

---

# Änderungsprinzip

Vor größeren Änderungen:

1. funktionierenden Zustand dokumentieren
2. Snapshot erstellen
3. Änderung möglichst isoliert durchführen
4. Funktion testen
5. Ergebnis dokumentieren

Neue Funktionen sollen bevorzugt additiv eingebaut werden.

Bestehende produktive Komponenten sollen nicht ohne Not verändert werden.

---

# Wiedereinstieg für einen neuen Chat

Folgender Text kann als Einstieg für zukünftige Arbeiten verwendet werden:

> Wir arbeiten am Makki-Heimserver OtterPi (`otterpi`).
>
> Das Service-Portal v1.0 und das Status Dashboard v3.3 sind produktiv.
>
> MeshCentral v1.2.4 läuft im Hybrid-Modus hinter nginx.
>
> Das Zertifikatskonzept mit `certUrl` und dem automatischen systemd-Zertifikatsmonitor ist produktiv und getestet.
>
> Der nächste geplante Schritt ist die Weiterentwicklung des Status Dashboards in Richtung eines kleinen Appliance Health Monitors / Selbstdiagnose-Systems.
>
> Wichtig: Keine unnötige Komplexität, keine Datenbank und keine permanente historische Datenspeicherung. SD-Karten-Schreiblast möglichst gering halten.
>
> Vor Änderungen zuerst den vorhandenen Stand prüfen und Änderungen möglichst isoliert durchführen.

---

# Repository-Grundsatz

Dieses Repository ist die technische Referenz für den dokumentierten OtterPi-Stand.

Es soll ermöglichen, auch nach längerer Pause ohne erneute Rekonstruktion der gesamten Servergeschichte weiterzuarbeiten.

🦦
