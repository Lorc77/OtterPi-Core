# OtterPi Core – Zertifikate und TLS

Stand: August 2026
System: otterpi

## 1. Zweck

Der OtterPi stellt mehrere Webdienste über HTTPS bereit.

Besonders wichtig ist MeshCentral, da die MeshCentral-Agenten auf eine konsistente TLS-Zertifikatskette angewiesen sind.

Das System wurde deshalb so aufgebaut, dass ein Zertifikatswechsel am externen CDN automatisch erkannt und an MeshCentral weitergegeben wird.

## 2. Produktives Zertifikatskonzept

Für MeshCentral existiert ein separater Zertifikats-Endpunkt:

cert.makki.route64.de

MeshCentral verwendet:

certUrl=https://cert.makki.route64.de

Beim Start lädt MeshCentral das Web-Zertifikat von diesem Endpunkt.

Im Journal erscheint unter anderem:

Loaded web certificate from
"https://cert.makki.route64.de"

Danach wird der SHA384-Hash des geladenen Zertifikats protokolliert.

## 3. Warum certUrl verwendet wird

MeshCentral verwaltet das produktive Web-Zertifikat in diesem Aufbau nicht unabhängig vom externen Zertifikats-Endpunkt.

Stattdessen übernimmt MeshCentral das Zertifikat von:

https://cert.makki.route64.de

Dadurch sollen CDN und MeshCentral dasselbe öffentliche Zertifikat verwenden.

Das ist insbesondere wichtig, weil MeshCentral-Agenten Zertifikatsänderungen erkennen können und eine unerwartete Änderung zu Verbindungsproblemen führen kann.

## 4. Zertifikatsproblem der ursprünglichen Architektur

Ursprünglich konnte folgende Situation entstehen:

CDN
|
| neues Zertifikat
v
öffentliches MeshCentral

während gleichzeitig:

MeshCentral
|
| altes Zertifikat
v
lokale Instanz

Dadurch entstand ein Zertifikats-Mismatch.

Mögliche Folge:

- Agent verliert Verbindung
- externer Zugriff funktioniert nicht mehr zuverlässig
- DNS und Routing sind trotzdem korrekt
- Ursache ist ausschließlich die unterschiedliche Zertifikatsversion

## 5. Aktuelle Lösung

Der aktuelle Aufbau verwendet:

CDN-Zertifikat
      |
      v
cert.makki.route64.de
      |
      v
MeshCentral certUrl
      |
      v
geladenes MeshCentral-Zertifikat

Zusätzlich überwacht ein eigener systemd-Dienst die Übereinstimmung.

## 6. Aktueller Zertifikats-Hash

Zum dokumentierten Stand:

c02a613bc7b5538ddb8161d5c76cc983152883ce272ee5f2f7e0d42adee969c4cbda3fc6778c0746040a0e07d6b50c7d

Dieser Wert ist eine Momentaufnahme.

Er darf nicht als dauerhaft gültiger Hash betrachtet werden.

Bei einem regulären Zertifikatswechsel muss sich der Hash ändern.

## 7. Externe Zertifikatsprüfung

Das Zertifikat kann mit OpenSSL geprüft werden.

Prinzip:

echo | openssl s_client \
-connect cert.makki.route64.de:443 \
-servername cert.makki.route64.de \
2>/dev/null | openssl x509 -outform der | sha384sum

Damit wird der SHA384-Hash des extern ausgelieferten Zertifikats ermittelt.

## 8. MeshCentral-Zertifikat prüfen

Der von MeshCentral geladene Hash wird aus dem Journal gelesen.

Beispiel:

journalctl -u meshcentral \
| grep "SHA384 cert hash"

Der dort angezeigte Hash muss mit dem extern ermittelten Zertifikats-Hash übereinstimmen.

## 9. Zertifikatsmonitor

Datei:

/usr/local/sbin/check-mesh-cert.sh

Version:

2.0

Aufgabe:

1. externes Zertifikat abrufen
2. SHA384-Hash bestimmen
3. zuletzt von MeshCentral geladenen Zertifikats-Hash ermitteln
4. beide Werte vergleichen
5. bei Unterschied MeshCentral neu starten
6. nach dem Neustart erneut prüfen
7. Fehlerzustand erkennen

## 10. Statusspeicher

Verzeichnis:

/var/lib/meshcentral-cert-check/

Dort werden unter anderem verwendet:

external_hash
meshcentral_hash
last_status

external_hash:

enthält den Hash des extern ausgelieferten Zertifikats.

meshcentral_hash:

enthält den von MeshCentral geladenen Hash.

last_status:

enthält den letzten Prüfstatus.

Zum dokumentierten Stand:

OK

## 11. systemd

Service:

/etc/systemd/system/meshcentral-cert-check.service

Timer:

/etc/systemd/system/meshcentral-cert-check.timer

Der Timer ist aktiviert und läuft automatisch.

Prüfintervall:

ca. 10 Minuten

Der Service ist ein Type=oneshot-Dienst.

Nach einem erfolgreichen Lauf darf der Service deshalb wieder:

inactive (dead)

anzeigen.

Das ist kein Fehler.

Der Timer bleibt dabei:

active (waiting)

und startet den Service beim nächsten Intervall erneut.

## 12. Automatischer Ablauf

Normalbetrieb:

CDN-Zertifikat
      |
      v
Hash bilden
      |
      v
MeshCentral-Hash lesen
      |
      v
Vergleich
      |
      +---- identisch ----> OK
      |
      +---- unterschiedlich
                    |
                    v
             MeshCentral restart
                    |
                    v
             neues Zertifikat
                    |
                    v
                 Prüfung
                    |
                    v
                    OK

## 13. Test des Fehlerfalls

Der Monitor besitzt einen Simulationsmodus:

sudo /usr/local/sbin/check-mesh-cert.sh --simulate-mismatch

Dabei wird absichtlich ein falscher MeshCentral-Hash simuliert.

Erwartetes Verhalten:

- Mismatch wird erkannt
- MeshCentral wird neu gestartet
- neues Zertifikat wird geladen
- erneute Prüfung wird durchgeführt
- Synchronität wird bestätigt

Der Test wurde erfolgreich durchgeführt.

## 14. Neustartverhalten

Ein Neustart von MeshCentral nach einem Zertifikatswechsel ist normal.

Nach dem Neustart sollte im Journal wieder erscheinen:

Loaded web certificate from
"https://cert.makki.route64.de"

Anschließend sollte der SHA384-Hash dem externen Zertifikat entsprechen.

## 15. Wiederanlauf bei Problemen

Zuerst MeshCentral prüfen:

systemctl status meshcentral

Danach externes Zertifikat prüfen.

Anschließend MeshCentral-Hash prüfen.

Danach den Monitor manuell starten:

sudo systemctl start meshcentral-cert-check.service

Danach erneut prüfen:

systemctl status meshcentral

und:

journalctl -u meshcentral -n 100

## 16. Wichtige DNS-Abhängigkeiten

Folgende Hostnamen sind für den Aufbau relevant:

mesh.makki.route64.de
cert.makki.route64.de

Diese DNS-Einträge sollten nicht ohne vorherige Prüfung geändert werden.

Insbesondere müssen Zertifikats-Endpunkt und tatsächlich ausgeliefertes Zertifikat weiterhin zusammenpassen.

## 17. Sicherheits- und Betriebsgrundsatz

Der Zertifikatsmonitor soll keine Zertifikate selbst erzeugen oder verwalten.

Seine Aufgabe ist ausschließlich:

Erkennen → reagieren → kontrollieren.

Dadurch bleibt die eigentliche Zertifikatsversorgung von der Überwachungslogik getrennt.

## 18. Aktueller Status

MeshCentral:

OK

certUrl:

OK

CDN:

OK

Zertifikatsvergleich:

OK

Automatischer Neustart:

getestet

Recovery:

getestet

systemd Timer:

aktiv

Automatische Kontrolle nach Boot:

getestet

## 19. Ziel

Ein zukünftiger Zertifikatswechsel am CDN soll nicht mehr manuell überwacht werden müssen.

Das System soll selbstständig:

- Änderung erkennen
- MeshCentral neu starten
- neues Zertifikat laden
- Ergebnis kontrollieren

und damit die Agent-Kommunikation stabil halten.

---
Ende der Datei
