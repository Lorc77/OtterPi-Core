# OtterPi Core – Netzwerk

Stand: August 2026
System: otterpi
Hardware: Raspberry Pi 4 Model B Rev 1.5

## 1. Netzwerkarchitektur

Der OtterPi ist über Ethernet mit dem lokalen Netzwerk verbunden.

Primäres Interface:

- eth0
- IPv4: 192.168.178.100/24
- Gateway: 192.168.178.1
- Gateway ist die lokale Fritz!Box

WLAN:

- Interface: wlan0
- vorhanden
- aktuell nicht aktiv
- Status: DOWN

Das System verwendet sowohl IPv4 als auch IPv6.

## 2. IPv4

Aktuelle LAN-Adresse:

192.168.178.100/24

Gateway:

192.168.178.1

Die IPv4-Adresse wird innerhalb des Heimnetzes verwendet.

Der externe Zugriff auf ausgewählte Dienste erfolgt nicht durch direktes Freigeben sämtlicher Dienste, sondern über die dafür vorgesehene Infrastruktur.

## 3. IPv6

IPv6 ist auf dem OtterPi aktiv.

Vorhanden sind:

- globale IPv6-Adresse
- ULA-Adresse

IPv6 ermöglicht einen direkten Zugriff aus IPv6-fähigen Netzen.

Da nicht alle externen Netze zuverlässige IPv6-Konnektivität besitzen, bleibt die zusätzliche IPv4-Erreichbarkeit über das CDN für bestimmte Dienste sinnvoll.

## 4. Ethernet

Primäres Netzwerkinterface:

eth0

Das Interface ist produktiv aktiv und stellt die Verbindung zum LAN bereit.

Das Dashboard erkennt den Verbindungsstatus des Interfaces über:

/sys/class/net/eth0/

und über die Kernel-Netzwerkstatusinformationen.

## 5. WLAN

Das Interface wlan0 ist auf dem System vorhanden.

Aktueller Zustand:

DOWN

WLAN wird derzeit nicht als primäre Netzwerkverbindung verwendet.

Das Dashboard berücksichtigt trotzdem den Zustand des Interfaces und kann zwischen folgenden Zuständen unterscheiden:

- verbunden
- nicht verbunden
- blockiert
- deaktiviert
- nicht vorhanden

## 6. DNS

Auf dem OtterPi läuft Pi-hole.

Pi-hole FTL stellt den zentralen DNS-Dienst für das LAN bereit.

DNS:

* TCP/UDP Port 53
* IPv4 und IPv6
* primär LAN-intern

Pi-hole verwendet Quad9 als externe Upstream-Resolver:

* `9.9.9.9`
* `149.112.112.112`
* `2620:fe::fe`
* `2620:fe::9`

Die verwendeten Quad9-Endpunkte entsprechen der gefilterten DNSSEC-Konfiguration ohne ECS.

Pi-hole selbst ist aktuell konfiguriert mit:

* DNSSEC: deaktiviert
* EDNS0 ECS: deaktiviert
* Query Logging: deaktiviert

Die Clients verwenden Pi-hole als DNS-Server.

Die DNS-Funktion wurde praktisch verifiziert:

* externe Namensauflösung funktioniert
* lokale Auflösung von `pi.hole` funktioniert
* IPv4 und IPv6 funktionieren
* eine bekannte Testdomain wird durch Pi-hole blockiert

Das Pi-hole-Webinterface läuft aktuell auf:

`Port 8080`

### Unbound

Unbound ist derzeit nicht installiert.

Eine lokale rekursive DNS-Auflösung mit Unbound wurde geprüft, aber zugunsten der einfacheren Architektur mit Quad9 als Upstream zunächst nicht umgesetzt.

Die Entscheidung kann bei späteren Anforderungen erneut überprüft werden.

## 7. Öffentliche Erreichbarkeit

Produktiv öffentlich erreichbar sind derzeit grundsätzlich nur:

- TCP 80
- TCP 443

Diese Ports werden durch nginx bereitgestellt.

Nicht öffentlich erreichbar sind unter anderem:

- TCP 22
- TCP 53
- TCP 1024
- TCP 4430
- TCP 4433

MeshCentral läuft intern und wird über nginx beziehungsweise die externe CDN-Struktur bereitgestellt.

## 8. nginx

nginx ist der zentrale Webserver und Reverse Proxy.

Öffentliche HTTP/HTTPS-Anfragen erreichen nginx.

nginx übernimmt unter anderem:

- HTTPS
- Reverse Proxy zu MeshCentral
- Bereitstellung lokaler Webinhalte
- virtuelle Hosts für verschiedene OtterPi-Dienste

MeshCentral selbst wird nicht direkt über seinen internen Port aus dem Internet veröffentlicht.

## 9. MeshCentral-Netzwerk

MeshCentral verwendet intern:

TCP 4430

Intel AMT verwendet:

TCP 4433

Zusätzlich existiert:

TCP 1024

für den MeshCentral-internen HTTP-Redirect.

Extern wird MeshCentral über nginx beziehungsweise den vorgesehenen CDN-Endpunkt bereitgestellt.

Hostname:

mesh.makki.route64.de

## 10. CDN

Für MeshCentral existiert eine vorgeschaltete CDN-Struktur.

Aktuell:

mesh.makki.route64.de
        |
        v
CDN
        |
        v
OtterPi / MeshCentral

Das CDN stellt insbesondere die IPv4-Erreichbarkeit für externe Netze sicher.

Dies ist relevant für:

- IPv4-only Netze
- DS-Lite-Umgebungen
- Universitätsnetze
- Fremdnetze
- Netze mit eingeschränkter IPv6-Unterstützung

## 11. Zertifikats-Endpunkt

Für MeshCentral existiert zusätzlich:

cert.makki.route64.de

Dieser Hostname dient als stabiler Zertifikats-Endpunkt für MeshCentral.

MeshCentral verwendet:

certUrl=https://cert.makki.route64.de

Damit kann MeshCentral das Zertifikat des vorgesehenen Endpunkts übernehmen.

## 12. Split-DNS

Für MeshCentral existiert eine interne DNS-Auflösung.

Innerhalb des LANs wird:

mesh.makki.route64.de

direkt auf die lokale MeshCentral-Instanz beziehungsweise den vorgesehenen internen Pfad aufgelöst.

Dadurch wird vermieden, dass interne Geräte unnötig über das externe CDN gehen.

Vorteile:

- kürzerer Netzwerkweg
- kein unnötiger Umweg über das Internet
- funktioniert auch bei DS-Lite
- lokale Geräte erreichen MeshCentral direkt

Die externe DNS-Konfiguration bleibt davon getrennt.

## 13. DynDNS

Für die externe Erreichbarkeit wird ein DynDNS-Update verwendet.

Aktueller Mechanismus:

ipv64.net

Das Update wird regelmäßig per Cron ausgeführt.

Der aktuelle Cron-Eintrag folgt dem Prinzip:

0 * * * * curl -sSL "https://ipv64.net/nic/update?key=...&domain=makki.route64.de" >/dev/null 2>&1

Die Ausgabe wird vollständig verworfen.

Dadurch entstehen keine zusätzlichen Logdateien und die Schreiblast auf dem Speichermedium bleibt minimal.

Der tatsächliche API-Key gehört nicht in die Projektdokumentation oder in ein öffentliches Repository.

## 14. Aktuelle Listener

Zum dokumentierten Stand existieren unter anderem folgende Listener:

22     SSH
53     Pi-hole DNS
80     nginx HTTP
443    nginx HTTPS
8080   Pi-hole Webinterface
1024   MeshCentral Redirect
4430   MeshCentral
4433   MeshCentral Intel AMT
16989  MeshCentral Agent

Die interne beziehungsweise externe Erreichbarkeit der einzelnen Ports ist getrennt zu betrachten.

Ein Listener auf dem System bedeutet nicht automatisch, dass dieser Port aus dem Internet erreichbar ist.

## 15. Firewall

Auf dem OtterPi ist derzeit keine lokale Firewall wie ufw installiert.

Aktuelle Entscheidung:

Keine zusätzliche Host-Firewall.

Begründung:

- Fritz!Box übernimmt die Edge-Firewall
- die Dienststruktur befindet sich noch im Ausbau
- zunächst soll die vollständige Dienststruktur dokumentiert werden
- zusätzliche Firewall-Regeln sollen erst nach vollständiger Aufnahme der tatsächlich benötigten Dienste eingeführt werden

Eine spätere lokale Firewall ist ausdrücklich möglich.

## 16. Netzwerkphilosophie

Das Netzwerkdesign folgt dem Grundprinzip:

So wenig öffentliche Angriffsfläche wie möglich.

Dienste sollen grundsätzlich intern bleiben, wenn keine externe Erreichbarkeit erforderlich ist.

Öffentlich:

- HTTP/HTTPS über nginx
- gezielt veröffentlichte Webdienste

Intern:

- SSH
- Pi-hole DNS
- MeshCentral Backend
- Intel AMT
- interne Verwaltungsports

## 17. Geplante Erweiterung des Dashboards

Das Status Dashboard soll künftig nicht nur die konfigurierten Netzwerkdaten anzeigen, sondern aktiv prüfen:

- Gateway-Erreichbarkeit
- DNS-Funktion
- optionale externe Erreichbarkeit
- Zustand von eth0
- Zustand von wlan0
- erwartete offene Ports
- unerwartete Listener

Geplante Darstellung:

🌐 Netzwerkprüfung

Gateway
🟢 erreichbar

DNS
🟢 funktioniert

Internet
🟢 erreichbar

Die Prüfungen sollen ausschließlich zur Laufzeit erfolgen.

Eine permanente Speicherung von Messwerten ist nicht vorgesehen.

## 18. Zielzustand

Das Netzwerk des OtterPi soll weiterhin:

- übersichtlich
- minimal
- nachvollziehbar
- wartbar
- möglichst wenig öffentlich exponiert

bleiben.

Das Dashboard soll daraus keinen vollständigen Netzwerkmonitor machen.

Es soll lediglich erkennen:

"Kann der OtterPi aktuell so kommunizieren, wie er soll?"

---
Ende der Datei
