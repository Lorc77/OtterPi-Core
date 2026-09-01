# 🦦 OtterPi Status Dashboard – Roadmap

Stand: August 2026

Aktuelle produktive Version:

**otterpi Status Dashboard v3.3**

Ziel der nächsten Ausbaustufen:

Das Dashboard soll sich von einer reinen Zustandsanzeige zu einem kleinen, ressourcenschonenden **Appliance Health Monitor** beziehungsweise Selbstdiagnose-System entwickeln.

---

# 1. Aktualität / Systemzeit

Geplant:

- Anzeige „Letzte Aktualisierung“
- optional Erkennung, ob Daten aus einem Cache stammen
- Zeitstempel eindeutig als Messzeitpunkt kennzeichnen

Grundidee:

Der Benutzer soll jederzeit erkennen können, wie aktuell die angezeigten Werte sind.

---

# 2. Netzwerkdetails

Geplant:

## Ethernet

Anzeigen:

- Linkgeschwindigkeit
- 100 Mbit/s
- 1000 Mbit/s
- Duplex-Status

## WLAN

Falls vorhanden:

- SSID
- Signalstärke in dBm
- Kanal
- Verbindungstyp

---

# 3. Netzwerk-Erreichbarkeit

Geplante Prüfungen:

- Gateway-Erreichbarkeit
- DNS-Funktion
- optional externe Verbindung

Neue Netzwerk-Ampel:

### Grün

Netzwerk vollständig verfügbar.

### Gelb

Interface ist aktiv, aber eine Teilfunktion weist ein Problem auf.

### Rot

Keine funktionierende Netzwerkverbindung.

---

# 4. Speicherhardware

Geplant:

- Temperatur des Speichermediums, falls verfügbar
- SD-Karte / eMMC / SSD
- SMART-Werte, falls verfügbar
- Gesundheitsstatus des Speichermediums

Wichtig:

Die Anzeige soll nur Werte darstellen, die das jeweilige Speichermedium tatsächlich bereitstellt.

---

# 5. Systemfehler / Journal

Geplant:

- Anzahl kritischer Systemfehler seit Boot
- Zusammenfassung relevanter Journal-Fehler
- optional letzte relevante Fehlermeldung

Beispiel:

```text
Journal:
0 Fehler
```

Dabei soll keine zusätzliche dauerhafte Datenhaltung eingeführt werden.

---

# 6. Neustart und Shutdown

Weiterhin anzeigen:

- letzten Systemstart
- Uptime

Zusätzlich geplant:

- letzter sauberer Shutdown
- Erkennung ungewöhnlicher Neustarts

Beispiel:

```text
Letzter Neustart:
07.08.2026 02:14

Shutdown:
ordnungsgemäß
```

---

# 7. Raspberry-Pi-Hardware

Geplant, sofern die jeweilige Information verfügbar ist:

- Versorgungsspannung
- Firmware-Version
- Bootloader-Version
- weitere sinnvolle `vcgencmd`-Informationen

Es sollen keine Informationen künstlich ergänzt werden, wenn sie auf der vorhandenen Hardware oder Firmware nicht zuverlässig verfügbar sind.

---

# 8. CPU-Auslastung

Aktuell vorhanden:

- Load Average
- 1 Minute
- 5 Minuten
- 15 Minuten

Geplant:

- CPU-Auslastung in Prozent
- optional Auslastung einzelner CPU-Kerne

Beispiel:

```text
Load:
0.15 / 0.12 / 0.10

CPU:
8 %
```

---

# 9. Top-Prozesse

Geplant:

- CPU-intensivste Prozesse
- RAM-intensivste Prozesse
- jeweils Top 3

Beispiel:

```text
Top CPU:
node     12 %
nginx     2 %
```

Die Funktion soll als Momentaufnahme arbeiten und keine Prozesshistorie speichern.

---

# 10. Dienste

Für jeden überwachten Dienst könnten zusätzlich angezeigt werden:

- Laufzeit
- Startzeit
- Restart-Zähler
- optional letzter Fehler

Beispiel:

```text
nginx

Status:
aktiv

Laufzeit:
14 Tage

Restarts:
0
```

Dabei soll zwischen:

- Prozess läuft
- Dienst ist tatsächlich erreichbar

unterschieden werden.

---

# 11. Versionsinformationen

Geplante neue Sektion:

- Dashboard-Version
- Kernel-Version
- Betriebssystem-Version
- relevante Software-Versionen

Beispiele:

- MeshCentral
- Pi-hole
- nginx
- Node.js

---

# 12. Sicherheit / Netzwerkdienste

Geplante Sicherheitsübersicht:

- aktive SSH-Verbindungen
- letzter Login
- offene Ports
- laufende Netzwerkdienste

Beispiel:

```text
Offene Ports:

22   SSH
80   HTTP
443  HTTPS
```

Die Darstellung soll sich bevorzugt auf erwartete beziehungsweise relevante Ports konzentrieren.

Nicht jede interne technische Information muss im Dashboard erscheinen.

---

# 13. Erwartete Ports

Statt einfach alle offenen Ports zu zeigen, soll perspektivisch geprüft werden, ob die erwarteten Ports vorhanden sind.

Beispiel:

```text
22 SSH
🟢 LAN only

53 DNS
🟢 LAN only

80 HTTP
🟢 intern

443 HTTPS
🟢 extern
```

Ein unerwarteter Listener könnte beispielsweise als Warnung erscheinen:

```text
⚠ Unerwarteter Port

8080/tcp
Prozess: xyz
```

---

# 14. Firewall

Falls später eine lokale Firewall eingesetzt wird:

```text
🔥 Firewall

Status:
🟢 aktiv

Regeln:
12 geladen
```

Wenn keine lokale Firewall vorhanden ist:

```text
🟡 keine lokale Firewall aktiv
```

Das soll nicht automatisch als kritischer Fehler gewertet werden.

Die Bewertung muss dem tatsächlichen Sicherheitskonzept entsprechen.

---

# 15. Zertifikate

Geplante Prüfung wichtiger HTTPS-Endpunkte.

Beispiele:

```text
mesh.makki.route64.de
makki.route64.de
```

Darstellung:

```text
🔐 Zertifikate

mesh.makki.route64.de

🟢 gültig

Ablauf:
Datum
```

Bei nahendem Ablauf:

```text
🟡 läuft bald ab
```

---

# 16. Sicherheitschecks

Mögliche zukünftige Prüfungen:

## SSH

- SSH aktiv?
- Root-Login erlaubt?
- Passwortauthentifizierung aktiviert?

## Updates

- Sind relevante Pakete aktuell?

## Benutzer

Optional:

- ungewöhnliche Benutzer
- auffällige Änderungen

Sicherheitschecks sollen zunächst rein diagnostisch sein.

Das Dashboard soll keine automatischen Änderungen am System durchführen.

---

# 17. Backupstatus

Spätere optionale Erweiterung:

- letzte Sicherung
- Alter des letzten Backups
- Backupstatus
- Ampel

Beispiel:

```text
Backup

🟢 aktuell

Letztes Backup:
vor 4 Stunden
```

---

# 18. Historie

Eine Historie ist bewusst nur optional vorgesehen.

Mögliche Werte:

- Temperatur
- Speicherverbrauch
- Neustarts

Eine historische Speicherung soll erst eingeführt werden, wenn ein konkreter Nutzen nachgewiesen ist.

Dabei muss insbesondere die zusätzliche Schreiblast auf der SD-Karte berücksichtigt werden.

---

# 19. Benachrichtigungen

Spätere optionale Erweiterung.

Mögliche Kanäle:

- E-Mail
- Matrix
- Telegram
- Webhook

Beispiele:

```text
⚠ Pi-hole DNS ausgefallen
⚠ Zertifikat läuft bald ab
⚠ Dienst nicht erreichbar
```

Benachrichtigungen sind ausdrücklich kein Bestandteil der nächsten Dashboard-Version.

---

# 20. Technische Zielarchitektur

Aktuell:

```text
status.cgi
```

Später eventuell:

```text
/opt/otterpi/

checks/
    hardware.sh
    network.sh
    services.sh
    security.sh
    ports.sh
    certificates.sh
```

Das CGI würde die einzelnen Checks aufrufen und deren Ergebnisse darstellen.

Diese Struktur ist eine mögliche Entwicklungsrichtung und noch keine produktive Architektur.

---

# 21. Bewusst nicht vorgesehen

Der aktuelle Projektansatz sieht ausdrücklich nicht vor:

- Kubernetes
- große Containerlandschaft
- schwere Monitoring-Systeme
- unnötige Dashboards
- permanente Historien
- Datenbanken ohne konkreten Nutzen

Das Dashboard soll klein bleiben.

---

# 22. Prioritäten

## Phase 1 – wichtigste Gesundheitschecks

1. Netzwerk-Erreichbarkeit
2. Journal-Fehler
3. Dienst-Laufzeiten
4. Raspberry-Pi-Hardwareinformationen
5. Speicherhardware-Status

## Phase 2 – Komfortinformationen

6. CPU-Prozentanzeige
7. Top-Prozesse
8. Versionsinformationen
9. Netzwerkdetails

## Phase 3 – Komfort und Überwachung

10. Backupstatus
11. Historie
12. Benachrichtigungen

---

# 23. Grundsatz für v4

Das Dashboard soll nicht mit allen Ideen gleichzeitig erweitert werden.

Der aktuelle Charakter:

> Appliance Health Monitor

soll erhalten bleiben.

Die bevorzugte Richtung lautet:

> Wenige, aussagekräftige Werte statt eines vollständigen Monitoring-Systems.

---

# 24. Entwicklungsziel

Die wichtigste Weiterentwicklung ist nicht die Anzahl der angezeigten Werte.

Entscheidend ist die Fähigkeit, einen aktuellen Fehler zu erkennen und verständlich zu erklären.

Beispiel:

Nicht nur:

```text
Pi-hole
🟢 aktiv
```

sondern perspektivisch:

```text
Pi-hole
🟢 Dienst aktiv
🟢 DNS-Antwort funktioniert
```

Damit wird aus einer Statusanzeige zunehmend ein kleines Selbstdiagnose-System.
