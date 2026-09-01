# OtterPi Core – Systempflege und Wartung

Stand: August 2026
System: otterpi

## 1. Grundprinzip

Der OtterPi soll möglichst wartungsarm betrieben werden.

Systempflege bedeutet daher nicht, möglichst viele automatische Wartungsmechanismen einzubauen.

Ziel ist:

- stabile Dienste
- kontrollierte Updates
- geringe Schreiblast
- nachvollziehbare Änderungen
- einfache Wiederherstellung

Änderungen am produktiven System sollen grundsätzlich nachvollziehbar und dokumentiert sein.

## 2. Speicheroptimierung

Der OtterPi verwendet eine SD-Karte als primäres Speichermedium.

Da Flash-Speicher nur eine begrenzte Schreibbelastbarkeit besitzt, wurde die dauerhafte Schreiblast bewusst reduziert.

Aktive Maßnahmen:

- ext4 mit noatime
- reduziertes Journald
- Logrotate
- fstrim
- deaktiviertes Pi-hole Query Logging
- keine unnötigen permanenten Datenbanken
- DynDNS-Ausgabe wird verworfen
- keine historische Speicherung im Status Dashboard

## 3. ext4 und noatime

Das Root-Dateisystem verwendet ext4.

Die Mountoption:

noatime

verhindert unnötige Aktualisierungen der Dateizugriffszeit.

Dadurch werden Schreibzugriffe reduziert.

Das ist insbesondere für ein System mit SD-Karte sinnvoll.

Die tatsächlich verwendeten Mountoptionen können mit:

findmnt /

kontrolliert werden.

## 4. Journald

Das System verwendet systemd-journald.

Das Journal ist bewusst klein konfiguriert.

Ziel:

- wichtige Systemmeldungen behalten
- unnötiges Anwachsen verhindern
- SD-Karte schonen

Das Journal soll nicht als langfristige Monitoring-Datenbank dienen.

Für historische Auswertungen ist es nicht vorgesehen.

## 5. Logrotate

Logrotate ist aktiv.

Damit werden klassische Logdateien regelmäßig rotiert.

Ziel ist insbesondere:

- unkontrolliertes Anwachsen verhindern
- Speicherplatz schützen
- alte Logs automatisch begrenzen

Die Logrotation soll mit der allgemeinen Philosophie des Systems möglichst schlank bleiben.

## 6. Pi-hole Query Logging

Das Pi-hole Query Logging ist deaktiviert.

Grund:

Die vollständige DNS-Historie ist für den Zweck des OtterPi nicht erforderlich.

Durch die Deaktivierung werden gleichzeitig:

- Schreibzugriffe reduziert
- Speicherplatz gespart
- unnötige historische Daten vermieden

Pi-hole bleibt trotzdem als DNS- und Filterdienst aktiv.

## 7. DynDNS

Die DynDNS-Aktualisierung wird regelmäßig ausgeführt.

Aktueller Mechanismus:

0 * * * * curl -sSL "https://ipv64.net/nic/update?key=...&domain=makki.route64.de" >/dev/null 2>&1

Die Ausgabe wird vollständig verworfen.

Dadurch entstehen keine zusätzlichen Logdateien.

Der API-Key darf nicht in der Projektdokumentation oder einem öffentlichen Repository gespeichert werden.

## 8. fstrim

fstrim ist auf dem System aktiv.

Zweck:

Nicht mehr verwendete Speicherbereiche können dem Flash-Speicher beziehungsweise Blockgerät als frei gemeldet werden.

Die tatsächliche Konfiguration sollte bei Bedarf mit systemd geprüft werden.

Typischerweise:

systemctl status fstrim.timer

Der Timer soll nicht unnötig häufig ausgeführt werden.

## 9. Updates

Systemupdates sollen kontrolliert durchgeführt werden.

Vor größeren Updates sollte zunächst der aktuelle Systemstand bekannt sein.

Mindestens folgende Punkte sollten geprüft werden:

- System erreichbar
- MeshCentral aktiv
- nginx aktiv
- Pi-hole aktiv
- Dashboard erreichbar
- Backup vorhanden
- keine aktuellen kritischen Fehler

Bei größeren Änderungen sollte vorher ein Snapshot erstellt werden.

## 10. Update-Prinzip

Nicht jedes verfügbare Update muss sofort installiert werden.

Priorität:

1. Sicherheitsupdates
2. relevante Fehlerkorrekturen
3. wichtige Abhängigkeitsupdates
4. Funktionsupdates
5. optionale Änderungen

Insbesondere bei MeshCentral, Node.js, nginx und Pi-hole sollte vor einem Versionssprung geprüft werden, ob Konfigurationsänderungen oder Kompatibilitätsprobleme zu erwarten sind.

## 11. MeshCentral-Updates

MeshCentral ist ein produktiver Dienst.

Vor einem Update sollte daher:

1. AutoBackup geprüft werden
2. config.json gesichert werden
3. aktuelle Version dokumentiert werden
4. Dienststatus geprüft werden
5. Update durchgeführt werden
6. Dienststatus geprüft werden
7. Webzugriff getestet werden
8. Agent-Verbindung getestet werden
9. Zertifikatsmonitor geprüft werden

Der erfolgreiche Zustand soll nach einem Update wieder eindeutig nachvollziehbar sein.

## 12. nginx-Updates

nginx ist Bestandteil der öffentlichen Webstruktur.

Vor Änderungen an nginx-Konfigurationen soll die Konfiguration geprüft werden.

Typischer Test:

nginx -t

Erst bei erfolgreicher Syntaxprüfung soll nginx neu geladen oder neu gestartet werden.

Danach:

systemctl status nginx

und anschließend ein Funktionstest der betroffenen Webdienste.

## 13. Pi-hole-Updates

Pi-hole ist ein produktiver lokaler DNS-Dienst.

Nach einem Update müssen mindestens geprüft werden:

- pihole-FTL aktiv
- DNS-Auflösung funktioniert
- Webinterface erreichbar
- keine kritischen Fehler im Dienststatus

Da DNS eine zentrale Funktion des Heimnetzes ist, sollte ein Pi-hole-Update nicht parallel zu mehreren anderen größeren Änderungen durchgeführt werden.

## 14. Node.js

MeshCentral verwendet Node.js.

Die Node-Version gehört deshalb zu den relevanten Systemversionen.

Ein Node.js-Update kann Auswirkungen auf MeshCentral haben.

Daher gilt:

Node.js nicht unabhängig von MeshCentral betrachten.

Vor einem größeren Node-Versionssprung:

- MeshCentral-Version dokumentieren
- Node-Version dokumentieren
- Backup prüfen
- Kompatibilität prüfen
- nach Update MeshCentral testen

## 15. Neustarts

Ein Neustart des Raspberry Pi wurde erfolgreich getestet.

Nach einem Boot sollen die produktiven Dienste automatisch starten.

Dazu gehören insbesondere:

- nginx
- MeshCentral
- Pi-hole FTL
- fcgiwrap
- NetworkManager
- systemd-timesyncd
- Zertifikatsmonitor
- Zertifikatsmonitor-Timer

Nach größeren Systemupdates ist ein kontrollierter Neustart sinnvoll, wenn dies vom Update erforderlich ist.

## 16. Wartungscheck nach Neustart

Nach einem geplanten Neustart sollten mindestens folgende Punkte geprüft werden:

systemctl status nginx

systemctl status meshcentral

systemctl status pihole-FTL

systemctl status fcgiwrap

systemctl status NetworkManager

systemctl status systemd-timesyncd

systemctl status meshcentral-cert-check.timer

Zusätzlich:

- Dashboard öffnen
- DNS testen
- MeshCentral testen
- Agent-Verbindung prüfen

## 17. Systemzeit

Die Zeitsynchronisation erfolgt über:

systemd-timesyncd

Eine korrekte Systemzeit ist wichtig für:

- TLS-Zertifikate
- Logs
- Cron
- systemd Timer
- DynDNS
- Diagnose

Der Dienst wird deshalb überwacht und gehört zum dokumentierten produktiven Dienstbestand.

## 18. Speicherplatz

Der aktuelle Root-Speicherstand laut Snapshot:

58 GB Gesamtgröße

11 GB belegt

46 GB verfügbar

Belegung:

19 %

Damit besteht derzeit kein akuter Speicherplatzmangel.

Das Dashboard überwacht die Belegung weiterhin.

Warnschwelle:

75 %

Kritische Schwelle:

90 %

Diese Werte dienen als Betriebsindikator und sind keine exakte Vorhersage eines unmittelbar bevorstehenden Ausfalls.

## 19. Inodes

Neben dem belegten Speicherplatz werden die Inodes überwacht.

Damit können auch Situationen erkannt werden, in denen sehr viele kleine Dateien vorhanden sind, obwohl noch ausreichend Speicherplatz verfügbar ist.

Aktuelle Dashboard-Schwellen:

unter 80 %:

OK

80–90 %:

Warnung

über 90 %:

kritisch

## 20. RAM und Swap

Das System besitzt:

1 GB RAM

Zusätzlich ist zram-Swap vorhanden.

Das Dashboard überwacht:

- RAM-Auslastung
- Swap-Auslastung
- Swap-Gerät
- Swap-Typ
- Swap-Status

Eine hohe Swap-Nutzung wird als Warnsignal betrachtet.

Ziel ist nicht, Swap vollständig zu vermeiden, sondern ungewöhnliche Speichernutzung frühzeitig sichtbar zu machen.

## 21. Temperatur

Die CPU-Temperatur wird über das Linux-Thermal-Subsystem ausgelesen.

Aktuelle Dashboard-Schwellen:

unter 65 °C:

OK

65–80 °C:

Warnung

ab 80 °C:

kritisch

Diese Werte dienen der einfachen Gesundheitsanzeige.

Die Raspberry-Pi-Hardware verfügt zusätzlich über eigene Schutzmechanismen gegen Übertemperatur.

## 22. Hardwareintegrität

Auf Raspberry-Pi-Systemen wird, sofern verfügbar, folgende Information geprüft:

vcgencmd get_throttled

Damit können unter anderem Hinweise auf:

- Unterspannung
- Frequenzbegrenzung
- Drosselung
- Temperatur-Limit

erkannt werden.

Das Dashboard unterscheidet dabei zwischen:

OK

seit Start aufgetreten

aktuell aktiv

unbekannt

## 23. Änderungen am System

Produktive Änderungen sollen möglichst einzeln durchgeführt werden.

Empfohlen:

1. Ausgangszustand dokumentieren
2. Backup erstellen
3. eine Änderung durchführen
4. Syntax beziehungsweise Konfiguration prüfen
5. Dienst neu starten oder reloaden
6. Funktion testen
7. Ergebnis dokumentieren

Dadurch bleibt die Ursache eines Problems nachvollziehbar.

## 24. Keine unnötige Automatisierung

Automatisierung ist willkommen, wenn sie einen klaren betrieblichen Nutzen hat.

Bereits sinnvoll automatisiert sind beispielsweise:

- MeshCentral-Zertifikatsprüfung
- MeshCentral-Recovery nach Zertifikatswechsel
- AutoBackup
- fstrim
- DynDNS-Aktualisierung
- Dienststart nach Boot

Nicht vorgesehen sind dagegen komplexe automatische Reparaturmechanismen, die bei unklaren Fehlern eigenständig viele Systemkomponenten verändern.

## 25. Dashboard als Diagnosewerkzeug

Das Status Dashboard soll die Wartung unterstützen.

Es soll möglichst schnell beantworten:

- Läuft das System?
- Gibt es Hardwareprobleme?
- Gibt es Ressourcenprobleme?
- Sind wichtige Dienste aktiv?
- Funktioniert das Netzwerk?
- Gibt es offensichtliche Fehler?

Es soll dagegen kein Ersatz für:

- systemctl
- journalctl
- dmesg
- Netzwerkdiagnose
- Paketverwaltung

sein.

## 26. Wartungsphilosophie

Der OtterPi ist eine Appliance-artige private Infrastruktur.

Deshalb gilt:

Lieber wenige zuverlässige Prüfungen als ein komplexes Monitoring-System.

Lieber nachvollziehbare manuelle Wartung als aggressive Automatisierung.

Lieber eine kleine Dokumentation als eine Vielzahl voneinander abhängiger Tools.

## 27. Aktueller Zustand

Der dokumentierte Systemstand ist:

- stabil
- produktiv
- getestet
- ressourcenschonend
- wartbar
- dokumentiert

Die vorhandenen automatischen Wartungsmechanismen funktionieren.

## 28. Ziel

Die Systempflege soll den Charakter des OtterPi erhalten:

klein
↓
übersichtlich
↓
wartbar
↓
zuverlässig

Der Server soll nicht durch zusätzliche Wartungssoftware selbst zum Wartungsprojekt werden.

---
Ende der Datei
