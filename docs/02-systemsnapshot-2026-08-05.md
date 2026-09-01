# 🦦 OtterPi – Systemsnapshot

Stand: 05.08.2026, 01:15 CEST

Dieser Snapshot beschreibt den dokumentierten Systemzustand des Raspberry-Pi-Heimservers `otterpi`.

## 1. Systembasis

### Host

Hostname:

`otterpi`

System:

Linux auf Raspberry Pi

Architektur:

`arm64`

Hardware:

Raspberry Pi 4 Model B Rev 1.5

CPU:

4 Kerne

RAM:

1 GB

### Netzwerk

#### LAN

Interface:

`eth0`

IPv4:

`192.168.178.100/24`

Gateway:

`192.168.178.1`

Gateway-Gerät:

Fritz!Box

#### IPv6

Globales IPv6:

aktiv

ULA IPv6:

aktiv

#### WLAN

Interface:

`wlan0`

Status:

`DOWN`

## 2. Speicherzustand

Root-Dateisystem:

```text
/dev/mmcblk0p2   58G   11G   46G   19%
```

Boot:

```text
/dev/mmcblk0p1   505M
```

Dateisystem:

`ext4`

Mountoption:

`noatime`

### Relevante Verzeichnisse

```text
/opt/meshcentral        773M
/opt/pihole             216K
/opt/Scratch            421M
/opt/WidevineCdm        9.9M
```

## 3. MeshCentral

Installationspfad:

`/opt/meshcentral`

Version:

`MeshCentral v1.2.4`

Betriebsmodus:

`Hybrid (LAN + WAN)`

Service:

`meshcentral`

Status:

`running`

### Ports

Interne Ports:

```text
4430   MeshCentral HTTP
4433   Intel AMT
1024   HTTP Redirect
```

Agent:

```text
16989
```

Öffentliche Bereitstellung:

```text
nginx :443
        ↓
MeshCentral :4430
```

MeshCentral ist nicht direkt öffentlich auf Port 4430 erreichbar.

## 4. MeshCentral-Daten

Pfad:

`/opt/meshcentral/meshcentral-data/`

Datenbanken:

```text
meshcentral.db
meshcentral-events.db
meshcentral-power.db
meshcentral-stats.db
```

Aktuelle Größen:

```text
meshcentral.db              41K
meshcentral-events.db      990K
meshcentral-power.db       4.8K
meshcentral-stats.db       103K
```

## 5. MeshCentral-Zertifikate

Vorhandene private Schlüssel:

```text
agentserver-cert-private.key
codesign-cert-private.key
mpsserver-cert-private.key
root-cert-private.key
webserver-cert-private.key
```

Berechtigung:

```text
-rw-------
```

Owner:

`meshcentral`

Status:

OK.

## 6. Zertifikatsmonitor

Service:

`meshcentral-cert-check.service`

Timer:

`meshcentral-cert-check.timer`

Status:

`enabled`

`active`

Prüfintervall:

ca. 10 Minuten

### Aktueller Zertifikatshash

```text
c02a613bc7b5538ddb8161d5c76cc983152883ce272ee5f2f7e0d42adee969c4cbda3fc6778c0746040a0e07d6b50c7d
```

Ergebnis:

CDN-Zertifikat und MeshCentral-Zertifikat identisch.

## 7. MeshCentral AutoBackup

AutoBackup ist über `config.json` aktiviert.

Intervall:

`24 Stunden`

Aufbewahrung:

`10 Tage`

Backupziel:

`/opt/meshcentral/meshcentral-backups/`

ZIP-Passwort:

gesetzt

### Backupstatus zum Snapshot-Zeitpunkt

Es waren 5 Backups vorhanden.

Beispiele:

```text
meshcentral-autobackup-2026-07-31-01-57.zip
meshcentral-autobackup-2026-08-05-01-08.zip
```

Letztes Backup wurde mit:

```text
7z t backup.zip
```

geprüft.

Ergebnis:

```text
Everything is Ok
```

Archiv:

verschlüsselt

Passwort:

erforderlich

## 8. Backup-Berechtigungen

Backupverzeichnis:

```text
drwxr-x---
meshcentral:meshcentral
```

ZIP-Dateien:

```text
-rw-r-----
meshcentral:meshcentral
```

## 9. MeshCentral config.json

Produktiver Pfad:

`/opt/meshcentral/meshcentral-data/config.json`

Berechtigung:

```text
-rw-r-----
```

Owner:

`meshcentral:meshcentral`

JSON-Prüfung:

`node JSON.parse()`

Ergebnis:

`JSON OK`

Vorhandene manuelle Sicherungen:

```text
config.json.backup-2026-08-04
config.json.before-autobackup
config.json.before-newaccounts-2026-08-04
config.json.working-2026-08-04
```

Einige Sicherungen wurden bewusst mit Root-Berechtigungen angelegt.

## 10. Laufende Dienste und Ports

Zum Snapshot-Zeitpunkt relevante Listener:

```text
22       SSH
53       Pi-hole DNS
80       nginx
443      nginx
8080     Pi-hole Web
1024     MeshCentral Redirect
4430     MeshCentral
4433     MeshCentral AMT
16989    MeshCentral Agent
```

## 11. SSH

Port:

`22`

Aktuelle Konfiguration:

```text
PermitRootLogin without-password
PasswordAuthentication yes
PubkeyAuthentication yes
MaxAuthTries 6
```

Bewertung:

Noch nicht vollständig gehärtet.

## 12. Firewall

Eine lokale Host-Firewall ist derzeit nicht installiert.

`ufw`:

nicht vorhanden

Aktuelle Entscheidung:

Keine lokale Firewall.

Begründung:

- Fritz!Box übernimmt die Edge-Firewall.
- Der Raspberry Pi soll später weitere Dienste aufnehmen.
- Zunächst soll eine vollständige Dienstaufnahme erfolgen.
- Eine Firewall soll anschließend gezielt nach tatsächlichen Anforderungen konfiguriert werden.

## 13. rpcbind

Installiert:

`rpcbind 1.2.7-1`

Status:

`active`

Listener:

```text
TCP 111
UDP 111
```

Aktuell registrierte RPC-Dienste:

keine außer dem Portmapper.

Bewertung:

Vor einer Deaktivierung soll geprüft werden, ob der Dienst tatsächlich benötigt wird.

## 14. Pi-hole

Installationspfad:

`/opt/pihole`

Dienst:

`pihole-FTL`

Status:

aktiv

Ports:

```text
53     DNS
8080   Webinterface
```

## 15. Aktive Dienste

Aktuell überwachte Dienste:

```text
nginx
MeshCentral
pihole-FTL
fcgiwrap
ssh
NetworkManager
systemd-timesyncd
```

## 16. Schreiboptimierungen

Aktiv:

```text
ext4 noatime
Pi-hole Query Logging deaktiviert
kleines Journald
Logrotate
fstrim
DynDNS ohne Logdatei
```

Ziel:

Minimierung unnötiger permanenter Schreibvorgänge auf der SD-Karte.

## 17. Systemstatus

Der dokumentierte Zustand zum Zeitpunkt dieses Snapshots war produktiv.

Die wesentlichen Funktionen wurden zuvor erfolgreich getestet:

- MeshCentral startet automatisch
- MeshCentral-Agent verbindet sich automatisch
- Reverse Proxy funktioniert
- TLS funktioniert
- Zertifikatsmonitor funktioniert
- systemd-Timer funktioniert
- Raspberry-Pi-Reboot funktioniert
- Agent-Reboot funktioniert
- Zertifikatswechsel-Simulation funktioniert
- automatische Recovery funktioniert

## 18. Snapshot-Zweck

Dieser Snapshot dient als Referenz für zukünftige Änderungen.

Insbesondere sollen spätere Änderungen am:

- Service-Portal
- Status-Dashboard
- nginx
- Netzwerk
- Sicherheitskonzept

gegen diesen Zustand verglichen werden können.

Vor größeren Änderungen soll erneut ein Snapshot erstellt werden.
