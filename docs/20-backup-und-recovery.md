# OtterPi – Backup- und Recovery-Konzept

**Projekt:** Makki Heimserver / OtterPi  
**Dokument:** Backup und Wiederherstellung  
**Stand:** August 2026  
**System:** `otterpi`

---

## 1. Zweck

Dieses Dokument beschreibt den aktuellen Backup- und Wiederherstellungsstand des OtterPi.

Ziel ist eine möglichst einfache Wiederherstellung ohne unnötige zusätzliche Infrastruktur.

Der OtterPi verwendet bewusst kein großes Backup- oder Monitoring-System.

---

## 2. Grundprinzip

Backups sollen vor allem die Wiederherstellung der produktiven Konfiguration und der relevanten Dienstedaten ermöglichen.

Dabei gilt:

- möglichst wenige zusätzliche Dienste
- keine unnötigen Datenbanken
- verschlüsselte Backups für sensible Daten
- nachvollziehbare Speicherorte
- regelmäßige Prüfung der Backup-Archive
- Konfigurationen vor größeren Änderungen zusätzlich sichern

---

## 3. MeshCentral AutoBackup

MeshCentral besitzt ein aktiviertes AutoBackup.

Konfiguration:

```text
Backupintervall: 24 Stunden
Aufbewahrung: 10 Tage
ZIP-Passwort: gesetzt
```

Backupziel:

```text
/opt/meshcentral/meshcentral-backups/
```

---

## 4. Inhalt der MeshCentral-Backups

Die Backups dienen insbesondere zur Sicherung des MeshCentral-Zustands.

Zum relevanten Datenbestand gehören unter anderem:

```text
/opt/meshcentral/meshcentral-data/
```

Darin befinden sich unter anderem:

```text
config.json
meshcentral.db
meshcentral-events.db
meshcentral-power.db
meshcentral-stats.db
```

Die genaue Zusammensetzung eines einzelnen AutoBackups ist von der MeshCentral-Version und deren Backupmechanismus abhängig.

---

## 5. Backup-Dateien

Beispielhafte Dateien:

```text
meshcentral-autobackup-2026-07-31-01-57.zip
meshcentral-autobackup-2026-08-05-01-08.zip
```

Zum dokumentierten Systemstand waren mehrere Backups vorhanden.

Die Aufbewahrung ist auf 10 Tage begrenzt.

Damit soll verhindert werden, dass sich über längere Zeit unkontrolliert große Backupbestände ansammeln.

---

## 6. Backup-Berechtigungen

Backupverzeichnis:

```text
/opt/meshcentral/meshcentral-backups/
```

Berechtigung:

```text
drwxr-x---
```

Eigentümer:

```text
meshcentral:meshcentral
```

ZIP-Dateien:

```text
-rw-r-----
```

Eigentümer:

```text
meshcentral:meshcentral
```

Die Backups sind damit nicht allgemein für beliebige lokale Benutzer lesbar.

---

## 7. Verschlüsselung

Die MeshCentral-AutoBackups sind passwortgeschützt.

Ein Archiv kann beispielsweise mit 7-Zip getestet werden:

```sh
7z t /opt/meshcentral/meshcentral-backups/<backup.zip>
```

Bei einem korrekten Passwort wird erwartet:

```text
Everything is Ok
```

Das Vorhandensein einer ZIP-Datei allein gilt nicht als ausreichender Backupnachweis.

Ein Backup sollte zumindest gelegentlich technisch geprüft werden.

---

## 8. Konfigurationsbackups

Zusätzlich zu den automatischen MeshCentral-Backups existieren beziehungsweise existierten manuelle Kopien von `config.json`.

Beispiele:

```text
config.json.backup-2026-08-04
config.json.before-autobackup
config.json.before-newaccounts-2026-08-04-2357
config.json.working-2026-08-04
```

Diese Dateien dokumentieren Änderungen und erleichtern das Zurückgehen auf einen bekannten Konfigurationsstand.

---

## 9. Nginx-Konfiguration

Für Änderungen an Nginx soll ebenfalls ein vorheriger Zustand nachvollziehbar bleiben.

Relevanter Bereich:

```text
/etc/nginx/
```

Vor größeren Änderungen empfiehlt sich eine Kopie beziehungsweise ein dokumentierter Snapshot der betroffenen Konfiguration.

Nach einer Änderung muss die Syntax geprüft werden:

```sh
sudo nginx -t
```

Nur bei erfolgreicher Prüfung soll die neue Konfiguration aktiviert werden.

---

## 10. systemd-Konfiguration

Eigene systemd-Units befinden sich unter:

```text
/etc/systemd/system/
```

Dazu gehören insbesondere:

```text
meshcentral-cert-check.service
meshcentral-cert-check.timer
```

Bei Änderungen an diesen Dateien soll der vorherige Zustand ebenfalls gesichert oder dokumentiert werden.

Anschließend:

```sh
sudo systemctl daemon-reload
```

und die jeweilige Unit prüfen.

---

## 11. Zertifikatsmonitor

Der Zertifikatsmonitor selbst verwendet einen kleinen Statusbereich:

```text
/var/lib/meshcentral-cert-check/
```

Darin befinden sich:

```text
external_hash
meshcentral_hash
last_status
```

Diese Dateien sind kein klassisches Backup.

Sie stellen lediglich den aktuellen Betriebszustand des Zertifikatsmonitors dar.

Ein Verlust dieser Dateien ist daher kein Verlust des MeshCentral-Datenbestands.

---

## 12. Service-Portal

Das Service-Portal befindet sich unter:

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

Änderungen am Portal sollen möglichst versioniert oder vor der Änderung kopiert werden.

---

## 13. Status Dashboard

Das produktive Dashboard befindet sich unter:

```text
/var/www/status/cgi-bin/status.cgi
```

Eine Entwicklungsfassung kann separat gehalten werden.

Der produktive Stand soll vor größeren Änderungen kopiert werden.

Das Dashboard selbst besitzt keine historische Datenbank.

Daher besteht sein wesentlicher Wiederherstellungsbedarf aus:

```text
status.cgi
```

sowie eventuell zugehörigen statischen Dateien.

---

## 14. Was nicht als Backup benötigt wird

Nicht jeder Laufzeitwert muss gesichert werden.

Insbesondere sind folgende Daten grundsätzlich reproduzierbar:

- CPU-Last
- RAM-Auslastung
- Temperatur
- Uptime
- Netzwerkstatus
- Prozessliste
- aktuelle systemd-Zustände
- aktuelle Journal-Laufzeitdaten
- Zertifikatsmonitor-Statusdateien

Das Dashboard erzeugt bewusst keine langfristige Historie.

---

## 15. Recovery-Ziel

Das Ziel einer Wiederherstellung ist nicht zwingend eine bitgenaue Rekonstruktion des gesamten Betriebssystems.

Viel wichtiger ist die Wiederherstellung der produktiven Dienste und ihrer Konfiguration.

Priorität:

1. Netzwerk
2. Nginx
3. MeshCentral
4. MeshCentral-Daten
5. Pi-hole
6. Service-Portal
7. Status Dashboard
8. Zertifikatsmonitor
9. sonstige individuelle Konfiguration

---

## 16. Recovery nach Konfigurationsfehler

Wenn eine Änderung einen Dienst beschädigt, soll möglichst zuerst die letzte funktionierende Konfiguration wiederhergestellt werden.

Beispiel MeshCentral:

```sh
sudo cp <backup-config.json> \
/opt/meshcentral/meshcentral-data/config.json
```

Danach JSON prüfen:

```sh
node -e 'JSON.parse(require("fs").readFileSync("/opt/meshcentral/meshcentral-data/config.json","utf8")); console.log("JSON OK")'
```

Danach:

```sh
sudo systemctl restart meshcentral
```

und anschließend:

```sh
systemctl status meshcentral --no-pager
```

---

## 17. Recovery nach Nginx-Fehler

Zunächst:

```sh
sudo nginx -t
```

Bei einem Konfigurationsfehler muss nicht sofort das gesamte System verändert werden.

Stattdessen:

1. letzte Änderung identifizieren
2. betroffene Datei feststellen
3. vorherige Version wiederherstellen
4. `nginx -t`
5. Nginx reloaden
6. externe Erreichbarkeit prüfen

---

## 18. Recovery nach MeshCentral-Zertifikatsproblem

Zuerst:

```sh
systemctl status meshcentral --no-pager
```

Dann:

```sh
journalctl -u meshcentral -n 100 --no-pager
```

Anschließend den Zertifikatsmonitor prüfen:

```sh
systemctl status meshcentral-cert-check.timer --no-pager
journalctl -u meshcentral-cert-check.service --no-pager
```

Der Zertifikatsmonitor kann bei einem erkannten Unterschied selbstständig einen MeshCentral-Neustart auslösen.

---

## 19. Recovery nach Raspberry-Pi-Neustart

Nach einem normalen Reboot sollen die produktiven Dienste automatisch wieder starten.

Prüfen:

```sh
systemctl --failed
```

Danach insbesondere:

```sh
systemctl status nginx --no-pager
systemctl status meshcentral --no-pager
systemctl status pihole-FTL --no-pager
systemctl status fcgiwrap --no-pager
systemctl status meshcentral-cert-check.timer --no-pager
```

Zusätzlich:

```sh
df -h /
```

und:

```sh
vcgencmd get_throttled
```

---

## 20. Recovery nach SD-Karten-Ausfall

Bei einem vollständigen Ausfall der SD-Karte ist eine Neuinstallation des Raspberry-Pi-Systems erforderlich.

Der Wiederaufbau erfolgt schrittweise:

```text
Raspberry Pi OS
      |
      v
Netzwerk
      |
      v
Basisdienste
      |
      v
Nginx
      |
      v
Pi-hole
      |
      v
MeshCentral
      |
      v
Konfiguration / Daten
      |
      v
Service-Portal
      |
      v
Status Dashboard
      |
      v
Zertifikatsmonitor
```

Dabei sollen nicht benötigte Altlasten vermieden werden.

Ein Neuaufbau ist eine Gelegenheit, nur den dokumentierten produktiven Zustand wiederherzustellen.

---

## 21. Recovery-Dokumentation

Nach einer tatsächlichen Wiederherstellung soll dokumentiert werden:

- Ursache
- betroffene Komponente
- Wiederherstellungsmethode
- verwendetes Backup
- erfolgreiche Tests
- eventuell geänderte Konfiguration
- neuer Systemstand

Damit bleibt nachvollziehbar, welcher Zustand aktuell produktiv ist.

---

## 22. Backup ist nicht gleich Recovery

Ein vorhandenes Backup bedeutet nicht automatisch, dass eine Wiederherstellung funktioniert.

Deshalb gilt:

```text
Backup vorhanden
      ≠
Recovery getestet
```

Für besonders wichtige Komponenten sollten Wiederherstellungswege zumindest gedanklich und dokumentarisch nachvollziehbar sein.

Die bisher durchgeführten Tests haben insbesondere die automatische Wiederherstellung nach:

- Agent-Neustart
- Raspberry-Reboot
- Zertifikatswechsel

erfolgreich bestätigt.

---

## 23. Bewusste Grenzen

Der OtterPi erhält derzeit bewusst kein zusätzliches Backup-Ökosystem mit:

- separatem Backupserver
- Datenbank
- Grafana
- InfluxDB
- dauerhaftem Monitoringdienst
- komplexem Backup-Agenten

Der bestehende Mechanismus soll zunächst ausreichend sein.

Eine spätere externe Sicherung kann ergänzt werden, wenn der tatsächliche Bedarf dafür entsteht.

---

## 24. Zielzustand

Der gewünschte Backupzustand ist:

```text
klein
+
verschlüsselt
+
regelmäßig
+
prüfbar
+
dokumentiert
+
wiederherstellbar
```

Der wichtigste Grundsatz bleibt:

**Der OtterPi soll auch nach einem Fehler oder Neuaufbau wieder zu einem bekannten, dokumentierten Produktionszustand zurückkehren können.**
