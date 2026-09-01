# OtterPi-Core – Backup- und Recovery-Konzept

**Projekt:** Makki Heimserver / OtterPi  
**System:** `otterpi`  
**Stand:** August 2026  
**Dokument:** Backup und Wiederherstellung  
**Status:** Dokumentation des produktiven Systems

---

## 1. Zweck

Dieses Dokument beschreibt die aktuell vorhandenen Backup-Mechanismen des OtterPi-Systems sowie das Vorgehen zur Wiederherstellung.

Ziel ist nicht ein komplexes Enterprise-Backup-System, sondern eine möglichst einfache und nachvollziehbare Absicherung der für den Betrieb wichtigen Konfigurationen und Daten.

Grundprinzip:

> Das System soll mit möglichst wenig zusätzlicher Komplexität wiederherstellbar sein.

Dabei wird zwischen automatischen Anwendungs-Backups und manuellen Konfigurations-Backups unterschieden.

---

## 2. Grundsätzliche Backup-Strategie

Der OtterPi verwendet derzeit insbesondere:

- MeshCentral AutoBackup
- manuelle Sicherungen wichtiger Konfigurationsdateien
- eine definierte Backup-Verzeichnisstruktur
- regelmäßige Überprüfung der erzeugten Archive

Bewusst nicht vorgesehen sind derzeit:

- Datenbankserver für Backupverwaltung
- umfangreiche Monitoring-Systeme
- permanente Backup-Historien auf dem Raspberry Pi
- unnötige zusätzliche Hintergrunddienste

Die SD-Karte soll möglichst wenig zusätzlich belastet werden.

---

## 3. MeshCentral AutoBackup

MeshCentral verfügt über ein aktiviertes AutoBackup.

Konfiguration:

```text
AutoBackup: aktiviert
Intervall: 24 Stunden
Aufbewahrung: 10 Tage
ZIP-Passwort: gesetzt
```

Backup-Verzeichnis:

```text
/opt/meshcentral/meshcentral-backups/
```

Die Backups werden von MeshCentral automatisch erzeugt.

---

## 4. Inhalt der MeshCentral-Backups

Die MeshCentral-Backups dienen insbesondere dazu, den Zustand der MeshCentral-Installation einschließlich ihrer relevanten Daten wiederherstellen zu können.

Zum MeshCentral-Datenbestand gehören unter anderem:

```text
/opt/meshcentral/meshcentral-data/
```

Darin befinden sich beispielsweise:

```text
meshcentral.db
meshcentral-events.db
meshcentral-power.db
meshcentral-stats.db
config.json
```

Zusätzlich existieren die für MeshCentral relevanten Zertifikatsdaten und weitere interne Dateien.

---

## 5. Backup-Dateinamen

Die automatischen Archive werden mit Datum und Uhrzeit benannt.

Beispiel:

```text
meshcentral-autobackup-2026-07-31-01-57.zip
meshcentral-autobackup-2026-08-05-01-08.zip
```

Dadurch ist der zeitliche Stand eines Backups unmittelbar erkennbar.

---

## 6. Aufbewahrung

Die aktuelle Aufbewahrungsdauer beträgt:

```text
10 Tage
```

Bei einem Backup-Intervall von 24 Stunden entspricht dies ungefähr zehn verfügbaren täglichen Sicherungsständen.

Das ist für den derzeitigen Einsatz ausreichend.

Eine längere Historie ist momentan nicht erforderlich.

---

## 7. Verschlüsselung

Die MeshCentral-Backuparchive werden mit einem gesetzten ZIP-Passwort erzeugt.

Damit ist ein Backup-Archiv nicht ohne weiteres lesbar.

Ein Backup darf daher nicht nur auf seine Existenz geprüft werden.

Es muss zusätzlich überprüft werden, ob:

1. das Archiv tatsächlich geöffnet werden kann,
2. die Archivstruktur intakt ist,
3. die Verschlüsselung funktioniert,
4. das verwendete Passwort bekannt und verfügbar ist.

---

## 8. Integritätsprüfung

Ein erzeugtes Backup wurde bereits erfolgreich getestet.

Prüfung:

```text
7z t backup.zip
```

Ergebnis:

```text
Everything is Ok
```

Damit wurde bestätigt, dass das Archiv technisch lesbar und nicht beschädigt ist.

Die Prüfung ist wichtiger als die reine Existenz einer ZIP-Datei.

Ein vorhandenes, aber beschädigtes Backup wäre im Fehlerfall wertlos.

---

## 9. Backup-Berechtigungen

Das Backup-Verzeichnis gehört dem MeshCentral-Benutzer:

```text
meshcentral:meshcentral
```

Verzeichnis:

```text
drwxr-x---
```

Die erzeugten ZIP-Dateien besitzen:

```text
-rw-r-----
meshcentral:meshcentral
```

Damit sind die Backups nicht allgemein für alle lokalen Benutzer lesbar.

---

## 10. Konfigurations-Backups

Neben den automatischen MeshCentral-Backups existieren manuelle Sicherungen von `config.json`.

Produktive Datei:

```text
/opt/meshcentral/meshcentral-data/config.json
```

Beispielhafte Sicherungen:

```text
config.json.backup-2026-08-04
config.json.before-autobackup
config.json.before-newaccounts-2026-08-04-2357
config.json.working-2026-08-04
```

Diese Dateien entstanden im Rahmen der Konfigurationsarbeiten und dienen als zusätzliche Rückfallebene.

---

## 11. Konfigurationsdatei

Die produktive MeshCentral-Konfiguration ist:

```text
/opt/meshcentral/meshcentral-data/config.json
```

Aktuelle Berechtigung:

```text
-rw-r-----
meshcentral:meshcentral
```

Die Datei wurde nach Änderungen mit Node.js überprüft.

Verwendete Prüfung:

```text
node JSON.parse()
```

Ergebnis:

```text
JSON OK
```

Damit wird sichergestellt, dass keine syntaktisch ungültige JSON-Konfiguration aktiviert wird.

---

## 12. Was nicht automatisch gesichert wird

Nicht jede Datei des gesamten Raspberry-Pi-Dateisystems wird momentan automatisch versioniert.

Insbesondere existiert derzeit kein vollständiges Image-Backup der SD-Karte als Bestandteil des laufenden Systems.

Das ist eine bewusste Vereinfachung.

Der OtterPi ist so aufgebaut, dass sich die wesentlichen Komponenten anhand der dokumentierten Struktur wieder einrichten lassen.

Dazu gehören insbesondere:

```text
/opt/meshcentral/
/opt/pihole/
/var/www/makki/
/var/www/status/
/etc/nginx/
/etc/systemd/system/
/usr/local/sbin/
```

---

## 13. Besonders wichtige Konfigurationen

Bei einer vollständigen Wiederherstellung sind insbesondere folgende Bereiche relevant:

### MeshCentral

```text
/opt/meshcentral/meshcentral-data/config.json
```

### Zertifikatsmonitor

```text
/usr/local/sbin/check-mesh-cert.sh
```

### systemd

```text
/etc/systemd/system/
```

Relevant sind insbesondere:

```text
meshcentral-cert-check.service
meshcentral-cert-check.timer
```

### Nginx

```text
/etc/nginx/
```

### Service-Portal

```text
/var/www/makki/
```

### Status-Dashboard

```text
/var/www/status/cgi-bin/status.cgi
```

---

## 14. Recovery-Grundprinzip

Bei einem Fehler soll nicht sofort das gesamte System neu aufgebaut werden.

Zunächst wird festgestellt, welche Komponente betroffen ist.

Beispiele:

```text
MeshCentral funktioniert nicht
        ↓
MeshCentral-Service prüfen
        ↓
Konfiguration prüfen
        ↓
Journal prüfen
        ↓
Backup prüfen
```

oder:

```text
Nginx funktioniert nicht
        ↓
Nginx-Konfiguration prüfen
        ↓
nginx -t
        ↓
letzte Änderung feststellen
        ↓
Konfiguration aus Sicherung wiederherstellen
```

---

## 15. MeshCentral-Recovery

Bei einem beschädigten oder fehlerhaften MeshCentral-Zustand sollte zunächst der Dienstzustand geprüft werden:

```text
systemctl status meshcentral
```

Danach:

```text
journalctl -u meshcentral -n 100
```

Besonders relevant sind Meldungen zu:

- Konfigurationsfehlern
- Zertifikaten
- Datenbanken
- Ports
- Netzwerkverbindungen
- Startfehlern

Erst wenn die Ursache bekannt ist, sollte ein Backup zurückgespielt werden.

---

## 16. Zertifikats-Recovery

Das produktive MeshCentral-Zertifikat wird über:

```text
https://cert.makki.route64.de
```

bezogen.

Der Zertifikatsmonitor befindet sich unter:

```text
/usr/local/sbin/check-mesh-cert.sh
```

Der Monitor speichert seinen Status unter:

```text
/var/lib/meshcentral-cert-check/
```

Dort befinden sich:

```text
external_hash
meshcentral_hash
last_status
```

Bei Problemen mit dem Zertifikatsmonitor sind diese Dateien und anschließend der systemd-Dienst zu prüfen.

---

## 17. Zertifikatsmonitor manuell prüfen

Der Dienst kann manuell ausgeführt werden:

```text
sudo systemctl start meshcentral-cert-check.service
```

Danach:

```text
systemctl status meshcentral-cert-check.service
```

Das Service-Verhalten `inactive (dead)` nach einem erfolgreichen `Type=oneshot`-Lauf ist dabei normal.

Entscheidend ist:

```text
status=0/SUCCESS
```

---

## 18. MeshCentral-Backup testen

Ein Backup sollte nicht nur vorhanden sein, sondern regelmäßig testweise geprüft werden.

Beispiel:

```text
7z t /opt/meshcentral/meshcentral-backups/meshcentral-autobackup-YYYY-MM-DD-HH-MM.zip
```

Erwartetes Ergebnis:

```text
Everything is Ok
```

Bei einem verschlüsselten Archiv muss das korrekte Passwort verwendet werden.

---

## 19. Wiederherstellung aus MeshCentral-Backup

Eine Wiederherstellung sollte nicht unüberlegt auf der laufenden Produktivinstallation durchgeführt werden.

Grundsätzlich:

1. MeshCentral stoppen.
2. Aktuellen Zustand zusätzlich sichern.
3. Gewünschtes Backup auswählen.
4. Backup prüfen.
5. Relevante Daten wiederherstellen.
6. Berechtigungen kontrollieren.
7. MeshCentral starten.
8. Journal kontrollieren.
9. Webzugriff testen.
10. Agent-Verbindung prüfen.
11. Zertifikatsmonitor prüfen.

Beispiel für das Stoppen:

```text
sudo systemctl stop meshcentral
```

Nach der Wiederherstellung:

```text
sudo systemctl start meshcentral
```

---

## 20. Nach einer Wiederherstellung prüfen

Nach einer MeshCentral-Wiederherstellung müssen mindestens folgende Punkte geprüft werden:

```text
systemctl status meshcentral
```

```text
journalctl -u meshcentral -n 100
```

```text
systemctl status meshcentral-cert-check.timer
```

Danach:

- MeshCentral-Weboberfläche erreichbar
- Reverse Proxy funktioniert
- TLS funktioniert
- Zertifikat korrekt
- Agent verbindet sich
- Intel-AMT-Funktion weiterhin vorhanden, sofern benötigt

---

## 21. Systemweiter Wiederaufbau

Sollte nicht nur MeshCentral, sondern die gesamte SD-Karte ausfallen, wird das System grundsätzlich neu aufgebaut.

Die Wiederherstellung orientiert sich dabei an der dokumentierten Sollstruktur des OtterPi.

Wichtige Komponenten:

```text
Raspberry-Pi-Betriebssystem
        ↓
Netzwerk
        ↓
Nginx
        ↓
Pi-hole
        ↓
MeshCentral
        ↓
systemd-Dienste
        ↓
Zertifikatsmonitor
        ↓
Service-Portal
        ↓
Status-Dashboard
```

Die detaillierte Installation ist nicht Bestandteil dieses Dokuments.

Dieses Dokument beschreibt ausschließlich die Backup- und Recovery-Seite.

---

## 22. Wiederherstellung des Service-Portals

Das Portal liegt produktiv unter:

```text
/var/www/makki/
```

Wichtige Dateien beziehungsweise Ressourcen sind unter anderem:

```text
index.html
otter2.png
favicon.svg
```

Zusätzliche Favicon-Dateien für eingebundene Dienste gehören ebenfalls zur Portalstruktur.

Bei einer Wiederherstellung muss die bestehende Verzeichnisstruktur erhalten bleiben.

---

## 23. Wiederherstellung des Status-Dashboards

Das produktive Dashboard befindet sich unter:

```text
/var/www/status/cgi-bin/status.cgi
```

Aktueller Stand:

```text
otterpi · Status Dashboard v3.3
```

Die Entwicklungsfassung befand sich zuletzt unter:

```text
~/status.cgi-dashboard-v3.3-dev
```

Das Dashboard selbst benötigt keine Datenbank und keine historische Datenspeicherung.

Die Seite wird bei jedem Aufruf aus dem aktuellen Systemzustand erzeugt.

---

## 24. Warum keine Dashboard-Datenbank verwendet wird

Das Status-Dashboard ist ausdrücklich als:

> Appliance Health Monitor

konzipiert.

Es soll den aktuellen Zustand erklären und nicht historische Messwerte sammeln.

Daher sind derzeit bewusst nicht vorgesehen:

```text
InfluxDB
Grafana
Prometheus
historische Datenbanken
permanente Messwertspeicherung
```

Dadurch bleibt das Dashboard:

- leichtgewichtig
- schnell
- einfach wiederherstellbar
- wartungsarm
- SD-kartenschonend

---

## 25. Backup-Ziel außerhalb des Raspberry Pi

Die derzeitigen MeshCentral-Backups liegen lokal auf dem Raspberry Pi.

Das bedeutet:

> Ein Ausfall der SD-Karte kann gleichzeitig Produktivdaten und deren lokale Backups betreffen.

Für eine zukünftige Ausbaustufe ist deshalb eine zusätzliche externe Kopie sinnvoll.

Mögliche Ziele wären beispielsweise:

- anderer Rechner im LAN
- NAS
- externer Datenträger
- anderer vertrauenswürdiger Speicher

Dies ist derzeit noch nicht Bestandteil der produktiven Konfiguration.

---

## 26. Priorität für zukünftige Backup-Erweiterungen

Falls das Backup-Konzept erweitert wird, sollte die Reihenfolge möglichst einfach bleiben:

### Priorität 1

Externe Kopie der wichtigsten Konfigurationen.

### Priorität 2

Externe Kopie der MeshCentral-Backups.

### Priorität 3

Regelmäßiger automatischer Integritätstest.

### Priorität 4

Optional vollständiges SD-Karten- oder Systemimage.

Ein komplexes Backup-System ist ausdrücklich nicht das Ziel.

---

## 27. Recovery-Ziel

Der OtterPi soll im Fehlerfall nicht zwingend auf exakt denselben Zustand bis auf jede temporäre Datei zurückgesetzt werden.

Wichtiger ist die Wiederherstellung der funktionalen Infrastruktur:

```text
Internet / LAN
      ↓
Nginx
      ↓
Portal
      ↓
Status-Dashboard

und

Nginx
      ↓
MeshCentral
      ↓
Agenten

sowie

Pi-hole
```

Die aktuelle Systemarchitektur und Konfiguration sind deshalb mindestens genauso wichtig wie die Backups selbst.

---

## 28. Dokumentationsprinzip

Die Repository-Dokumentation ist Bestandteil des Recovery-Konzepts.

Ein Backup ohne Kenntnis über:

- Pfade
- Dienste
- Konfigurationen
- Ports
- DNS
- Zertifikate
- systemd
- Nginx
- Benutzer und Berechtigungen

ist nur eingeschränkt nützlich.

Deshalb wird der produktive Zustand im Repository möglichst vollständig dokumentiert.

---

## 29. Aktueller Stand

Zum dokumentierten Stand sind folgende Punkte erfolgreich geprüft:

```text
MeshCentral AutoBackup          OK
Backup vorhanden                OK
Backup-Archiv testbar           OK
Archiv verschlüsselt             OK
Backup-Berechtigungen            OK
config.json gesichert            OK
config.json syntaktisch gültig   OK
```

Das Backup-Konzept ist damit für den aktuellen Produktionsstand funktionsfähig.

---

## 30. Zusammenfassung

Der OtterPi verwendet bewusst ein schlankes Backup-Konzept.

Die wichtigsten Elemente sind:

- automatisches MeshCentral-Backup
- 24-Stunden-Intervall
- 10 Tage Aufbewahrung
- verschlüsselte Archive
- geprüfte Backup-Integrität
- zusätzliche Konfigurationssicherungen
- dokumentierte Wiederherstellungspfade
- keine zusätzliche Backup-Datenbank

Die wichtigste zukünftige Verbesserung wäre nicht mehr lokale Komplexität, sondern eine einfache externe Kopie der vorhandenen Backups.

Damit würde der Schutz vor einem vollständigen Verlust der SD-Karte deutlich verbessert.

---

**Status:** produktionsnah dokumentiert  
**Grundsatz:** Einfach, nachvollziehbar, wiederherstellbar. 🦦
