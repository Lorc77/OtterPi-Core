# OtterPi-Core – Sicherheit und Zugriff

**Projekt:** Makki Heimserver / OtterPi  
**System:** `otterpi`  
**Stand:** August 2026  
**Dokument:** Sicherheit und Zugriff  
**Status:** Dokumentation des aktuellen Produktivstands

---

## 1. Ziel

Der OtterPi ist ein privater Heimserver.

Das Sicherheitskonzept verfolgt deshalb einen einfachen Ansatz:

- möglichst wenige öffentlich erreichbare Dienste
- klare Trennung zwischen Internet und LAN
- keine unnötigen offenen Ports
- bestehende Dienste nur dort veröffentlichen, wo es erforderlich ist
- Änderungen nachvollziehbar dokumentieren

Der Server soll kein möglichst komplexes Sicherheitssystem darstellen, sondern eine überschaubare und wartbare Infrastruktur bleiben.

---

## 2. Öffentliche Erreichbarkeit

Öffentlich erreichbar sind derzeit ausschließlich:

```text
TCP 80
TCP 443
```

Diese Ports werden von Nginx verwendet.

Nginx dient als öffentlicher Einstiegspunkt für die Webdienste.

---

## 3. Nicht öffentlich erreichbare Ports

Folgende Ports sind nicht direkt aus dem Internet erreichbar:

```text
22
53
1024
4430
4433
```

Bedeutung:

```text
22    SSH
53    Pi-hole DNS
1024  MeshCentral HTTP Redirect
4430  MeshCentral internes HTTP
4433  Intel AMT
```

MeshCentral wird nicht direkt über seinen internen Port veröffentlicht.

---

## 4. Nginx als Reverse Proxy

Der öffentliche HTTPS-Zugriff auf MeshCentral erfolgt über Nginx.

Vereinfacht:

```text
Internet
   |
   v
TCP 443
   |
   v
Nginx
   |
   v
MeshCentral :4430
```

Damit bleibt MeshCentral selbst vom öffentlichen Netzwerkzugriff getrennt.

Der öffentliche Hostname ist:

```text
mesh.makki.route64.de
```

---

## 5. MeshCentral

MeshCentral läuft im Hybridbetrieb:

```text
LAN + WAN
```

Interner Backend-Port:

```text
4430
```

Intel-AMT:

```text
4433
```

Zusätzlich existiert der MeshCentral-Redirect-Port:

```text
1024
```

Diese Ports sind nicht als öffentliche Internet-Ports vorgesehen.

---

## 6. SSH

SSH läuft derzeit auf:

```text
TCP 22
```

Der Dienst ist aktiv.

Aktuelle relevante Einstellungen:

```text
PermitRootLogin without-password
PasswordAuthentication yes
PubkeyAuthentication yes
MaxAuthTries 6
```

Der SSH-Zugang ist damit aktuell noch nicht vollständig gehärtet.

---

## 7. Bewertung des aktuellen SSH-Zustands

Die Einstellung:

```text
PasswordAuthentication yes
```

bedeutet, dass grundsätzlich eine Anmeldung per Passwort möglich ist.

Für einen langfristigen Produktionsbetrieb wäre eine spätere Härtung sinnvoll.

Mögliche Zielkonfiguration:

```text
PasswordAuthentication no
PubkeyAuthentication yes
```

Dabei darf die Änderung erst erfolgen, wenn ein funktionierender Schlüsselzugang getestet wurde.

Wichtig:

> SSH niemals abschalten oder Passwortauthentifizierung deaktivieren, bevor ein alternativer administrativer Zugang erfolgreich getestet wurde.

---

## 8. Root-Login

Aktuell:

```text
PermitRootLogin without-password
```

Damit ist kein klassischer Root-Login per Passwort vorgesehen.

Die genaue Bedeutung hängt von der verwendeten OpenSSH-Version und den weiteren SSH-Einstellungen ab.

Eine spätere explizite Härtung kann sinnvoll sein.

---

## 9. Lokale Firewall

Auf dem OtterPi ist derzeit keine lokale Firewall installiert.

Insbesondere:

```text
ufw
```

ist nicht vorhanden.

Dies ist eine bewusste Entscheidung für den aktuellen Systemstand.

---

## 10. Warum derzeit keine Host-Firewall

Die aktuelle Architektur verwendet die Fritz!Box als Edge-Firewall.

Der OtterPi befindet sich im privaten LAN.

Die Entscheidung gegen eine zusätzliche Host-Firewall wurde getroffen, weil:

- die Netzwerkarchitektur zunächst vollständig erfasst werden soll
- weitere Dienste noch geplant sind
- keine unnötige zusätzliche Komplexität eingeführt werden soll
- die tatsächliche Portstruktur zunächst dokumentiert wird

Das bedeutet nicht, dass eine lokale Firewall grundsätzlich unerwünscht ist.

Sie bleibt eine mögliche spätere Ausbaustufe.

---

## 11. Offene Ports

Aktuell relevante Listener:

```text
22       SSH
53       Pi-hole DNS
80       Nginx HTTP
443      Nginx HTTPS
8080     Pi-hole Webinterface
4430     MeshCentral
4433     MeshCentral AMT
1024     MeshCentral Redirect
16989    MeshCentral Agent
```

Diese Liste beschreibt lokale Listener.

Sie darf nicht automatisch mit öffentlich erreichbaren Ports gleichgesetzt werden.

---

## 12. Unterschied zwischen Listener und Internetzugriff

Ein Dienst kann lokal auf einem Port lauschen, ohne dass dieser Port aus dem Internet erreichbar ist.

Beispiel:

```text
MeshCentral :4430
```

Der Port ist auf dem Raspberry Pi aktiv.

Der öffentliche Zugriff erfolgt jedoch über:

```text
Nginx :443
```

Deshalb ist die tatsächliche Angriffsfläche kleiner als die reine Liste aller lokalen Listener vermuten lässt.

---

## 13. Pi-hole

Pi-hole FTL läuft lokal auf dem OtterPi.

DNS:

```text
TCP/UDP 53
```

Webinterface:

```text
TCP 8080
```

Pi-hole ist ein lokaler Netzwerkdienst und soll nicht als öffentlicher Internetdienst betrieben werden.

---

## 14. Port 8080

Das Pi-hole-Webinterface verwendet:

```text
8080
```

Dieser Port ist nicht als öffentlicher Webzugang vorgesehen.

Der Zugriff erfolgt aus dem LAN.

---

## 15. Nginx

Nginx ist der öffentliche Webserver.

Öffentliche Ports:

```text
80
443
```

Nginx übernimmt insbesondere:

- HTTP
- HTTPS
- Reverse Proxy
- Weiterleitung an interne Dienste
- Bereitstellung des Service-Portals
- Bereitstellung der Statusseite

---

## 16. Öffentliche DNS-Namen

Aktuell relevante DNS-Namen:

```text
makki.route64.de
mesh.makki.route64.de
cert.makki.route64.de
status.makki.route64.de
pihole.makki.route64.de
```

Nicht jeder dieser Namen muss öffentlich aus jedem Netzwerk erreichbar sein.

Insbesondere Status-Dashboard und Pi-hole sind als LAN-Dienste vorgesehen.

---

## 17. Split-DNS

Für MeshCentral existiert eine interne DNS-Auflösung.

Intern kann:

```text
mesh.makki.route64.de
```

direkt auf die lokale MeshCentral-Instanz zeigen.

Extern erfolgt der Zugriff über das CDN beziehungsweise den öffentlichen Netzwerkpfad.

Ziel:

```text
LAN
 ↓
lokale MeshCentral-Instanz

WAN
 ↓
CDN
 ↓
MeshCentral
```

---

## 18. Grund für Split-DNS

Split-DNS verhindert, dass interne Clients für einen lokalen Dienst unnötig den externen Weg nehmen.

Vorteile:

- kein unnötiger Umweg
- geringere Abhängigkeit vom externen Pfad
- direkter LAN-Zugriff
- bessere Funktion in bestimmten DS-Lite-Szenarien
- geringere externe Netzwerklast

---

## 19. CDN und IPv4

Das CDN bleibt Bestandteil der Architektur.

Grund:

Nicht alle externen Netze verfügen über zuverlässige native IPv6-Konnektivität.

Das betrifft beispielsweise:

- IPv4-only-Netze
- bestimmte Fremdnetze
- Universitätsnetzwerke
- DS-Lite-Umgebungen

Der direkte IPv6-Zugriff auf den Heimanschluss ist daher nicht als alleiniger externer Zugangsweg ausreichend.

---

## 20. Zertifikatsicherheit

MeshCentral verwendet:

```text
https://cert.makki.route64.de
```

als Zertifikatsquelle.

Der Zertifikatsmonitor vergleicht regelmäßig:

```text
CDN-Zertifikat
        ↓
MeshCentral-Zertifikat
```

Bei einem Unterschied wird MeshCentral automatisch neu gestartet.

Damit soll verhindert werden, dass Agenten wegen eines Zertifikatswechsels dauerhaft die Verbindung verlieren.

---

## 21. Zertifikatsmonitor

Der Monitor befindet sich unter:

```text
/usr/local/sbin/check-mesh-cert.sh
```

Systemd:

```text
/etc/systemd/system/meshcentral-cert-check.service
/etc/systemd/system/meshcentral-cert-check.timer
```

Der Timer läuft ungefähr alle:

```text
10 Minuten
```

---

## 22. Zertifikatsüberwachung als Sicherheitskomponente

Der Zertifikatsmonitor ist nicht nur ein Komfortmechanismus.

Er stellt sicher, dass der Zertifikatszustand der externen und internen MeshCentral-Komponente regelmäßig kontrolliert wird.

Dadurch wird ein bekannter Fehlerzustand automatisch erkannt und behoben.

Der Mechanismus wurde bereits mit einem simulierten Zertifikats-Mismatch getestet.

---

## 23. systemd-Dienste

Wichtige systemd-Dienste:

```text
meshcentral
meshcentral-cert-check.service
meshcentral-cert-check.timer
nginx
pihole-FTL
fcgiwrap
ssh
NetworkManager
systemd-timesyncd
```

Der Zertifikatsmonitor besteht bewusst aus einem `oneshot`-Service und einem Timer.

Nach erfolgreichem Lauf darf der Service daher:

```text
inactive (dead)
```

anzeigen.

Der Timer bleibt:

```text
active (waiting)
```

---

## 24. rpcbind

Auf dem System ist:

```text
rpcbind 1.2.7-1
```

installiert.

Der Dienst ist derzeit aktiv und verwendet:

```text
TCP/UDP 111
```

Aktuell wurden keine registrierten RPC-Dienste außer dem Portmapper festgestellt.

Eine Deaktivierung wurde noch nicht vorgenommen.

---

## 25. Bewertung von rpcbind

rpcbind ist derzeit ein zu prüfender Dienst.

Vor einer Deaktivierung muss festgestellt werden, ob irgendein vorhandener Dienst davon abhängig ist.

Grundregel:

> Nicht benötigte Netzwerkdienste sollten langfristig entfernt oder deaktiviert werden.

Aber:

> Ein Dienst wird erst deaktiviert, nachdem seine Abhängigkeiten geprüft wurden.

---

## 26. NetworkManager

NetworkManager verwaltet die Netzwerkverbindungen des Systems.

Der aktive Netzwerkadapter ist:

```text
eth0
```

IPv4:

```text
192.168.178.100/24
```

Gateway:

```text
192.168.178.1
```

IPv6 ist ebenfalls aktiviert.

---

## 27. WLAN

Das Interface:

```text
wlan0
```

ist vorhanden.

Zum dokumentierten Zeitpunkt war es:

```text
DOWN
```

Es wird derzeit nicht für die produktive Netzwerkverbindung benötigt.

---

## 28. Administrativer Zugang

Der primäre administrative Zugang erfolgt derzeit über SSH.

Der öffentliche MeshCentral-Zugang ist nicht als Ersatz für die lokale Systemadministration zu betrachten.

Das bedeutet:

```text
MeshCentral
    = Fernwartung von verwalteten Geräten

SSH
    = Administration des OtterPi selbst
```

Diese Trennung sollte beibehalten werden.

---

## 29. Sicherheitsprinzip für das Service-Portal

Das Service-Portal dient primär als zentrale Übersicht.

Es enthält Verweise auf:

- MeshCentral
- ZOOLOGY-Observer
- WeatherHub-Observer
- OtterPi Status
- Pi-hole
- weitere Projekte

Das Portal selbst ist kein Administrationssystem.

Administrative Funktionen sollen nicht unnötig in das Portal eingebaut werden.

---

## 30. Status-Dashboard

Das Status-Dashboard befindet sich unter:

```text
/var/www/status/cgi-bin/status.cgi
```

Es ist derzeit als:

```text
LAN only
```

vorgesehen.

Es zeigt Systeminformationen und Diagnosewerte.

Es besitzt keine Benutzerverwaltung und keine Änderungsfunktionen.

---

## 31. Sicherheitsprinzip des Dashboards

Das Dashboard soll möglichst ausschließlich lesend arbeiten.

Es soll:

- Informationen abfragen
- Zustände bewerten
- Ergebnisse anzeigen

Es soll nicht:

- Systemkonfiguration verändern
- Dienste administrieren
- Dateien bearbeiten
- Benutzer verwalten
- Befehle über Webparameter ausführen

Damit bleibt die CGI-Anwendung möglichst klein und kontrollierbar.

---

## 32. CGI und Privilegien

Das Dashboard wird über:

```text
fcgiwrap
```

ausgeführt.

Die CGI-Anwendung sollte keine unnötigen Root-Rechte besitzen.

Falls für einzelne Prüfungen privilegierte Informationen erforderlich sind, sollte dies gezielt und restriktiv gelöst werden.

Ein pauschales:

```text
CGI als root
```

ist ausdrücklich nicht das gewünschte Ziel.

---

## 33. Sicherheitschecks für v3.4

Für die geplante nächste Dashboard-Version sind unter anderem folgende Prüfungen vorgesehen:

```text
SSH aktiv?
Root-Login sinnvoll konfiguriert?
Passwortauthentifizierung aktiv?
Lokale Firewall vorhanden?
Offene Ports?
Unerwartete Netzwerkdienste?
```

Diese Prüfungen sollen zunächst nur Informationen liefern.

Automatische Änderungen sollen daraus nicht entstehen.

---

## 34. Update-Status

Ein späterer Sicherheitscheck kann zusätzlich prüfen:

```text
Sind Systemupdates verfügbar?
```

Auch hier gilt:

Das Dashboard soll zunächst nur anzeigen:

```text
System aktuell
```

oder beispielsweise:

```text
Updates verfügbar
```

Eine automatische Installation über das Webinterface ist nicht vorgesehen.

---

## 35. Aktuelle Sicherheitsbewertung

Der aktuelle Zustand lässt sich grob so zusammenfassen:

```text
Öffentliche Webports       OK
MeshCentral hinter Nginx   OK
Interne Mesh-Ports         nicht öffentlich
Pi-hole                    LAN only
Status-Dashboard           LAN only
SSH                        aktiv, noch nicht vollständig gehärtet
Lokale Firewall            nicht vorhanden
rpcbind                    noch zu prüfen
Zertifikatsüberwachung     aktiv
```

---

## 36. Bekannte offene Punkte

Folgende Punkte bleiben bewusst für eine spätere Sicherheitsausbaustufe offen:

1. SSH weiter härten.
2. Passwortauthentifizierung nach erfolgreichem Schlüsseltest deaktivieren.
3. rpcbind-Abhängigkeiten prüfen.
4. Nicht benötigte Dienste identifizieren.
5. Erwartete und tatsächlich offene Ports vergleichen.
6. Optional lokale Firewall einführen.
7. Update-Status automatisiert anzeigen.

---

## 37. Grundsatz für zukünftige Änderungen

Sicherheitsänderungen sollen immer schrittweise erfolgen.

Vor einer Änderung:

```text
aktuellen Zustand dokumentieren
        ↓
Konfiguration sichern
        ↓
Änderung durchführen
        ↓
Dienst prüfen
        ↓
Zugriff testen
        ↓
Fehlerfall berücksichtigen
```

Insbesondere Änderungen an:

- SSH
- Nginx
- Netzwerk
- Firewall
- DNS
- MeshCentral

dürfen nicht gleichzeitig mit mehreren anderen grundlegenden Änderungen durchgeführt werden.

---

## 38. Zielbild

Das langfristige Ziel ist kein maximal abgesichertes, komplexes Enterprise-System.

Das Ziel ist:

```text
kleine Angriffsfläche
        +
wenige Dienste
        +
klare Netzwerkgrenzen
        +
regelmäßige Selbstprüfung
        +
gute Dokumentation
```

Damit bleibt der OtterPi auch nach Jahren nachvollziehbar und wartbar.

---

## 39. Zusammenfassung

Der OtterPi besitzt derzeit eine bewusst überschaubare Netzwerk- und Sicherheitsarchitektur.

Öffentlich notwendig sind im Wesentlichen:

```text
80/tcp
443/tcp
```

Die eigentlichen internen Dienste bleiben hinter der Netzwerkgrenze beziehungsweise hinter Nginx.

Besonders wichtig sind:

- MeshCentral nur über Nginx öffentlich
- interne MeshCentral-Ports nicht veröffentlichen
- Pi-hole nicht öffentlich anbieten
- Status-Dashboard LAN-only
- Zertifikatswechsel automatisch überwachen
- SSH später gezielt härten
- unnötige Netzwerkdienste prüfen

Der nächste sinnvolle Schritt besteht daher nicht in einer großen Sicherheitsplattform, sondern in kleinen, überprüfbaren Verbesserungen.

**Grundsatz:**

> Sicherheit durch kleine Angriffsfläche, klare Grenzen und nachvollziehbare Konfiguration. 🦦
