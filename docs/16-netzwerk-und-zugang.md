# OtterPi-Core – Netzwerk und Zugang

**Dokument:** 16-netzwerk-und-zugang.md  
**Projekt:** OtterPi-Core  
**System:** otterpi  
**Stand:** August 2026  
**Status:** produktiv

---

## 1. Zweck

Dieses Dokument beschreibt die Netzwerk- und Zugangsarchitektur des OtterPi.

Dabei wird zwischen folgenden Bereichen unterschieden:

- lokales LAN
- IPv4
- IPv6
- externe Erreichbarkeit
- CDN-Zugang
- Reverse Proxy
- lokale Dienste
- öffentlich erreichbare Ports
- ausschließlich intern erreichbare Ports

Ziel ist eine klare Trennung zwischen öffentlichen und internen Diensten.

---

## 2. Lokales Netzwerk

Der OtterPi befindet sich im privaten LAN hinter einer Fritz!Box.

Aktuelle IPv4-Konfiguration:

```text
IP-Adresse:
192.168.178.100/24

Gateway:
192.168.178.1
```

Primäres Netzwerkinterface:

```text
eth0
```

Ethernet ist der derzeit verwendete Netzwerkweg.

---

## 3. WLAN

Das WLAN-Interface ist vorhanden:

```text
wlan0
```

Zum dokumentierten Snapshot-Zeitpunkt:

```text
Status:
DOWN
```

WLAN ist damit nicht der primäre Netzwerkweg.

Die Infrastruktur ist auf Ethernet ausgelegt.

---

## 4. IPv6

IPv6 ist aktiviert.

Vorhanden sind:

- globale IPv6-Adressen
- ULA-Adressen

IPv6 ermöglicht grundsätzlich eine direkte externe Erreichbarkeit des Systems.

Die Architektur verlässt sich jedoch nicht ausschließlich auf IPv6.

---

## 5. Warum IPv4 weiterhin benötigt wird

Nicht jedes externe Netzwerk bietet zuverlässige IPv6-Konnektivität.

Relevant sind beispielsweise:

- IPv4-only-Netze
- DS-Lite-Umgebungen
- öffentliche WLANs
- Universitätsnetze
- Fremdnetze
- ältere oder eingeschränkte Providerzugänge

Deshalb bleibt der IPv4-Zugang über das CDN Bestandteil der Architektur.

---

## 6. Externe DNS-Struktur

Wichtige öffentliche Namen:

```text
makki.route64.de
mesh.makki.route64.de
cert.makki.route64.de
```

Der externe MeshCentral-Hostname ist:

```text
mesh.makki.route64.de
```

Der Zertifikats-Endpunkt ist:

```text
cert.makki.route64.de
```

---

## 7. CDN

Das CDN-Frontend befindet sich aktuell unter:

```text
49.13.166.255
```

Der externe Netzwerkweg für MeshCentral ist:

```text
Internet
   |
   v
mesh.makki.route64.de
   |
   v
CDN
   |
   v
OtterPi / MeshCentral
```

Das CDN stellt dabei die externe Erreichbarkeit bereit.

---

## 8. Zweck des CDN

Das CDN erfüllt insbesondere die Aufgabe, den Dienst auch aus Netzwerken erreichbar zu machen, in denen ein direkter IPv6-Zugriff nicht zuverlässig möglich ist.

Es stellt damit eine zusätzliche Zugangsschicht zwischen Internet und OtterPi dar.

Der CDN-Zugang wird insbesondere für MeshCentral benötigt.

---

## 9. MeshCentral

Der externe MeshCentral-Hostname lautet:

```text
mesh.makki.route64.de
```

Intern läuft MeshCentral auf:

```text
TCP 4430
```

Zusätzlich existieren:

```text
TCP 4433
TCP 1024
```

für MeshCentral-spezifische Funktionen.

Diese Ports sind nicht öffentlich erreichbar.

---

## 10. Reverse Proxy

Der öffentliche HTTPS-Zugang erfolgt über nginx.

Netzwerkweg:

```text
Internet
   |
   v
TCP 443
   |
   v
nginx
   |
   v
MeshCentral :4430
```

MeshCentral wird somit nicht direkt über seinen internen Port aus dem Internet veröffentlicht.

---

## 11. nginx

nginx ist der öffentliche Webserver und Reverse Proxy.

Öffentlich relevante Ports:

```text
TCP 80
TCP 443
```

Port 80 dient dem HTTP-Zugang beziehungsweise der Weiterleitung.

Port 443 stellt den produktiven HTTPS-Zugang bereit.

---

## 12. MeshCentral bleibt hinter nginx

MeshCentral läuft ausschließlich hinter nginx.

Der interne MeshCentral-Webserver lauscht auf:

```text
4430
```

Dieser Port ist nicht als öffentlicher Internet-Port vorgesehen.

Dadurch ist die externe Struktur klar:

```text
Internet
    |
  HTTPS
    |
    v
  nginx
    |
    v
MeshCentral
```

---

## 13. Interne MeshCentral-Ports

Aktuell relevante MeshCentral-Ports:

```text
4430    Webserver intern
4433    Intel AMT intern
1024    HTTP Redirect intern
```

Diese Ports dürfen nicht versehentlich durch eine Änderung der Router- oder Firewall-Konfiguration öffentlich exponiert werden.

---

## 14. MeshCentral Intel AMT

Intel AMT verwendet:

```text
TCP 4433
```

Dieser Port bleibt intern.

Die externe Veröffentlichung erfolgt nicht direkt über diesen Port.

---

## 15. Pi-hole

Pi-hole stellt den lokalen DNS-Dienst bereit.

DNS:

```text
TCP/UDP 53
```

Das Pi-hole-Webinterface verwendet:

```text
TCP 8080
```

Diese Dienste sind für das lokale Netzwerk vorgesehen.

Das Pi-hole-Webinterface wird nicht als öffentlicher Internetdienst betrieben.

---

## 16. SSH

SSH verwendet:

```text
TCP 22
```

SSH ist für Administration vorgesehen.

Der Port ist nicht öffentlich über das Internet erreichbar.

Der aktuelle SSH-Konfigurationsstand ist noch nicht vollständig gehärtet und soll später separat betrachtet werden.

---

## 17. Öffentliche Ports

Nach aktuellem Architekturstand sollen aus dem Internet lediglich die Webports erreichbar sein:

```text
TCP 80
TCP 443
```

Damit ergibt sich:

```text
80    HTTP
443   HTTPS
```

Alle übrigen Dienste bleiben intern.

---

## 18. Nicht öffentlich erreichbare Ports

Aktuell dokumentiert:

```text
22      SSH
53      Pi-hole DNS
1024    MeshCentral Redirect
4430    MeshCentral
4433    Intel AMT
8080    Pi-hole Webinterface
```

Diese Ports sind nicht Bestandteil der öffentlichen Weboberfläche.

---

## 19. Portübersicht

| Port | Dienst | Zugriff |
|---:|---|---|
| 22 | SSH | LAN |
| 53 | Pi-hole DNS | LAN |
| 80 | nginx / HTTP | öffentlich |
| 443 | nginx / HTTPS | öffentlich |
| 8080 | Pi-hole Webinterface | LAN |
| 1024 | MeshCentral Redirect | intern |
| 4430 | MeshCentral | intern |
| 4433 | Intel AMT | intern |
| 16989 | MeshCentral Agent | intern |

Die tatsächliche Listener-Situation soll bei späteren Snapshots erneut geprüft werden.

---

## 20. Split-DNS

Für MeshCentral existiert eine interne DNS-Auflösung.

Intern wird:

```text
mesh.makki.route64.de
```

nicht zwingend über den externen CDN-Weg aufgelöst.

Stattdessen kann die lokale MeshCentral-Instanz direkt erreicht werden.

Vereinfachte Darstellung:

```text
LAN-Gerät
   |
   v
lokale DNS-Auflösung
   |
   v
OtterPi / MeshCentral
```

---

## 21. Warum Split-DNS verwendet wird

Split-DNS vermeidet unnötige Umwege für lokale Clients.

Vorteile:

- LAN-Zugriff bleibt lokal
- kein unnötiger Weg über das CDN
- weniger Abhängigkeit vom externen Zugang
- bessere Funktion bei bestimmten DS-Lite-Szenarien
- lokale Geräte erreichen den Dienst direkt

---

## 22. Externer MeshCentral-Zugang

Von außerhalb des LANs wird weiterhin verwendet:

```text
https://mesh.makki.route64.de
```

Der externe Weg führt über das CDN.

Damit existieren zwei logische Zugangswege:

```text
LAN:
Client
  ↓
Split-DNS
  ↓
OtterPi

WAN:
Client
  ↓
mesh.makki.route64.de
  ↓
CDN
  ↓
OtterPi
```

---

## 23. Zertifikats-Endpunkt

Der Zertifikats-Endpunkt lautet:

```text
https://cert.makki.route64.de
```

Auch dieser Name zeigt aktuell auf das CDN-Frontend.

Die DNS-Auflösung wurde dokumentiert als:

```text
cert.makki.route64.de
    ↓
49.13.166.255
```

---

## 24. Zusammenhang zwischen CDN und MeshCentral-Zertifikat

MeshCentral verwendet:

```text
certUrl=https://cert.makki.route64.de
```

Dadurch lädt MeshCentral das produktive Web-Zertifikat vom definierten Zertifikats-Endpunkt.

Der Zweck besteht darin, sicherzustellen, dass:

```text
CDN-Zertifikat
        =
MeshCentral-Zertifikat
```

bleibt.

Ein Zertifikatswechsel am CDN wird dadurch automatisch erkannt und verarbeitet.

Die vollständige Zertifikatsarchitektur ist in der separaten Dokumentation beschrieben.

---

## 25. Sicherheitsgrenze

Der zentrale Sicherheitsgrundsatz lautet:

> Öffentliche Dienste werden ausschließlich über die dafür vorgesehenen Reverse-Proxy- und CDN-Wege veröffentlicht.

Interne Backend-Ports sollen nicht direkt aus dem Internet erreichbar sein.

Insbesondere:

```text
4430
4433
1024
8080
22
53
```

sind keine öffentlichen Webports.

---

## 26. Lokale Firewall

Zum dokumentierten Stand ist keine zusätzliche lokale Firewall wie `ufw` installiert.

Die Entscheidung wurde bewusst getroffen.

Aktuelle Architektur:

```text
Internet
   |
   v
Fritz!Box / Edge-Firewall
   |
   v
OtterPi
```

Die lokale Firewall soll nicht einfach zusätzlich installiert werden, ohne vorher alle benötigten Dienste und Netzwerkwege vollständig zu erfassen.

---

## 27. Grund für die spätere Firewall-Entscheidung

Der OtterPi soll künftig eventuell weitere Dienste aufnehmen.

Vor einer lokalen Firewall-Konfiguration soll deshalb zunächst eine vollständige Bestandsaufnahme erfolgen.

Dabei sollen mindestens bekannt sein:

- benötigte Ports
- lokale Dienste
- externe Dienste
- LAN-Zugriffe
- IPv4-Zugriffe
- IPv6-Zugriffe
- MeshCentral-Kommunikation
- Pi-hole-Kommunikation
- Dashboard-Zugriff

Erst danach soll entschieden werden, ob eine Host-Firewall einen echten zusätzlichen Nutzen bringt.

---

## 28. Netzwerkphilosophie

Das Netzwerk soll nicht unnötig kompliziert werden.

Grundprinzip:

```text
öffentlich:
    80
    443

intern:
    alles andere
```

Ausnahmen müssen bewusst dokumentiert werden.

---

## 29. Geplante Netzwerkdiagnose

Eine zukünftige Dashboard-Version soll den Netzwerkzustand nicht nur anhand des Interface-Status bewerten.

Geplant sind Prüfungen wie:

```text
Gateway erreichbar?
DNS funktioniert?
Internet erreichbar?
```

Beispiel:

```text
🌐 Netzwerkprüfung

Gateway
🟢 erreichbar

DNS
🟢 funktioniert

Internet
🟢 erreichbar
```

Dabei soll zwischen:

- Interface aktiv
- Netzwerk funktionsfähig
- Internet erreichbar

unterschieden werden.

---

## 30. Geplante Portprüfung

Das Dashboard soll perspektivisch nicht einfach alle offenen Ports anzeigen.

Stattdessen soll eine Liste erwarteter Ports definiert werden.

Beispiel:

```text
22      SSH       LAN only
53      DNS       LAN only
80      HTTP      öffentlich
443     HTTPS     öffentlich
```

Ein unerwarteter Listener könnte anschließend als Warnung angezeigt werden.

Beispiel:

```text
⚠ Unerwarteter Port

8080/tcp
Prozess: ...
```

---

## 31. Zielbild

Die Netzwerkarchitektur soll langfristig einfach lesbar bleiben:

```text
                    Internet
                       |
                       v
                 CDN / DNS
                       |
                       v
                 nginx :443
                       |
                       v
                MeshCentral :4430
                       |
                 +-----+-----+
                 |           |
               Agents      AMT
```

Parallel dazu:

```text
                    LAN
                     |
          +----------+----------+
          |          |          |
        Pi-hole    Dashboard   SSH
          |          |          |
          +----------+----------+
                     |
                   otterpi
```

---

## 32. Aktueller Netzwerkstatus

Zum dokumentierten Stand:

```text
LAN                     OK
eth0                    aktiv
IPv4                    192.168.178.100/24
Gateway                 192.168.178.1
IPv6                    aktiv
WLAN                    vorhanden / DOWN

nginx                   OK
Reverse Proxy           OK
MeshCentral              OK
Split-DNS               OK
CDN                     OK
Externer HTTPS-Zugang   OK
```

---

## 33. Änderungsregel

Änderungen an folgenden Komponenten sollen besonders vorsichtig erfolgen:

```text
mesh.makki.route64.de
cert.makki.route64.de
nginx
DNS
CDN
Fritz!Box-Portfreigaben
MeshCentral-Ports
```

Vor Änderungen an der externen Erreichbarkeit soll möglichst ein aktueller Systemsnapshot vorhanden sein.

---

**OtterPi-Core**

> Intern direkt. Extern gezielt. Öffentlich nur, was öffentlich sein muss. 🦦
