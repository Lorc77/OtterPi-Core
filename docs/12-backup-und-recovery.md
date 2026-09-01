# OtterPi Core – Backup und Recovery

Stand: August 2026
System: otterpi

## 1. Grundprinzip

Der OtterPi soll möglichst einfach wiederherstellbar sein.

Backups werden dort eingesetzt, wo ein Verlust der Daten oder Konfiguration einen manuellen Wiederaufbau verursachen würde.

Gleichzeitig soll die Backup-Struktur die SD-Karte nicht unnötig belasten.

Es wird deshalb bewusst kein komplexes Backup- oder Monitoring-System eingesetzt.

## 2. MeshCentral AutoBackup

MeshCentral besitzt eine aktivierte AutoBackup-Funktion.

Die Konfiguration befindet sich in:

/opt/meshcentral/meshcentral-data/config.json

AutoBackup ist aktiviert.

Aktuelle Einstellungen:

- Backupintervall: 24 Stunden
- Aufbewahrung: 10 Tage
- ZIP-Passwort: gesetzt

## 3. Backup-Verzeichnis

Die MeshCentral-Backups werden gespeichert unter:

/opt/meshcentral/meshcentral-backups/

Das Verzeichnis gehört:

meshcentral:meshcentral

Aktuelle Berechtigungen:

drwxr-x---

Die Backup-Dateien gehören ebenfalls:

meshcentral:meshcentral

Aktuelle Berechtigungen der ZIP-Dateien:

-rw-r-----

Dadurch können die Backups nicht von beliebigen lokalen Benutzern gelesen werden.

## 4. Backup-Dateien

Die Dateien folgen dem MeshCentral-Schema:

meshcentral-autobackup-JJJJ-MM-TT-HH-MM.zip

Beispiele aus dem dokumentierten Systemstand:

meshcentral-autobackup-2026-07-31-01-57.zip

meshcentral-autobackup-2026-08-05-01-08.zip

Zum Stand des Snapshots waren fünf Backups vorhanden.

## 5. Verschlüsselung

Die AutoBackup-Archive sind passwortgeschützt.

Das Passwort ist gesetzt und gehört nicht in das öffentliche OtterPi-Core-Repository.

Die Repository-Dokumentation beschreibt deshalb nur:

- dass ein Passwort verwendet wird
- dass die Archive verschlüsselt sind
- wie die Integrität geprüft werden kann

Das tatsächliche Passwort wird ausschließlich lokal verwaltet.

## 6. Backup-Prüfung

Ein Backup wurde testweise mit 7-Zip geprüft.

Beispiel:

7z t backup.zip

Ergebnis:

Everything is Ok

Damit wurde sowohl die Lesbarkeit als auch die Archivintegrität geprüft.

Da das Archiv verschlüsselt ist, ist für eine vollständige Prüfung das Backup-Passwort erforderlich.

## 7. Was MeshCentral sichert

Das MeshCentral-AutoBackup dient insbesondere zur Sicherung der MeshCentral-Konfiguration und der zugehörigen persistenten Daten.

Zum MeshCentral-Datenverzeichnis gehören unter anderem:

/opt/meshcentral/meshcentral-data/

Dort befinden sich unter anderem:

meshcentral.db
meshcentral-events.db
meshcentral-power.db
meshcentral-stats.db
config.json

Die tatsächliche Backup-Zusammensetzung wird von MeshCentral bestimmt.

## 8. Konfigurationsdatei

Die produktive Konfiguration befindet sich unter:

/opt/meshcentral/meshcentral-data/config.json

Berechtigung:

-rw-r-----

Besitzer:

meshcentral:meshcentral

Die JSON-Syntax wurde erfolgreich geprüft.

Prüfung über Node.js:

node JSON.parse()

Ergebnis:

JSON OK

## 9. Manuelle Konfigurationssicherungen

Während der Entwicklung wurden zusätzlich mehrere Kopien der config.json angelegt.

Beispiele:

config.json.backup-2026-08-04

config.json.before-autobackup

config.json.before-newaccounts-2026-08-04-2357

config.json.working-2026-08-04

Diese Dateien dienten insbesondere als Sicherheitskopien während Konfigurationsänderungen.

Ein Teil dieser Dateien wurde bewusst mit root als Besitzer abgelegt.

## 10. Grundsatz für zukünftige Änderungen

Vor größeren Änderungen an produktiven Konfigurationen soll grundsätzlich zuerst eine Rückfallmöglichkeit geschaffen werden.

Beispiel:

1. aktuelle Konfiguration sichern
2. Änderung durchführen
3. JSON beziehungsweise Syntax prüfen
4. Dienst neu starten
5. Funktion testen
6. bei Fehler auf vorherigen Stand zurückkehren

Dadurch soll verhindert werden, dass eine einzelne Konfigurationsänderung den produktiven Dienst dauerhaft beschädigt.

## 11. Systemweite Wiederherstellung

Neben den MeshCentral-Backups existiert die Projektdokumentation im OtterPi-Core-Repository.

Das Repository dokumentiert:

- Hardware
- Betriebssystem
- Netzwerk
- Dienste
- Webstruktur
- Dashboard
- Zertifikatskonzept
- Backup-Konzept
- bekannte Abhängigkeiten
- geplante Erweiterungen

Das Repository ist ausdrücklich keine vollständige Systemkopie.

Es dient als technischer Wiederaufbau- und Wiedereinstiegspunkt.

## 12. Was NICHT ins Repository gehört

Nicht in das Repository gehören:

- private Schlüssel
- Passwörter
- API-Keys
- DynDNS-Schlüssel
- Zugangsdaten
- verschlüsselte Backup-Passwörter
- persönliche Geheimnisse
- private Zertifikatsdateien

Solche Werte werden ausschließlich lokal beziehungsweise in einer geeigneten geheimen Konfiguration verwaltet.

## 13. MeshCentral-Zertifikate

Im MeshCentral-Datenverzeichnis existieren unter anderem private Schlüssel:

agentserver-cert-private.key
codesign-cert-private.key
mpsserver-cert-private.key
root-cert-private.key
webserver-cert-private.key

Diese Dateien sind vertraulich.

Die dokumentierten Berechtigungen:

-rw-------

Besitzer:

meshcentral

Die privaten Schlüssel dürfen nicht in das OtterPi-Core-Repository übernommen werden.

## 14. Recovery – MeshCentral

Bei einem Problem mit MeshCentral ist zunächst der Dienstzustand zu prüfen:

systemctl status meshcentral

Danach:

journalctl -u meshcentral -n 100

Bei Konfigurationsproblemen sollte zunächst die zuletzt funktionierende config.json wiederhergestellt werden.

Anschließend:

1. JSON-Syntax prüfen
2. MeshCentral neu starten
3. Dienststatus prüfen
4. Webzugriff testen
5. Agent-Verbindung prüfen
6. Zertifikatsmonitor kontrollieren

## 15. Recovery – Zertifikatsproblem

Bei einem Zertifikatsproblem ist nicht sofort die Konfiguration zu verändern.

Zuerst prüfen:

cert.makki.route64.de

Danach den externen Zertifikats-Hash bestimmen.

Anschließend den von MeshCentral geladenen Hash vergleichen.

Der vorhandene Zertifikatsmonitor kann anschließend manuell ausgeführt werden:

sudo systemctl start meshcentral-cert-check.service

Das automatische Recovery wurde erfolgreich getestet.

## 16. Recovery – Raspberry-Pi-Neustart

Nach einem Neustart des Raspberry Pi sollen die produktiven Dienste automatisch starten.

Dazu gehören insbesondere:

- nginx
- MeshCentral
- Pi-hole FTL
- fcgiwrap
- NetworkManager
- systemd-timesyncd
- Zertifikatsmonitor beziehungsweise Timer

Der automatische Start wurde erfolgreich getestet.

Auch der erste Timerlauf des Zertifikatsmonitors nach einem Boot wurde erfolgreich geprüft.

## 17. Recovery – Agent

Ein MeshCentral-Agent wurde testweise neu gestartet.

Erwartetes Verhalten:

Agent
↓
offline
↓
automatischer Reconnect
↓
online

Der Reconnect wurde erfolgreich getestet.

Es war kein manueller Eingriff erforderlich.

## 18. Recovery-Ziel

Ein Recovery soll möglichst deterministisch ablaufen.

Die Grundidee lautet:

Problem erkennen
↓
Ursache eingrenzen
↓
letzten funktionierenden Zustand bestimmen
↓
Konfiguration beziehungsweise Dienst wiederherstellen
↓
Dienst starten
↓
Funktion testen

Nicht vorgesehen ist ein blindes Neuinstallieren sämtlicher Komponenten.

## 19. Recovery-Dokumentation

Für zukünftige Erweiterungen sollen neue Dienste immer mit folgenden Informationen dokumentiert werden:

- Installationspfad
- Konfigurationspfad
- systemd-Service
- abhängige Dienste
- Ports
- benötigte Dateien
- Backup-Methode
- Wiederherstellungsmethode
- Funktionstest

Damit bleibt der Server auch nach längerer Pause nachvollziehbar.

## 20. Snapshot-Prinzip

Vor größeren Umbauten wird ein Systemsnapshot erstellt.

Ein Snapshot soll mindestens dokumentieren:

- aktuellen Systemzustand
- aktive Dienste
- Ports
- Konfiguration
- Speicherzustand
- Netzwerk
- Zertifikatsstatus
- Backupstatus
- bekannte funktionierende Tests

Dadurch kann nach einer Änderung eindeutig festgestellt werden:

"Was war vorher funktionierend?"

## 21. Aktueller Backup-Status

Zum dokumentierten Stand:

MeshCentral AutoBackup:

aktiv

Intervall:

24 Stunden

Aufbewahrung:

10 Tage

Backups vorhanden:

5

Archivprüfung:

erfolgreich

Verschlüsselung:

aktiv

Backup-Berechtigungen:

korrekt

## 22. Zielzustand

Das Backup-System soll weiterhin einfach bleiben.

Keine zusätzlichen komplexen Backup-Dienste sind derzeit vorgesehen.

Der Schwerpunkt liegt auf:

- funktionierenden MeshCentral-Backups
- geprüfter Archivintegrität
- sauberer Konfigurationssicherung
- nachvollziehbarer Dokumentation
- reproduzierbarem Recovery

Der OtterPi soll dadurch nicht zu einem Backup-Server werden.

Er soll lediglich zuverlässig genug dokumentiert und gesichert sein, dass ein Ausfall beherrschbar bleibt.

---
Ende der Datei
