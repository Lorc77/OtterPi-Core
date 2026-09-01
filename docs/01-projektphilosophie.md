# 🦦 OtterPi – Projektphilosophie

Stand: August 2026

## 1. Grundidee

Der Makki-Heimserver ist keine Spielwiese für möglichst viele Dienste.

Er ist eine bewusst klein gehaltene, private Infrastruktur mit dem Ziel, möglichst zuverlässig, wartbar und ressourcenschonend zu funktionieren.

Der Server soll vor allem:

- stabil laufen
- wenig Wartungsaufwand verursachen
- möglichst wenig dauerhaft auf die SD-Karte schreiben
- übersichtlich bleiben
- leicht diagnostizierbar sein
- bei Problemen nachvollziehbar bleiben

## 2. Grundprinzipien

### Möglichst wenig Komplexität

Jeder zusätzliche Dienst erhöht:

- Wartungsaufwand
- Fehlerquellen
- Ressourcenverbrauch
- potenzielle Angriffsfläche

Daher werden neue Komponenten nur eingesetzt, wenn sie einen konkreten Nutzen haben.

### Keine unnötigen Hintergrunddienste

Dienste sollen einen klaren Zweck erfüllen.

Insbesondere sollen keine zusätzlichen Monitoring- oder Datenbankdienste eingeführt werden, nur weil sie technisch möglich wären.

### SD-Karte schonen

Der Raspberry Pi verwendet eine SD-Karte als Massenspeicher.

Daher wird dauerhafte Schreiblast bewusst reduziert.

Aktuell eingesetzte Maßnahmen:

- ext4 mit `noatime`
- reduziertes Journald
- deaktiviertes Pi-hole Query Logging
- Logrotate
- fstrim
- DynDNS ohne lokale Logdateien

### Keine dauerhaften Datenbanken ohne echten Nutzen

Das Status-Dashboard benötigt keine historische Datenhaltung.

Es soll den aktuellen Zustand des Systems ermitteln und anzeigen.

Daher sind aktuell keine Komponenten wie:

- InfluxDB
- Grafana
- Prometheus
- permanente Messdatenbanken

vorgesehen.

## 3. Weboberflächen

Die Webstruktur wird bewusst in verschiedene Aufgabenbereiche getrennt.

### Zugang / Portal

Das Service-Portal dient als zentrale Einstiegseite.

Pfad:

`/var/www/makki/`

Es enthält Links zu den verschiedenen Diensten.

### Status / Diagnose

Das Status-Dashboard dient ausschließlich zur Zustands- und Diagnoseanzeige.

Produktiver Pfad:

`/var/www/status/cgi-bin/status.cgi`

Aktuelle Version:

`v3.3`

### Eigentliche Dienste

Die eigentlichen Dienste bleiben von Portal und Statusanzeige getrennt.

Beispiele:

- MeshCentral
- Pi-hole
- nginx

## 4. Charakter des Status-Dashboards

Das Dashboard soll kein vollständiges Enterprise-Monitoring-System werden.

Sein Charakter ist:

> Appliance Health Monitor

Es soll auf einen Blick beantworten:

- Läuft das System?
- Gibt es offensichtliche Hardwareprobleme?
- Sind Ressourcen knapp?
- Sind wichtige Dienste aktiv?
- Funktioniert das Netzwerk?
- Gibt es einen aktuellen Fehler?

Die Anzeige soll dabei möglichst verständlich bleiben.

## 5. Aktuelle Entwicklungsidee

Die nächste Entwicklungsrichtung ist nicht:

> Mehr Messwerte.

Sondern:

> Mehr Diagnosefähigkeit.

Das Dashboard soll schrittweise von einer Zustandsanzeige zu einem einfachen Selbstdiagnose-System werden.

Beispiel:

Nicht nur:

`nginx – aktiv`

sondern perspektivisch:

`nginx – aktiv`  
`HTTPS – erreichbar`

Damit wird zwischen:

- Prozess läuft
- Dienst funktioniert tatsächlich

unterschieden.

## 6. Keine historische Datensammlung

Das Dashboard soll grundsätzlich mit Live-Daten arbeiten.

Es werden keine permanenten Messwerte gespeichert.

Eine spätere Historie wäre nur dann sinnvoll, wenn ein konkreter Diagnosevorteil entsteht.

Auch dann soll zuerst geprüft werden, ob sich dies ohne unnötige Schreiblast lösen lässt.

## 7. Sicherheitsprinzip

Das System soll möglichst wenig öffentlich exponiert werden.

Öffentlich notwendige Dienste werden über nginx bereitgestellt.

Interne Verwaltungs- und Backend-Ports bleiben intern.

MeshCentral läuft hinter nginx.

## 8. Änderungsprinzip

Vor größeren Änderungen wird ein vollständiger Snapshot des funktionierenden Systems erstellt.

Damit existiert jederzeit ein klarer Rückkehrpunkt.

Neue Funktionen sollen möglichst additiv implementiert werden.

Bestehende produktive Funktionen sollen nicht unnötig verändert werden.

## 9. Entwicklungsphilosophie

Neue Funktionen werden bevorzugt:

- klein
- nachvollziehbar
- lokal
- wartbar
- ressourcenschonend
- ohne zusätzliche permanente Dienste

umgesetzt.

Der Server soll auch nach Jahren noch verständlich sein.

## 10. Langfristiges Ziel

OtterPi soll kein möglichst großer Server werden.

Das Ziel ist ein kleiner, zuverlässiger Heimserver, bei dem jederzeit nachvollziehbar ist:

> Was läuft?
>
> Warum läuft es?
>
> Ist es gesund?
>
> Und wenn nicht: Wo liegt das Problem?

🦦
