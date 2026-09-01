# 🦦 OtterPi – PWM-Lüftersteuerung

Stand: 01.09.2026

System: `otterpi`  
Hardware: Raspberry Pi 4 Model B Rev 1.5  
Betriebssystem: Debian GNU/Linux 13 „Trixie“  
Architektur: `arm64`

Geplanter Lüfter:

`Noctua NF-A4x10 5V PWM`

Status:

**Hardware-PWM auf GPIO18 verifiziert. Lüftereinbau und eigentliche Regelungssoftware stehen noch aus.**

---

## 1. Zweck

Der Raspberry Pi soll mit einem temperaturabhängig geregelten 4-poligen PWM-Lüfter ausgestattet werden.

Der Lüfter soll nicht lediglich ein- und ausgeschaltet werden. Stattdessen wird seine Drehzahl über den separaten PWM-Steuereingang abhängig von der CPU-Temperatur geregelt.

Zusätzlich soll das Tacho-/RPM-Signal überwacht werden.

Die geplante Lösung soll:

- möglichst wenig CPU-Leistung benötigen,
- möglichst wenig RAM benötigen,
- ohne hochfrequentes Python-Polling auskommen,
- Linux-/Hardware-PWM verwenden,
- die tatsächliche Lüfterdrehzahl überwachen,
- einen möglichen Lüfterfehler erkennen,
- als systemd-Service automatisch starten,
- Statusinformationen für das bestehende Dashboard bereitstellen.

Die Lüftersteuerung soll als kleine, lokale und ressourcenschonende Systemkomponente umgesetzt werden.

---

## 2. Hardware

### 2.1 Raspberry Pi

Verwendet wird:

`Raspberry Pi 4 Model B Rev 1.5`

Der Pi verwendet:

- 4 CPU-Kerne
- 1 GB RAM
- arm64
- Debian GNU/Linux 13 „Trixie“

---

### 2.2 Lüfter

Verwendet wird ausschließlich:

`Noctua NF-A4x10 5V PWM`

Baugröße:

`40 × 40 × 10 mm`

Versorgung:

`5 V`

Der Lüfter besitzt einen 4-poligen Anschluss.

| Lüfter-Pin | Farbe | Funktion |
|---|---|---|
| 1 | Schwarz | GND |
| 2 | Gelb | +5 V |
| 3 | Grün | Tacho / RPM |
| 4 | Blau | PWM |

Der Lüfter benötigt maximal etwa 70 mA.

---

## 3. Geplante Verkabelung

Die Versorgung erfolgt direkt über die 5-V-Schiene des Raspberry Pi.

Der GPIO wird ausdrücklich **nicht** zur Versorgung des Motors verwendet.

Geplante Belegung:

| Raspberry Pi 4 | Physischer Pin | Lüfter |
|---|---:|---|
| +5 V | 4 | Pin 2 / Gelb |
| GND | 6 | Pin 1 / Schwarz |
| GPIO18 | 12 | Pin 4 / Blau / PWM |
| freier GPIO | noch offen | Pin 3 / Grün / Tacho |

Prinzip:

```text
Raspberry Pi 4

+5 V  ───────────────────── Lüfter +5 V
GND   ───────────────────── Lüfter GND

GPIO18 ──────────────────── Lüfter PWM

GPIO ? ◄─────────────────── Lüfter Tacho
```

Für den PWM-Anschluss ist kein MOSFET zur Versorgungsschaltung erforderlich.

Der Motor wird direkt mit 5 V versorgt. Der Raspberry Pi liefert lediglich das separate PWM-Steuersignal.

Das Tacho-Signal wird separat als Eingang ausgewertet.

Vor dem direkten Anschluss des Tacho-Signals muss dessen elektrische Beschaltung anhand der konkreten Lüfterspezifikation geprüft werden.

---

## 4. Warum ein 4-poliger PWM-Lüfter?

Ein klassischer 2-poliger Lüfter müsste über seine Versorgung geschaltet bzw. geregelt werden.

Der verwendete NF-A4x10 5V PWM besitzt dagegen einen separaten PWM-Steuereingang.

Damit bleibt die Versorgung konstant:

```text
+5 V ─────────────── Lüfter
```

und nur das Steuersignal wird verändert:

```text
GPIO18 ───────────── PWM-Eingang
```

Vorteile:

- keine Motorversorgung über GPIO,
- kein MOSFET für die eigentliche Lüfterversorgung,
- konstante 5-V-Versorgung,
- definierter PWM-Eingang,
- Drehzahlsteuerung über die vorgesehene Schnittstelle,
- separates Tacho-Signal zur Überwachung.

---

## 5. PWM-Konzept

Als PWM-Frequenz sind vorgesehen:

`25 kHz`

GPIO18 wurde als PWM-Ausgang ausgewählt.

Die eigentliche PWM-Erzeugung soll durch den Linux-Kernel beziehungsweise den Hardware-PWM-Controller erfolgen.

Es soll ausdrücklich kein Python-basierter Software-PWM-Mechanismus eingesetzt werden.

---

## 6. Verifizierter PWM-/Kernel-Stand

Die PWM-Konfiguration wurde am 01.09.2026 direkt auf dem laufenden System geprüft.

### 6.1 Kernel

```text
Linux otterpi 6.18.39+rpt-rpi-v8 #1 SMP PREEMPT Debian 1:6.18.39-1+rpt1 (2026-07-29) aarch64 GNU/Linux
```

---

### 6.2 PWM vor der Konfiguration

Vor dem Neustart war unter:

```text
/sys/class/pwm/
```

kein PWM-Controller sichtbar.

---

### 6.3 PWM nach dem Neustart

Nach dem Neustart ist vorhanden:

```text
/sys/class/pwm/pwmchip0
```

Der Controller besitzt:

```text
npwm = 2
```

Damit stellt der laufende Kernel einen PWM-Controller mit zwei Kanälen bereit.

---

### 6.4 GPIO18

Der GPIO wurde mit `pinctrl` geprüft.

Vor Aktivierung:

```text
18: ip    pd | lo // GPIO18 = input
```

Nach Aktivierung des PWM-Kanals:

```text
18: a5    pd | lo // GPIO18 = PWM0_0
```

Damit ist die für dieses Projekt entscheidende Zuordnung auf dem tatsächlich laufenden System bestätigt:

```text
GPIO18
  ↓
PWM0_0
  ↓
pwmchip0 / pwm0
```

Es handelt sich somit nicht um eine angenommene oder aus einer Dokumentation übernommene Zuordnung, sondern um einen direkt am System verifizierten Zustand.

---

### 6.5 Hardware-PWM-Test

Der PWM-Kanal wurde testweise exportiert und mit 25 kHz betrieben.

Verwendete Werte:

```text
period = 40000 ns
duty_cycle = 10000 ns
enable = 1
```

Damit ergibt sich:

```text
40000 ns / 25 kHz = 1 Periode
```

und:

```text
10000 / 40000 = 25 %
```

Der Kernel akzeptierte die Konfiguration.

Der Status war:

```text
period:     40000
duty_cycle: 10000
enable:     1
```

Anschließend wurde der Duty Cycle wieder auf:

```text
0
```

gesetzt.

Aktueller Testzustand:

```text
duty_cycle = 0
enable     = 1
```

Damit wird derzeit kein aktiver Lüfterbetrieb angesteuert.

Der eigentliche Lüfter war zum Zeitpunkt dieses Tests noch nicht angeschlossen.

---

## 7. Device Tree und Overlays

Die bestehende Boot-Konfiguration enthält unter anderem:

```text
dtoverlay=vc4-kms-v3d
```

Dies ist die bestehende KMS-/Grafik-Konfiguration und stellt für die geplante Lüfter-PWM kein Problem dar.

Aktuell sind keine zusätzlichen Overlays dynamisch geladen:

```text
sudo dtoverlay -l
```

Ergebnis:

```text
No overlays loaded
```

Die für PWM relevanten Overlay-Dateien sind zwar unter:

```text
/boot/firmware/overlays/
```

vorhanden, werden derzeit aber nicht aktiv geladen.

Insbesondere wurden keine PWM-Overlays auf Verdacht aktiviert.

Die heute verifizierte PWM-Funktion steht bereits ohne ein zusätzlich geladenes Overlay zur Verfügung.

---

## 8. Temperaturregelung

Die CPU-Temperatur ist die Führungsgröße der Regelung.

Vorläufig vorgesehene Kennlinie:

| CPU-Temperatur | PWM |
|---:|---:|
| < 40 °C | 0 % |
| 40 °C | 20 % |
| 50 °C | 25 % |
| 60 °C | 35 % |
| 65 °C | 45 % |
| 70 °C | 60 % |
| 75 °C | 75 % |
| 80 °C | 90 % |
| ≥ 85 °C | 100 % |

Zwischen den definierten Punkten soll linear interpoliert werden.

Beispiele:

```text
45 °C → 22,5 %
55 °C → 30 %
68 °C → ca. 54 %
73 °C → ca. 67,5 %
77 °C → ca. 82,5 %
```

Ab 85 °C wird unabhängig von der Kennlinie 100 % PWM gefahren.

Die konkreten Werte gelten zunächst als Ausgangspunkt und können nach dem realen Lüftertest angepasst werden.

---

## 9. Hysterese

Die Regelung soll eine Hysterese berücksichtigen.

Ziel ist, ein ständiges Ein-/Ausschalten bei Temperaturen knapp um die Einschaltgrenze zu vermeiden.

Vorläufig:

```text
Einschalten:
ab 40 °C

Ausschalten:
unter 38 °C
```

Die endgültigen Werte werden nach dem praktischen Verhalten des Lüfters festgelegt.

---

## 10. Tacho / RPM

Der Tacho-Anschluss wird von Beginn an berücksichtigt.

Er ist zunächst **nicht** Bestandteil der eigentlichen Temperaturregelung.

Die Regelung bleibt:

```text
CPU-Temperatur
      ↓
Temperaturkurve
      ↓
PWM-Sollwert
      ↓
Lüfter
```

Der Tacho dient dagegen zur Überwachung:

```text
Lüfter
   ↓
Tacho / RPM
   ↓
Raspberry Pi
   ↓
Status / Dashboard
```

Mögliche Zustände:

```text
PWM = 0 %, RPM = 0
→ OFF
```

```text
PWM > 0 %, RPM > 0
→ OK
```

```text
PWM > 0 %, RPM = 0
→ möglicher Lüfterfehler
```

```text
PWM hoch, RPM ungewöhnlich niedrig
→ mögliche Blockade / Problem
```

Eine Rückkopplungsregelung anhand der RPM ist zunächst nicht vorgesehen.

Die CPU-Temperatur bleibt die Führungsgröße.

---

## 11. RPM-Auswertung

Das Tacho-Signal soll nicht über eine hochfrequente Userspace-Polling-Schleife erfasst werden.

Die konkrete Methode wird nach Anschluss des Lüfters anhand der tatsächlich verfügbaren GPIO-/Kernel-Funktionen festgelegt.

Dabei müssen insbesondere berücksichtigt werden:

- elektrischer Pegel des Tacho-Ausgangs,
- geeigneter GPIO-Eingang,
- Pull-up-Anforderung,
- Anzahl der Tacho-Impulse pro Umdrehung,
- zuverlässige Erfassung ohne unnötige CPU-Last.

Der Tacho-GPIO ist aktuell noch nicht festgelegt.

---

## 12. Ressourcenverbrauch

Die Lüftersteuerung soll dem Grundprinzip des OtterPi entsprechen:

> möglichst klein, lokal, nachvollziehbar und ressourcenschonend.

Insbesondere vermieden werden sollen:

- schnelle Python-Polling-Schleifen,
- Software-PWM,
- permanentes GPIO-Polling,
- unnötig häufige Dateisystemzugriffe,
- unnötige Netzwerkkommunikation,
- zusätzliche Monitoring-Dienste.

Die geplante Architektur besteht aus:

```text
Linux / Hardware
       │
       ├── PWM-Erzeugung
       │
       └── Tacho-/GPIO-Erfassung
              │
              ▼
       kleiner Userspace-Dienst
              │
       ┌──────┼────────┐
       │      │        │
 Temperatur  PWM     RPM/Status
       │      │        │
       └──────┼────────┘
              ▼
          Dashboard
```

Die CPU-Temperatur soll zunächst ungefähr alle 5 Sekunden ausgewertet werden.

Die RPM-Auswertung soll zunächst ungefähr alle 2 Sekunden aktualisiert werden.

Diese Intervalle sind Ausgangswerte und können nach dem praktischen Test angepasst werden.

Der PWM-Wert soll nur geändert werden, wenn tatsächlich eine relevante Änderung vorliegt.

---

## 13. Softwarearchitektur

Ein kleiner Userspace-Dienst soll später folgende Aufgaben übernehmen:

- CPU-Temperatur lesen,
- Temperatur → PWM berechnen,
- PWM aktualisieren,
- RPM erfassen,
- Lüfterstatus bestimmen,
- Fehlerzustände erkennen,
- Statusdaten für das Dashboard bereitstellen.

Der Dienst soll über systemd gestartet werden.

Geplanter Service:

```text
pi-fan.service
```

Geplanter Statusaufruf:

```bash
systemctl status pi-fan.service
```

Geplanter automatischer Start:

```bash
systemctl enable --now pi-fan.service
```

Die Software wird erst nach Abschluss der Hardwaretests implementiert.

---

## 14. Statusdaten

Der Lüfterdienst soll mindestens folgende Werte bereitstellen:

```text
cpu_temperature
fan_pwm_percent
fan_rpm
fan_status
```

Beispiel:

```text
CPU:        57,3 °C
Lüfter:     42 %
Drehzahl:   2180 RPM
Status:     OK
```

Mögliche Statuswerte:

```text
OFF
OK
WARNING
ERROR
```

Beispiel:

```text
PWM 0 %, RPM 0
→ OFF
```

```text
PWM 50 %, RPM 2200
→ OK
```

```text
PWM 50 %, RPM 0
→ ERROR
```

Die genaue Fehlerlogik wird nach dem realen Anlaufverhalten des Lüfters festgelegt.

---

## 15. Dashboard-Integration

Das bestehende OtterPi-Dashboard ist bewusst als leichtgewichtiger Appliance Health Monitor aufgebaut.

Die Lüftersteuerung soll dieses Konzept nicht durch einen zusätzlichen Monitoring-Stack erweitern.

Bevorzugt wird daher eine lokale, maschinenlesbare Statusbereitstellung.

Eine mögliche Variante ist:

```text
/var/lib/pi-fan/status.json
```

Beispiel:

```json
{
  "temperature": 57.3,
  "pwm": 42.0,
  "rpm": 2180,
  "status": "ok"
}
```

Alternativ kann ein bereits vorhandener MQTT-Broker verwendet werden.

Es soll ausdrücklich kein MQTT-Broker ausschließlich für die Lüftersteuerung installiert werden.

Welche Variante tatsächlich verwendet wird, wird bei der Implementierung anhand der bestehenden Dashboard-Architektur entschieden.

---

## 16. Fehlererkennung

Grundsätzlich vorgesehen:

```text
PWM > 0
UND
RPM = 0
→ FAN ERROR
```

Die Fehlererkennung muss eine Anlaufverzögerung besitzen.

Ein Lüfter darf unmittelbar nach Erhöhung des PWM-Wertes nicht bereits als defekt gemeldet werden, bevor er seine Drehzahl aufgebaut hat.

Daher soll später beispielsweise eine Logik verwendet werden:

```text
PWM wird erhöht
      ↓
Anlaufphase
      ↓
RPM prüfen
      ↓
RPM vorhanden?
   /       \
 JA         NEIN
 ↓           ↓
 OK       WARNING/ERROR
```

Die konkreten Zeitwerte werden erst nach dem Einbau und Test des tatsächlichen Lüfters festgelegt.

---

## 17. Geplanter Einbau- und Testablauf

### Phase 1 – bereits durchgeführt

System und PWM-Funktion prüfen:

```bash
uname -a
ls -l /sys/class/pwm/
gpioinfo
pinctrl get 18
sudo dtoverlay -l
```

Ergebnis:

- Kernel identifiziert,
- PWM-Controller vorhanden,
- `pwmchip0` vorhanden,
- zwei PWM-Kanäle vorhanden,
- GPIO18 als `PWM0_0` bestätigt,
- Hardware-PWM erfolgreich getestet.

---

### Phase 2 – Lüfter anschließen

Geplant:

```text
+5 V  → Lüfter Pin 2
GND   → Lüfter Pin 1
GPIO18 → Lüfter Pin 4 / PWM
```

Der Tacho-Anschluss wird zunächst noch nicht zwingend angeschlossen.

---

### Phase 3 – PWM-Test

Mit angeschlossenem Lüfter sollen zunächst folgende Werte getestet werden:

```text
0 %
20 %
30 %
50 %
75 %
100 %
```

Dabei insbesondere prüfen:

- läuft der Lüfter bei 20 % zuverlässig an?
- muss der Anlaufwert höher gewählt werden?
- wie niedrig kann die Drehzahl sinnvoll geregelt werden?
- ist der Lauf stabil?
- entstehen störende Geräusche?
- ist die Drehzahländerung gleichmäßig?

---

### Phase 4 – Tacho anschließen

Nach Prüfung der elektrischen Eigenschaften des Tacho-Ausgangs:

```text
Lüfter Pin 3 / Grün / Tacho
        ↓
geeigneter GPIO-Eingang
```

Der verwendete GPIO wird erst nach Prüfung der freien GPIOs und der elektrischen Anforderungen festgelegt.

---

### Phase 5 – RPM-Messung

RPM-Erfassung implementieren.

Dabei berücksichtigen:

- Impulse pro Umdrehung,
- Messfenster,
- Anlaufphase,
- niedrige Drehzahlen,
- Stillstand,
- möglichst geringe CPU-Last.

---

### Phase 6 – Temperaturregelung

Kennlinie implementieren:

```text
<40 °C       0 %
40 °C       20 %
50 °C       25 %
60 °C       35 %
65 °C       45 %
70 °C       60 %
75 °C       75 %
80 °C       90 %
≥85 °C     100 %
```

Lineare Interpolation zwischen den Punkten.

---

### Phase 7 – Fehlererkennung

Nach erfolgreicher RPM-Messung:

```text
PWM > 0
+
RPM = 0
+
Anlaufphase abgelaufen
→ FAN ERROR
```

Zusätzlich kann später ein ungewöhnlich niedriger RPM-Wert bei hohem PWM-Sollwert als `WARNING` erkannt werden.

---

### Phase 8 – systemd

Erst nach erfolgreichem manuellen Test:

```text
pi-fan.service
```

installieren und aktivieren.

---

### Phase 9 – Dashboard

Nach erfolgreichem Regelungsbetrieb:

```text
Temperatur
PWM
RPM
Status
```

in das bestehende Dashboard integrieren.

Dabei soll möglichst keine zusätzliche permanente Infrastruktur entstehen.

---

## 18. Noch offene Punkte

Zum aktuellen Stand sind folgende Punkte noch offen:

1. tatsächlicher Lüfterbetrieb mit angeschlossenem NF-A4x10,
2. Verhalten bei 20 % PWM,
3. sinnvoller minimaler PWM-Wert,
4. tatsächliche Drehzahlkurve,
5. Tacho-Pegel und elektrische Beschaltung,
6. geeigneter Tacho-GPIO,
7. zuverlässige RPM-Erfassung,
8. genaue Anlaufverzögerung,
9. endgültige Hysterese,
10. endgültige Fehlerlogik,
11. Implementierung des Userspace-Dienstes,
12. systemd-Service,
13. Dashboard-Schnittstelle.

Diese Punkte sollen erst nach dem realen Lüftertest entschieden werden.

---

## 19. Bewusst noch nicht umgesetzt

Bis zum Abschluss der Hardwaretests werden keine weiteren dauerhaften Änderungen vorgenommen.

Insbesondere:

- keine zusätzliche Device-Tree-Konfiguration auf Verdacht,
- keine weiteren PWM-Overlays ohne konkreten Bedarf,
- keine Software-PWM-Lösung,
- keine RPi.GPIO-/wiringPi-Lösung,
- kein Tacho-GPIO auf Verdacht,
- kein systemd-Service,
- keine endgültige Lüfterregelungssoftware.

Die heute erfolgreich verifizierte Kernel-PWM-Konfiguration bleibt zunächst die technische Grundlage.

---

## 20. Grundsätzliche Designentscheidungen

Folgende Entscheidungen sind festgelegt:

1. Lüfter:
   `Noctua NF-A4x10 5V PWM`

2. Versorgung:
   direkt über 5 V des Raspberry Pi

3. PWM:
   separater PWM-Eingang des Lüfters

4. PWM-GPIO:
   `GPIO18`

5. Physischer PWM-Pin:
   `Pin 12`

6. Hardware-PWM:
   Linux-/Kernel-basiert

7. Verifizierter PWM-Kanal:
   `pwmchip0 / pwm0`

8. Verifizierte GPIO-Funktion:
   `PWM0_0`

9. PWM-Frequenz:
   `25 kHz`

10. MOSFET:
    nicht erforderlich

11. Tacho:
    wird berücksichtigt

12. Tacho-Funktion:
    zunächst Monitoring, nicht Regelgröße

13. Temperatur:
    Führungsgröße der Regelung

14. Temperaturbereich:
    zunächst 40–85 °C

15. PWM unter 40 °C:
    zunächst 0 %

16. Ressourcenverbrauch:
    so gering wie praktisch möglich

17. Regelungsintervall:
    zunächst ca. 5 Sekunden

18. RPM-Auswertung:
    zunächst ca. 2 Sekunden

19. Automatischer Start:
    systemd

20. Dashboard:
    maschinenlesbare Statusdaten

---

## 21. Wiedereinstieg

Der nächste Arbeitsschritt erfolgt nach dem Einbau des Noctua-Lüfters.

Zuerst:

```text
Lüfter anschließen
      ↓
PWM 0 %
      ↓
PWM 20 %
      ↓
PWM 30 %
      ↓
PWM 50 %
      ↓
PWM 75 %
      ↓
PWM 100 %
```

Danach:

```text
Tacho elektrisch prüfen
      ↓
Tacho-GPIO auswählen
      ↓
RPM messen
      ↓
Temperaturregelung implementieren
      ↓
Fehlererkennung
      ↓
systemd
      ↓
Dashboard
```

Wichtig:

Die heute verifizierte Hardware-PWM-Konfiguration muss nicht erneut grundsätzlich gesucht werden.

Der zentrale technische Befund lautet:

```text
Raspberry Pi 4
      ↓
Linux 6.18.39+rpt-rpi-v8
      ↓
pwmchip0
      ↓
pwm0
      ↓
GPIO18
      ↓
PWM0_0
      ↓
25 kHz Hardware-PWM
```

Damit ist die zentrale Voraussetzung für die geplante PWM-Lüftersteuerung auf dem realen OtterPi-System bestätigt.

Der nächste praktische Test ist ausschließlich der reale Betrieb des angeschlossenen Lüfters.
