# OtterPi – Zertifikatskonzept

Stand: August 2026

## Zweck

Dieses Dokument beschreibt das produktive TLS- und Zertifikatskonzept des OtterPi-Heimservers.

Das Konzept betrifft insbesondere MeshCentral und dessen vorgeschaltetes CDN.

Ziel ist, dass das Zertifikat, das externe Clients über das CDN sehen, mit dem von MeshCentral verwendeten Zertifikat übereinstimmt.

Dadurch werden Probleme vermieden, bei denen MeshCentral nach einem Zertifikatswechsel am CDN weiterhin ein altes Zertifikat verwendet.

---

## 1. Beteiligte Domains

### MeshCentral

Produktive Adresse:

mesh.makki.route64.de

Diese Adresse wird für den externen Zugriff auf MeshCentral verwendet.

### Zertifikats-Endpunkt

cert.makki.route64.de

Dieser Endpunkt stellt das Zertifikat bereit, das MeshCentral über `certUrl` lädt.

### Service-Portal

makki.route64.de

Diese Domain gehört zum allgemeinen Service-Portal des Heimservers.

---

## 2. Architektur

Der externe Zugriff auf MeshCentral erfolgt über das CDN.

Vereinfacht:

Internet
  |
  v
mesh.makki.route64.de
  |
  v
CDN
  |
  v
Nginx / MeshCentral auf otterpi

MeshCentral selbst läuft nicht direkt öffentlich auf Port 443.

Nginx übernimmt den öffentlichen HTTPS-Zugriff und leitet intern an MeshCentral weiter.

---

## 3. MeshCentral certUrl

MeshCentral verwendet einen externen Zertifikats-Endpunkt:

certUrl=https://cert.makki.route64.de

Beim Start lädt MeshCentral das Web-Zertifikat von diesem Endpunkt.

Im Journal erscheint anschließend unter anderem:

Loaded web certificate from
"https://cert.makki.route64.de"

sowie der SHA384-Hash des geladenen Zertifikats.

---

## 4. Warum certUrl verwendet wird

Das CDN kann sein öffentlich verwendetes TLS-Zertifikat ändern.

Wenn MeshCentral gleichzeitig weiterhin ein älteres Zertifikat verwendet, können Agenten Verbindungsprobleme bekommen.

Der Zertifikats-Endpunkt dient deshalb als gemeinsame Quelle.

Ziel:

CDN-Zertifikat
=
MeshCentral-Zertifikat

Damit wird der Zertifikatswechsel nicht manuell am MeshCentral-Server durchgeführt.

---

## 5. Zertifikatsüberwachung

Zusätzlich existiert ein eigener Zertifikatsmonitor:

/usr/local/sbin/check-mesh-cert.sh

Der Monitor wird regelmäßig über systemd ausgeführt.

Er prüft:

1. Zertifikat von `cert.makki.route64.de` abrufen
2. SHA384-Hash bestimmen
3. zuletzt von MeshCentral geladenen Zertifikats-Hash aus dem Journal ermitteln
4. Hashes vergleichen
5. bei einem Unterschied MeshCentral neu starten
6. nach dem Neustart erneut prüfen

---

## 6. Systemd-Komponenten

Service:

/etc/systemd/system/meshcentral-cert-check.service

Timer:

/etc/systemd/system/meshcentral-cert-check.timer

Der Timer läuft ungefähr alle zehn Minuten.

Der Service ist als `Type=oneshot` ausgeführt.

Nach einem erfolgreichen Lauf ist der Service daher wieder:

inactive (dead)

mit:

status=0/SUCCESS

Das ist normal und kein Fehler.

---

## 7. Statusdateien

Der Zertifikatsmonitor verwendet:

/var/lib/meshcentral-cert-check/

Darin befinden sich unter anderem:

external_hash

meshcentral_hash

last_status

### external_hash

Enthält den zuletzt ermittelten Hash des externen Zertifikats.

### meshcentral_hash

Enthält den von MeshCentral erkannten Zertifikats-Hash.

### last_status

Enthält den letzten Status des Prüflaufs.

Beispiel:

OK

---

## 8. Aktuell bekannter Zertifikats-Hash

Zum dokumentierten Stand:

c02a613bc7b5538ddb8161d5c76cc983152883ce272ee5f2f7e0d42adee969c4cbda3fc6778c0746040a0e07d6b50c7d

Dieser Wert ist eine Momentaufnahme und darf nicht als dauerhaft erwarteter Hash behandelt werden.

Bei einem legitimen Zertifikatswechsel ändert sich der Hash.

Der Zertifikatsmonitor ist genau dafür vorgesehen.

---

## 9. Verhalten bei Zertifikatswechsel

Normalfall:

CDN-Zertifikat
  |
  v
Hash A

MeshCentral
  |
  v
Hash A

Ergebnis:

OK

Bei einem Zertifikatswechsel:

CDN-Zertifikat
  |
  v
Hash B

MeshCentral
  |
  v
Hash A

Der Monitor erkennt:

Mismatch

Danach:

MeshCentral Neustart
  |
  v
MeshCentral lädt neues Zertifikat
  |
  v
erneute Hash-Prüfung
  |
  v
Hash B = Hash B
  |
  v
OK

---

## 10. Getestetes Fehlerszenario

Der Monitor unterstützt einen Simulationsmodus:

sudo /usr/local/sbin/check-mesh-cert.sh --simulate-mismatch

Dabei wird absichtlich ein falscher MeshCentral-Hash simuliert.

Erwartetes Verhalten:

TESTMODUS: simuliere falsches MeshCentral Zertifikat

WARNUNG:
Zertifikat unterschiedlich

Danach wird ein MeshCentral-Neustart ausgelöst.

Nach dem Neustart erfolgt eine erneute Prüfung.

Der dokumentierte Test endete erfolgreich mit:

OK nach Restart:
Zertifikate synchron

---

## 11. Manuelle Prüfung

### Externes Zertifikat prüfen

echo | openssl s_client \
-connect cert.makki.route64.de:443 \
-servername cert.makki.route64.de \
2>/dev/null | openssl x509 -outform der | sha384sum

### MeshCentral-Hash prüfen

journalctl -u meshcentral \
| grep "SHA384 cert hash"

### Zertifikatsmonitor manuell ausführen

sudo systemctl start meshcentral-cert-check.service

---

## 12. Relevante Journaldiagnose

Bei Problemen mit MeshCentral und TLS sollte insbesondere geprüft werden:

journalctl -u meshcentral -n 100

Gesucht werden unter anderem:

Loaded web certificate from

und:

SHA384 cert hash

Damit lässt sich nachvollziehen, welches Zertifikat MeshCentral beim Start tatsächlich geladen hat.

---

## 13. DNS

Die Zertifikats-Domain:

cert.makki.route64.de

wird auf das CDN aufgelöst.

Zum dokumentierten Stand:

49.13.166.255

Prüfung:

dig cert.makki.route64.de +short

Auch:

mesh.makki.route64.de

ist Teil der externen MeshCentral-Struktur.

DNS-Einstellungen für diese Domains sollten nicht ohne vorherige Prüfung geändert werden.

---

## 14. Split-DNS

Im LAN existiert eine interne DNS-Auflösung für MeshCentral.

Dadurch können lokale Geräte MeshCentral direkt erreichen, ohne den externen CDN-Weg zu nehmen.

Ziele:

- unnötige Schleifen vermeiden
- lokale Erreichbarkeit verbessern
- MeshCentral im LAN direkt erreichbar halten
- Funktion auch in Umgebungen mit DS-Lite ermöglichen

Das Split-DNS-Konzept ist Bestandteil der produktiven Netzwerkarchitektur.

---

## 15. Warum das CDN weiterhin benötigt wird

Das CDN wird nicht entfernt, obwohl direkter IPv6-Zugriff möglich ist.

Gründe:

- IPv4-Erreichbarkeit
- Netze ohne funktionierendes IPv6
- Fremdnetze
- Universitätsnetze
- DS-Lite-Umgebungen
- unterschiedliche externe Netzbedingungen

IPv6 allein wird daher nicht als ausreichender Ersatz betrachtet.

---

## 16. Sicherheits- und Betriebsgrundsatz

Der Zertifikatsmonitor soll nicht selbst Zertifikate ausstellen oder verwalten.

Seine Aufgabe ist ausschließlich:

Erkennen
  ->
Vergleichen
  ->
bei Abweichung reagieren
  ->
Ergebnis kontrollieren

Die eigentliche Zertifikatsquelle bleibt der definierte externe Endpunkt.

---

## 17. Wiederanlauf nach einem Zertifikatsproblem

Bei einem unerwarteten TLS-Problem:

1. MeshCentral-Status prüfen.
2. Externes Zertifikat prüfen.
3. MeshCentral-Hash prüfen.
4. Zertifikatsmonitor manuell starten.
5. Journal erneut prüfen.
6. Falls erforderlich MeshCentral-Status erneut kontrollieren.

Wichtige Befehle:

systemctl status meshcentral

systemctl status meshcentral-cert-check.timer

sudo systemctl start meshcentral-cert-check.service

journalctl -u meshcentral-cert-check.service

journalctl -u meshcentral -n 100

---

## 18. Produktionsstatus

Das Zertifikatskonzept wurde vollständig getestet.

Geprüft wurden:

- certUrl funktioniert
- MeshCentral lädt das externe Zertifikat
- CDN- und MeshCentral-Hash stimmen überein
- systemd-Timer funktioniert
- Zertifikatswechsel kann erkannt werden
- automatischer MeshCentral-Neustart funktioniert
- Zertifikat wird nach Neustart erneut geladen
- erneute Prüfung funktioniert
- Agenten verbinden sich nach dem Neustart wieder

Status:

PRODUKTIV

---

## 19. Wichtige Dateien

MeshCentral:

/opt/meshcentral/

MeshCentral-Konfiguration:

/opt/meshcentral/meshcentral-data/config.json

Zertifikatsmonitor:

/usr/local/sbin/check-mesh-cert.sh

Monitor-Status:

/var/lib/meshcentral-cert-check/

Systemd:

/etc/systemd/system/meshcentral-cert-check.service

/etc/systemd/system/meshcentral-cert-check.timer

---

## 20. Grundsatz für zukünftige Änderungen

Die Zertifikatsarchitektur ist produktiv und getestet.

Änderungen an folgenden Komponenten sollten daher nur bewusst und einzeln erfolgen:

- mesh.makki.route64.de
- cert.makki.route64.de
- CDN-Konfiguration
- MeshCentral `certUrl`
- Zertifikatsmonitor
- systemd Timer
- Split-DNS

Nach Änderungen ist mindestens ein vollständiger Zertifikats- und Agent-Reconnect-Test durchzuführen.

---

## Status

Zertifikatskonzept: PRODUKTIV

Automatische Überwachung: AKTIV

Automatische Recovery: GETESTET

Manuelle Intervention bei normalem Zertifikatswechsel: NICHT ERFORDERLICH
