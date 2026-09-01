# OtterPi – Betrieb und Wartung

**Projekt:** Makki Heimserver / OtterPi  
**Dokument:** Betriebs- und Wartungskonzept  
**Stand:** August 2026  
**System:** `otterpi`

---

## 1. Zweck

Dieses Dokument beschreibt den normalen Betrieb, die grundlegende Wartung und die wichtigsten Kontrollmaßnahmen des OtterPi.

Der OtterPi ist als kleine, wartbare private Infrastruktur ausgelegt.

Das Ziel ist nicht maximale Automatisierung oder ein vollständiges Monitoring-System, sondern:

- stabiler Dauerbetrieb
- möglichst geringe Komplexität
- geringe Schreiblast auf der SD-Karte
- nachvollziehbare Konfiguration
- einfache Wiederherstellung
- klare Diagnosemöglichkeiten

---

## 2. Grundsatz

Änderungen am produktiven System werden grundsätzlich nachvollziehbar und möglichst einzeln durchgeführt.

Vor größeren Änderungen soll ein aktueller Systemstand dokumentiert beziehungsweise gesichert werden.

Insbesondere vor Änderungen an:

- MeshCentral
- Nginx
- DNS
- Zertifikaten
- systemd-Units
- Netzwerkdiensten
- Dashboard
- Firewall-/Zugriffsregeln

soll der aktuelle Zustand festgehalten werden.

---

## 3. Normaler Betriebszustand

Der normale produktive Zustand umfasst unter anderem:

- Raspberry Pi läuft stabil
- `nginx` ist aktiv
- `meshcentral` ist aktiv
- `pihole-FTL` ist aktiv
- `fcgiwrap` ist aktiv
- `NetworkManager` ist aktiv
- `systemd-timesyncd` ist aktiv
- MeshCentral ist über den Reverse Proxy erreichbar
- Zertifikatsmonitor und Timer sind aktiv
- Dashboard ist über das LAN erreichbar
- Root-Dateisystem ist `rw`
- kein aktiver Hardwarefehler
- ausreichend freier Speicher

---

## 4. Schnelle Statusprüfung

Bei einer kurzen Kontrolle sind insbesondere folgende Befehle relevant:

```sh
hostname
uptime
systemctl --failed
systemctl status nginx --no-pager
systemctl status meshcentral --no-pager
systemctl status pihole-FTL --no-pager
df -h /
free -h
```

Für den Hardwarezustand des Raspberry Pi:

```sh
vcgencmd get_throttled
```

Für die Netzwerkgrundlage:

```sh
ip addr
ip route
```

---

## 5. Dashboard als erste Anlaufstelle

Das OtterPi Status Dashboard ist die bevorzugte schnelle Übersicht über den Systemzustand.

Aktuell zeigt das Dashboard unter anderem:

- Gesamtstatus
- Hardwareintegrität
- Unterspannung
- Frequenzbegrenzung
- Drosselung
- Temperatur-Limit
- Root-Dateisystem
- aktive Dienste
- CPU-Temperatur
- CPU-Load
- RAM
- zram-Swap
- SD-Karten-Auslastung
- Inodes
- Hostname
- Hardware
- Betriebssystem
- Kernel
- Bootzeit
- Uptime
- IPv4
- Gateway
- IPv6
- MAC-Adresse
- Netzwerkinterfaces
- CPU-Frequenz
- Prozessanzahl

Das Dashboard ist dabei bewusst kein historisches Monitoring-System.

Es beschreibt primär den **aktuellen Zustand**.

---

## 6. Dienstprüfung

Bei Problemen mit einem Dienst zunächst den Status prüfen:

```sh
systemctl status <dienst> --no-pager
```

Beispiel:

```sh
systemctl status meshcentral --no-pager
```

Anschließend können die letzten Meldungen geprüft werden:

```sh
journalctl -u <dienst> -n 100 --no-pager
```

Bei einem Dienst, der unmittelbar nach dem Start wieder beendet wird:

```sh
systemctl status <dienst> --no-pager
journalctl -u <dienst> -b --no-pager
```

---

## 7. MeshCentral

MeshCentral läuft intern und wird nicht direkt öffentlich veröffentlicht.

Der externe Zugriff erfolgt über:

```text
https://mesh.makki.route64.de
```

Der interne MeshCentral-Port ist:

```text
4430
```

Der Intel-AMT-Port ist:

```text
4433
```

Der interne HTTP-Redirect-Port ist:

```text
1024
```

Der öffentliche Zugriff erfolgt über Nginx.

### Bei MeshCentral-Problemen

Zuerst:

```sh
systemctl status meshcentral --no-pager
```

Danach:

```sh
journalctl -u meshcentral -n 100 --no-pager
```

Insbesondere nach einem Zertifikatswechsel sollte geprüft werden, ob MeshCentral das Zertifikat erneut über `certUrl` geladen hat.

---

## 8. Zertifikatsmonitor

Der Zertifikatsmonitor überwacht das Verhältnis zwischen:

```text
CDN-Zertifikat
      |
      v
cert.makki.route64.de
      |
      v
MeshCentral geladenes Zertifikat
```

Status prüfen:

```sh
systemctl status meshcentral-cert-check.timer --no-pager
```

Manuellen Prüflauf durchführen:

```sh
sudo systemctl start meshcentral-cert-check.service
```

Logs prüfen:

```sh
journalctl -u meshcentral-cert-check.service --no-pager
```

Der Service ist als `oneshot` ausgeführt.

Nach erfolgreichem Lauf darf er daher wieder:

```text
inactive (dead)
```

anzeigen.

Das ist kein Fehler.

Der Timer bleibt dabei aktiv.

---

## 9. Zertifikatswechsel

Ein Zertifikatswechsel am CDN ist kein manueller Sonderfall mehr.

Der vorgesehene Ablauf ist:

```text
CDN-Zertifikat ändert sich
        |
        v
Timer erkennt Unterschied
        |
        v
MeshCentral wird neu gestartet
        |
        v
MeshCentral lädt neues Zertifikat
        |
        v
erneute Prüfung
        |
        v
OK
```

Bei einer unerwarteten Störung sind zunächst die Logs des Zertifikatsmonitors und MeshCentral zu prüfen.

---

## 10. Nginx

Nginx stellt den öffentlichen HTTPS-Zugang bereit und fungiert als Reverse Proxy.

Bei Änderungen an der Nginx-Konfiguration soll vor dem Reload die Konfiguration geprüft werden:

```sh
sudo nginx -t
```

Nur bei erfolgreicher Prüfung:

```sh
sudo systemctl reload nginx
```

Bei Problemen:

```sh
systemctl status nginx --no-pager
journalctl -u nginx -n 100 --no-pager
```

Die bestehende MeshCentral-Konfiguration soll bei Änderungen an anderen Webangeboten nicht unnötig verändert werden.

---

## 11. Service-Portal

Das Service-Portal liegt unter:

```text
/var/www/makki/
```

Die produktive Startseite ist:

```text
/var/www/makki/index.html
```

Backups liegen unter:

```text
/var/www/makki/backups/
```

Änderungen am Portal sollen möglichst als separate Version oder Backup nachvollziehbar bleiben.

---

## 12. Status Dashboard

Das produktive Dashboard liegt unter:

```text
/var/www/status/cgi-bin/status.cgi
```

Die aktuelle dokumentierte Version ist:

```text
otterpi Status Dashboard v3.3
```

Die Entwicklungsrichtung für die nächste Version ist eine stärkere aktive Diagnose.

Dabei soll das Dashboard weiterhin:

- leichtgewichtig
- schnell
- stateless
- ohne Datenbank
- ohne historische Datenspeicherung
- ressourcenschonend

bleiben.

---

## 13. Speicher und SD-Karte

Die Root-Dateisystembelegung sollte regelmäßig kontrolliert werden:

```sh
df -h /
```

Zusätzlich:

```sh
df -i /
```

Große Verzeichnisse können bei Bedarf gesucht werden:

```sh
sudo du -xh /opt /var /home 2>/dev/null | sort -h | tail -30
```

Dabei ist besonders auf unerwartet stark wachsende Logs oder Datenverzeichnisse zu achten.

---

## 14. Journald

Das Journal ist bewusst klein gehalten.

Der aktuelle Zustand kann geprüft werden:

```sh
journalctl --disk-usage
```

Bootbezogene Meldungen:

```sh
journalctl -b
```

Fehler seit dem aktuellen Boot:

```sh
journalctl -p err -b --no-pager
```

Für eine schnelle Prüfung:

```sh
journalctl -p 0..3 -b --no-pager
```

Das Dashboard soll künftig relevante Journalfehler zusammenfassen, ohne selbst eine zusätzliche permanente Historie aufzubauen.

---

## 15. Neustart

Ein normaler Neustart erfolgt mit:

```sh
sudo reboot
```

Nach dem Neustart sollten automatisch wieder starten:

- Nginx
- MeshCentral
- Pi-hole FTL
- fcgiwrap
- NetworkManager
- systemd-timesyncd
- Zertifikatsmonitor-Timer

Nach einem geplanten Neustart kann der Gesamtzustand anschließend über das Dashboard und die wichtigsten systemd-Dienste kontrolliert werden.

---

## 16. Backup-Grundsatz

MeshCentral besitzt ein aktiviertes AutoBackup.

Backupziel:

```text
/opt/meshcentral/meshcentral-backups/
```

Die Backups sind verschlüsselt und werden mit Passwort geschützt.

Ein Archiv kann mit 7-Zip geprüft werden:

```sh
7z t <backup.zip>
```

Erwartetes Ergebnis:

```text
Everything is Ok
```

Ein Backup gilt erst dann als sinnvoll überprüft, wenn nicht nur die Datei vorhanden ist, sondern das Archiv tatsächlich testbar ist.

---

## 17. Änderungen an Konfigurationen

Vor manuellen Änderungen an produktiven Konfigurationen sollte eine Kopie erstellt werden.

Besonders wichtig:

```text
/opt/meshcentral/meshcentral-data/config.json
/etc/nginx/
/etc/systemd/system/
```

Nach Änderungen sollte jeweils die zuständige Konfiguration syntaktisch beziehungsweise funktional geprüft werden.

Beispiele:

```sh
node -e 'JSON.parse(require("fs").readFileSync("/opt/meshcentral/meshcentral-data/config.json","utf8")); console.log("JSON OK")'
```

und:

```sh
sudo nginx -t
```

---

## 18. Keine unnötige Wartungsautomatisierung

Der OtterPi soll nicht durch immer weitere Wartungsskripte und Hintergrunddienste komplexer werden.

Automatisiert werden sollen vor allem Dinge, die:

- zuverlässig erkennbar sind
- keinen zusätzlichen Datenbestand benötigen
- einen klaren Nutzen besitzen
- Fehler automatisch beheben können

Das Zertifikatsmonitoring ist ein Beispiel für eine solche sinnvolle Automatisierung.

---

## 19. Grundregel bei Fehlern

Bei einem Fehler nicht sofort mehrere Dinge gleichzeitig verändern.

Vorgehen:

1. aktuellen Zustand feststellen
2. Dienststatus prüfen
3. Journal prüfen
4. Netzwerk prüfen
5. Konfiguration prüfen
6. Ursache eingrenzen
7. eine Änderung durchführen
8. Ergebnis kontrollieren
9. Änderung dokumentieren

Dadurch bleibt nachvollziehbar, welche Maßnahme eine Störung verursacht oder behoben hat.

---

## 20. Zielbild

Der OtterPi soll langfristig ein kleines, selbstdiagnosefähiges System bleiben.

Das bedeutet:

```text
wenig Dienste
     +
klare Konfiguration
     +
automatische Wiederherstellung
     +
aktive Diagnose
     +
gute Dokumentation
```

und ausdrücklich nicht:

```text
möglichst viele Monitoring-Komponenten
     +
Datenbanken
     +
historische Metriken
     +
unnötige Hintergrunddienste
```

Die wichtigste Eigenschaft des Systems bleibt daher:

**Es soll im Fehlerfall möglichst schnell verständlich machen, was nicht funktioniert – ohne selbst zum komplexen Monitoring-Projekt zu werden.**
