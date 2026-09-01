# 🦦 OtterPi – MeshCentral Zertifikats- und CDN-Dokumentation

System: `otterpi`  
Dienst: MeshCentral  
Version: `1.2.4`  
Stand: 04.08.2026

## 1. Zweck

Diese Dokumentation beschreibt das Zertifikatskonzept von MeshCentral sowie die automatische Erkennung und Behebung eines Zertifikatswechsels am CDN-Frontend.

Ziel ist, dass MeshCentral und das öffentlich sichtbare CDN-Zertifikat dauerhaft synchron bleiben.

---

## 2. Ausgangssituation

MeshCentral wird über ein CDN-Frontend öffentlich bereitgestellt.

Das ursprüngliche Problem:

- Das CDN konnte sein öffentliches TLS-Zertifikat wechseln.
- MeshCentral konnte zu diesem Zeitpunkt noch das alte Zertifikat geladen haben.
- MeshCentral-Agenten reagieren auf einen Zertifikatswechsel nicht beliebig tolerant.
- Dadurch konnten Agenten ihre Verbindung verlieren.

Die Ursache lag nicht bei DNS oder Routing, sondern bei einem Zertifikats-Mismatch.

---

## 3. Aktuelle Architektur

Netzwerkweg:

```text
Internet
   |
   v
mesh.makki.route64.de
   |
   v
CDN Frontend
49.13.166.255
   |
   v
Backend / MeshCentral
otterpi
```

MeshCentral selbst läuft intern.

Der öffentliche Zugriff erfolgt über nginx beziehungsweise das CDN-Frontend.

---

## 4. DNS

### MeshCentral

```text
mesh.makki.route64.de
        |
        v
49.13.166.255
```

### Zertifikats-Endpunkt

```text
cert.makki.route64.de
        |
        v
49.13.166.255
```

Prüfung:

```text
dig cert.makki.route64.de +short
```

Ergebnis:

```text
49.13.166.255
```

---

## 5. certUrl

MeshCentral verwendet:

```text
certUrl=https://cert.makki.route64.de
```

Damit lädt MeshCentral sein Web-Zertifikat vom definierten Zertifikats-Endpunkt.

Die Zertifikatsverwaltung erfolgt dadurch nicht separat über ACME innerhalb von MeshCentral.

Vorteile:

- CDN-Zertifikat und MeshCentral-Zertifikat bleiben identisch.
- Es ist keine separate lokale Zertifikatsverwaltung notwendig.
- Agenten sehen konsistent dasselbe Zertifikat.

---

## 6. Zertifikatsprüfung

### CDN-Zertifikat

Prüfung:

```sh
echo | openssl s_client \
-connect cert.makki.route64.de:443 \
-servername cert.makki.route64.de \
2>/dev/null | openssl x509 -outform der | sha384sum
```

Aktueller Hash:

```text
c02a613bc7b5538ddb8161d5c76cc983152883ce272ee5f2f7e0d42adee969c4cbda3fc6778c0746040a0e07d6b50c7d
```

### MeshCentral-Zertifikat

Prüfung:

```sh
journalctl -u meshcentral \
| grep "SHA384 cert hash"
```

Aktueller Hash:

```text
c02a613bc7b5538ddb8161d5c76cc983152883ce272ee5f2f7e0d42adee969c4cbda3fc6778c0746040a0e07d6b50c7d
```

Ergebnis:

CDN und MeshCentral verwenden dasselbe Zertifikat.

---

## 7. Erfolgreicher MeshCentral-Start

Beim Start wird unter anderem protokolliert:

```text
MeshCentral HTTP server running on port 4430, alias port 443.

Loaded web certificate from
"https://cert.makki.route64.de"

host:
"mesh.makki.route64.de"

SHA384 cert hash:
c02a613bc7b5538ddb8161d5c76cc983152883ce272ee5f2f7e0d42adee969c4cbda3fc6778c0746040a0e07d6b50c7d
```

---

## 8. Automatischer Zertifikatsmonitor

Produktiver Monitor:

```text
/usr/local/sbin/check-mesh-cert.sh
```

Version:

`2.0`

Aufgaben:

1. Zertifikat von `cert.makki.route64.de` abrufen.
2. Zertifikats-Hash bestimmen.
3. MeshCentral-Hash aus dem aktuellen Journal ermitteln.
4. Beide Hashes vergleichen.
5. Bei einem Unterschied MeshCentral neu starten.
6. Nach dem Neustart erneut prüfen.
7. Fehler erkennen und entsprechend melden.

---

## 9. Ablauf bei Zertifikatswechsel

Normalbetrieb:

```text
CDN-Zertifikat
      |
      v
Hash ermitteln
      |
      v
MeshCentral-Hash
      |
      v
Vergleich
      |
      +---- identisch ----> OK
      |
      +---- unterschiedlich
                  |
                  v
          MeshCentral Restart
                  |
                  v
          neues Zertifikat laden
                  |
                  v
            erneut prüfen
                  |
                  v
                 OK
```

---

## 10. Statusspeicher

Verzeichnis:

```text
/var/lib/meshcentral-cert-check/
```

Dateien:

### `external_hash`

Enthält den Hash des externen/CDN-Zertifikats.

### `meshcentral_hash`

Enthält den von MeshCentral geladenen Zertifikats-Hash.

### `last_status`

Enthält den letzten Status, beispielsweise:

```text
OK
```

---

## 11. systemd Timer

Timer:

```text
/etc/systemd/system/meshcentral-cert-check.timer
```

Service:

```text
/etc/systemd/system/meshcentral-cert-check.service
```

Status:

```text
enabled
active
```

Prüfintervall:

ca. 10 Minuten

Der Timer ist für den automatischen Start nach einem Systemboot eingerichtet.

---

## 12. Service-Verhalten

Der Zertifikatsprüfservice ist ein:

```text
Type=oneshot
```

Nach einem erfolgreichen Lauf ist der Service selbst:

```text
inactive (dead)
status=0/SUCCESS
```

Das ist korrekt.

Der Timer startet den Service beim nächsten Intervall erneut.

---

## 13. Automatischer Testlauf

Beispiel eines erfolgreichen Timerlaufs:

```text
Aug 04 20:03:10
```

Ergebnis:

```text
OK: CDN und MeshCentral Zertifikat identisch
```

Hash:

```text
c02a613bc7b5538ddb8161d5c76cc983152883ce272ee5f2f7e0d42adee969c4cbda3fc6778c0746040a0e07d6b50c7d
```

---

## 14. Recovery-Test

Testmodus:

```sh
sudo /usr/local/sbin/check-mesh-cert.sh --simulate-mismatch
```

Dabei wird absichtlich ein falscher MeshCentral-Hash simuliert.

Beispiel:

```text
TESTMODUS: simuliere falsches MeshCentral Zertifikat

WARNUNG:
Zertifikat unterschiedlich

CDN:
c02a613...

MeshCentral:
111111111111

Starte MeshCentral neu

OK nach Restart:
Zertifikate synchron
```

Der Recovery-Test war erfolgreich.

---

## 15. Split-DNS

Im LAN wird:

```text
mesh.makki.route64.de
```

direkt auf die lokale MeshCentral-Instanz aufgelöst.

Grund:

- LAN-Geräte müssen nicht über das externe CDN gehen.
- unnötige Schleifen werden vermieden.
- direkter Zugriff im LAN bleibt möglich.
- das Konzept funktioniert auch bei DS-Lite-Umgebungen.

Das Split-DNS-Konzept ist Bestandteil der aktuellen Architektur.

---

## 16. Warum das CDN bestehen bleibt

Das CDN bleibt für externe IPv4-Erreichbarkeit wichtig.

Insbesondere für:

- Netze ohne IPv6
- Universitätsnetze
- Fremdnetze
- DS-Lite-Umgebungen
- sonstige Umgebungen mit eingeschränkter IPv6-Erreichbarkeit

Ein direkter IPv6-Zugriff kann nicht überall vorausgesetzt werden.

---

## 17. Bekannte Stolperfallen

### Zertifikatswechsel

Bei einem Zertifikatswechsel soll nicht manuell eingegriffen werden.

Zuerst prüfen:

```sh
journalctl -u meshcentral-cert-check.service
```

---

### MeshCentral-Neustart

Ein automatischer Neustart nach einem Zertifikatswechsel ist vorgesehen und normal.

Prüfen:

```sh
journalctl -u meshcentral -n 100
```

Erwartet wird unter anderem:

```text
Loaded web certificate from
"https://cert.makki.route64.de"
```

---

### DNS

Folgende Einträge nicht ohne vorherige Prüfung verändern:

```text
mesh.makki.route64.de
cert.makki.route64.de
```

---

## 18. Wiederanlauf nach Fehler

### Schritt 1 – MeshCentral prüfen

```sh
systemctl status meshcentral
```

### Schritt 2 – externes Zertifikat prüfen

```sh
echo | openssl s_client \
-connect cert.makki.route64.de:443 \
-servername cert.makki.route64.de \
2>/dev/null | openssl x509 -outform der | sha384sum
```

### Schritt 3 – MeshCentral-Hash prüfen

```sh
journalctl -u meshcentral \
| grep "SHA384 cert hash"
```

### Schritt 4 – Monitor manuell ausführen

```sh
sudo systemctl start meshcentral-cert-check.service
```

---

## 19. Finaler dokumentierter Zustand

```text
MeshCentral                 OK
CDN                         OK
certUrl                     OK
Split DNS                   OK
IPv4 Zugriff                OK
IPv6 Zugriff                OK
Agent Verbindung            OK
Zertifikatsmonitor          OK
Systemd Timer               OK
Recovery-Test               OK
```

---

## 20. Ergebnis

Die ursprüngliche Ursache:

> CDN-Zertifikat wechselt, MeshCentral verwendet weiterhin das alte Zertifikat.

wurde durch den automatischen Zertifikatsmonitor behoben.

Die aktuelle Lösung:

- verwendet einen stabilen Zertifikats-Endpunkt
- erkennt Zertifikatsänderungen automatisch
- startet MeshCentral bei Bedarf neu
- lädt das neue Zertifikat automatisch
- prüft den Erfolg anschließend erneut
- benötigt bei normalen Zertifikatswechseln keine manuelle Intervention

Status:

**produktionsbereit**
