# 🦦 OtterPi – PWM-Lüftersteuerung

Stand: 05.09.2026

System: `otterpi`  
Hardware: Raspberry Pi 4 Model B Rev 1.5  
Betriebssystem: Debian GNU/Linux 13 „Trixie“  
Architektur: `arm64`

Geplanter Lüfter:

`Noctua NF-A4x10 5V PWM`

Status:

**Hardware-PWM auf GPIO18 und Tacho-Erfassung auf GPIO17 erfolgreich verifiziert. Der angeschlossene Lüfter lässt sich per Hardware-PWM reproduzierbar in der Drehzahl verändern. Die eigentliche temperaturabhängige Regelungssoftware steht noch aus.**

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
| GPIO17 | 11 | Pin 3 / Grün / Tacho |

Prinzip:

```text
Raspberry Pi 4

+5 V  ───────────────────── Lüfter +5 V
GND   ───────────────────── Lüfter GND

GPIO18 ──────────────────── Lüfter PWM

GPIO17 ◄─────────────────── Lüfter Tacho
```

GPIO17 wird als Tacho-Eingang verwendet.

Physischer Pin:
GPIO17 → Pin 11

Der Tacho wurde am realen angeschlossenen Lüfter bereits erfolgreich mit `gpiomon` auf `gpiochip0`, Offset 17, erkannt.

Für den PWM-Anschluss ist kein MOSFET zur Versorgungsschaltung erforderlich.

Der Motor wird direkt mit 5 V versorgt. Der Raspberry Pi liefert lediglich das separate PWM-Steuersignal.

Das Tacho-Signal wird separat als Eingang ausgewertet.

Das Tacho-Signal wurde am angeschlossenen Lüfter bereits erfolgreich auf GPIO17 erfasst. Die weitere Software-Auswertung und die endgültige RPM-Berechnung stehen noch aus.

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

### 6.5 Hardware-PWM-Test mit angeschlossenem Lüfter

Der PWM-Kanal `pwmchip0/pwm0` wurde mit dem angeschlossenen Noctua NF-A4x10 5V PWM erfolgreich getestet.

Verwendete PWM-Frequenz:

```text
period = 40000 ns
       = 25 kHz
```

Der Duty Cycle wurde während des Tests schrittweise verändert.

Getestet wurden unter anderem:

```text
0 %
25 %
50 %
75 %
100 %
```

Die Änderung des Duty Cycles war am realen Lüfter eindeutig reproduzierbar:

- bei niedrigem Duty Cycle läuft der Lüfter langsam,
- mit steigendem Duty Cycle steigt die Drehzahl,
- bei 100 % läuft der Lüfter deutlich schneller,
- bei 0 % stoppt der Lüfter.

Damit ist nicht nur die Funktion des Kernel-PWM-Controllers, sondern auch die tatsächliche Drehzahlsteuerung des angeschlossenen Lüfters über GPIO18 verifiziert.

Beispiel für 25 %:

```text
period     = 40000 ns
duty_cycle = 10000 ns
enable     = 1
```

Berechnung:

```text
10000 / 40000 = 0,25 = 25 %
```

Der Duty Cycle lässt sich anschließend ohne Änderung der PWM-Frequenz direkt verändern.

Beispiel:

```text
20000 / 40000 = 50 %
30000 / 40000 = 75 %
40000 / 40000 = 100 %
```

Der Lüfter reagiert entsprechend auf die Änderungen.

Für einen späteren Softwaredienst soll die PWM weiterhin ausschließlich über den Linux-/Kernel-PWM-Controller erzeugt werden.

---

### 6.6 Tacho-/RPM-Signal auf GPIO17

Der Tacho-Ausgang des angeschlossenen Lüfters wurde erfolgreich auf `GPIO17` erkannt.

Verwendete Linux-GPIO-Schnittstelle:

```text
/dev/gpiochip0
```

GPIO:

```text
gpiochip0 offset 17
```

Verwendetes Werkzeug:

```text
gpiomon (libgpiod v2.2.1)
```

Test:

```bash
sudo gpiomon --chip gpiochip0 --edges rising --num-events 20 --localtime 17
```

Dabei wurden stabile Rising-Edge-Ereignisse empfangen.

Die gemessenen Zeitabstände zwischen den Rising Edges verändern sich reproduzierbar mit der PWM-/Lüfterdrehzahl.

Damit ist bestätigt:

```text
Lüfter Tacho
      ↓
GPIO17
      ↓
gpiochip0 / offset 17
      ↓
libgpiod / gpiomon
      ↓
Edge Events
```

GPIO17 ist damit als Tacho-GPIO festgelegt.

Eine hochfrequente Userspace-Polling-Schleife ist für die spätere RPM-Erfassung nicht erforderlich. Die GPIO-Ereigniserfassung kann über die Kernel-GPIO-Event-Schnittstelle erfolgen.

Die genaue RPM-Berechnung sowie die Anzahl der Tacho-Impulse pro Umdrehung werden im nächsten Schritt anhand der realen Messwerte und der Lüfterspezifikation festgelegt.

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

### 10.1 Verifizierter Tacho-GPIO

Als Tacho-Eingang wurde `GPIO17` ausgewählt.

Physischer Pin:

`Pin 11`

Der GPIO wurde zunächst als Eingang mit Pull-up betrieben:

```text
17: ip    pu | hi // GPIO17 = input
```

Der Eingang zeigte ohne angeschlossenen bzw. stabilen Tacho-Pegel wechselnde Zustände. Nach Anschluss des Lüfter-Tachos wurde das Signal jedoch reproduzierbar mit `gpiomon` erfasst.

Verwendet wurde:

```bash
sudo gpiomon --chip gpiochip0 --edges rising --num-events 20 --localtime 17
```

Damit konnten wiederholt steigende Flanken auf `gpiochip0`, Offset `17`, erfasst werden.

GPIO17 ist damit als geeigneter Tacho-Eingang auf dem realen System verifiziert.

### 10.2 Kalibrierstand Tacho / RPM

Der Tacho wurde bei verschiedenen PWM-Duty-Cycles vermessen.

Die Messung erfolgte über 20 steigende Flanken mit:

```bash
sudo gpiomon --chip gpiochip0 --edges rising --num-events 20 --localtime 17
```

Bisher eindeutig beobachtete Tacho-Frequenzen:

| Test | mittlere Periodendauer | Tacho-Frequenz |
|---:|---:|---:|
| Test 1 | ca. 11,66 ms | ca. 85,8 Hz |
| Test 2 | ca. 24,47 ms | ca. 40,9 Hz |
| Test 3 | ca. 8,41 ms | ca. 118,9 Hz |
| Test 4 | ca. 6,10 ms | ca. 164,0 Hz |

Die Messungen zeigen reproduzierbar, dass der Tacho auf `GPIO17` ein verwertbares Impulssignal liefert.

Die absolute RPM-Berechnung ist noch nicht abgeschlossen. Dafür müssen die Tacho-Impulse pro Umdrehung eindeutig festgelegt werden.

Aktueller Kalibrierstand:

```text
Tacho-GPIO:       GPIO17
Physischer Pin:   11
GPIO-Chip:        gpiochip0
GPIO-Offset:      17
Flanke:           rising
Messmethode:      libgpiod / gpiomon
```

Die bisher gemessenen Frequenzen werden als Referenzwerte für die spätere RPM-Kalibrierung verwendet.

---

## 11. RPM-Auswertung

Das Tacho-Signal soll nicht über eine hochfrequente Userspace-Polling-Schleife erfasst werden.

Die grundsätzliche Erfassungsmethode ist inzwischen verifiziert.

Der Tacho wird über den GPIO-Event-Mechanismus des Kernels und `libgpiod` erfasst. Für die Tests wird `gpiomon` verwendet.

Beispiel:

```bash
sudo gpiomon --chip gpiochip0 --edges rising --num-events 20 --localtime 17
```

Damit ist kein hochfrequentes Userspace-Polling des GPIO-Pegels erforderlich.

Die endgültige RPM-Auswertung soll später ebenfalls ereignisbasiert erfolgen. Die Anwendung muss nicht permanent den GPIO-Zustand abfragen, sondern kann die vom Kernel gemeldeten Flanken auswerten.

Noch offen sind:

- genaue Tacho-Impulse pro Umdrehung,
- sinnvolles Messfenster,
- Glättung der RPM-Anzeige,
- Verhalten bei sehr niedriger Drehzahl,
- Verhalten bei Stillstand,
- Anlaufphase.

Der Tacho-GPIO ist festgelegt:

```text
GPIO17
physischer Pin 11
gpiochip0 / offset 17
```

Die Edge-Erfassung wurde mit `gpiomon` erfolgreich verifiziert.

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

Die RPM-Auswertung soll zunächst ungefähr alle 2 Sekunden als aktualisierter Statuswert bereitgestellt werden.

Die eigentliche Flankenerfassung erfolgt dabei ereignisbasiert über die Linux-GPIO-Event-Schnittstelle und nicht durch kontinuierliches Userspace-Polling.

Damit kann die spätere RPM-Erfassung auch bei hohen Drehzahlen ohne eine hochfrequente Python-Polling-Schleife umgesetzt werden.

Die endgültige Messfenster- und Auswertelogik wird nach Abschluss der RPM-Kalibrierung festgelegt.

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

### Phase 1 – System und Hardware-Schnittstellen geprüft

System und PWM-/GPIO-Funktionen wurden auf dem realen OtterPi geprüft.

Verwendete Prüfungen:

```bash
uname -a
ls -l /sys/class/pwm/
gpioinfo
pinctrl get 18
pinctrl get 17
sudo dtoverlay -l
```

Ergebnis:

- Kernel identifiziert,
- PWM-Controller vorhanden,
- `pwmchip0` vorhanden,
- zwei PWM-Kanäle vorhanden,
- GPIO18 als `PWM0_0` bestätigt,
- Hardware-PWM mit 25 kHz erfolgreich getestet,
- angeschlossener Lüfter reagiert reproduzierbar auf Änderungen des PWM-Duty-Cycles,
- GPIO17 als Tacho-Eingang festgelegt,
- Tacho-Signal auf GPIO17 erfolgreich mit `gpiomon` erkannt,
- stabile Rising-Edge-Ereignisse bei unterschiedlichen Lüfterdrehzahlen beobachtet.

Damit sind sowohl die PWM-Ausgabe als auch die grundlegende Tacho-Erfassung auf der realen Hardware verifiziert.

---

### Phase 2 – Lüfter angeschlossen

Der Noctua NF-A4x10 5V PWM wurde angeschlossen.

Verwendete Anschlüsse:

```text
+5 V    → Lüfter Pin 2 / Gelb
GND     → Lüfter Pin 1 / Schwarz
GPIO18  → Lüfter Pin 4 / Blau / PWM
GPIO17  → Lüfter Pin 3 / Grün / Tacho
```

Der Lüfter wird direkt über die 5-V-Schiene versorgt.

GPIO18 übernimmt ausschließlich das PWM-Steuersignal.

GPIO17 übernimmt ausschließlich die Tacho-Erfassung.

---

### Phase 3 – PWM-Test

Der angeschlossene Lüfter wurde mit verschiedenen PWM-Duty-Cycles getestet.

Dabei wurde bestätigt:

- der Lüfter stoppt bei 0 %,
- der Lüfter läuft bei niedrigem Duty Cycle,
- die Drehzahl steigt mit zunehmendem Duty Cycle,
- 50 %, 75 % und 100 % lassen sich reproduzierbar ansteuern,
- die Drehzahländerung ist am Tacho-Signal eindeutig messbar.

Der praktische PWM-Test ist damit erfolgreich abgeschlossen.

Noch offen ist die Bestimmung des sinnvollen minimalen Anlauf-/Dauerbetriebswertes sowie die genaue Zuordnung von PWM-Duty-Cycle zu realer Drehzahl.

---

### Phase 4 – Tacho anschließen und prüfen

**Erledigt.**

Der Tacho-Ausgang des Lüfters wurde mit `GPIO17` verbunden.

Physischer Pin:

```text
GPIO17 → Pin 11
```

Das Signal wurde erfolgreich mit `gpiomon` erfasst.

Beispiel:

```bash
sudo gpiomon --chip gpiochip0 --edges rising --num-events 20 --localtime 17
```

Dabei wurden stabile, regelmäßig wiederkehrende steigende Flanken beobachtet.

GPIO17 ist damit als Tacho-Eingang grundsätzlich verifiziert.

---

### Phase 5 – RPM-Messung

**Teilweise erledigt.**

Die Tacho-Flankenerfassung über `libgpiod`/`gpiomon` funktioniert.

Es wurden mehrere Messungen bei unterschiedlichen Lüfterdrehzahlen durchgeführt. Dabei wurde eine reproduzierbare Tacho-Frequenz festgestellt.

Noch offen:

- Tacho-Impulse pro Umdrehung eindeutig bestimmen,
- Frequenz → RPM umrechnen,
- Messfenster festlegen,
- RPM glätten,
- Anlauf- und Stillstandserkennung implementieren.

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

1. endgültige PWM-Minimaldrehzahl bestimmen,
2. tatsächliche Drehzahlkurve über den gesamten PWM-Bereich dokumentieren,
3. Tacho-Impulse pro Umdrehung eindeutig festlegen,
4. Frequenz → RPM kalibrieren,
5. sinnvolles RPM-Messfenster festlegen,
6. Anlaufverhalten und Anlaufverzögerung bestimmen,
7. endgültige Hysterese festlegen,
8. endgültige Fehlerlogik festlegen,
9. Implementierung des Userspace-Dienstes,
10. systemd-Service,
11. Dashboard-Schnittstelle.

Bereits verifiziert sind:

- Hardware-PWM auf GPIO18,
- 25-kHz-PWM,
- Lüfter-Drehzahländerung über den PWM-Duty-Cycle,
- Tacho-Signal des Lüfters,
- Tacho-Erfassung über GPIO17,
- Kernel-/libgpiod-basierte Flankenerfassung ohne GPIO-Polling.

---

## 19. Bewusst noch nicht umgesetzt

Bis zum Abschluss der Hardwaretests werden keine weiteren dauerhaften Änderungen vorgenommen.

Insbesondere:

- keine zusätzliche Device-Tree-Konfiguration auf Verdacht,
- keine weiteren PWM-Overlays ohne konkreten Bedarf,
- keine Software-PWM-Lösung,
- keine RPi.GPIO-/wiringPi-Lösung,
- kein systemd-Service,
- keine endgültige Lüfterregelungssoftware.

Die bereits erfolgreich verifizierte Kernel-PWM-Konfiguration und die funktionierende GPIO17-Tacho-Erfassung bleiben zunächst die technische Grundlage für die weitere Implementierung.

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

8. Verifizierte PWM-GPIO-Funktion:
   `PWM0_0`

9. PWM-Frequenz:
   `25 kHz`

10. MOSFET:
    nicht erforderlich

11. Tacho-GPIO:
    `GPIO17`

12. Physischer Tacho-Pin:
    `Pin 11`

13. Tacho-Schnittstelle:
    Linux GPIO Event API / libgpiod

14. Tacho-Funktion:
    zunächst Monitoring, nicht Regelgröße

15. Temperatur:
    Führungsgröße der Regelung

16. Temperaturbereich:
    zunächst 40–85 °C

17. PWM unter 40 °C:
    zunächst 0 %

18. GPIO-Chip:
    `gpiochip0`

19. Tacho-Flankenerfassung:
    `libgpiod / gpiomon`

20. Tacho-Auswertung:
    ereignisbasiert, kein hochfrequentes GPIO-Polling

21. RPM:
    noch nicht endgültig kalibriert

22. Ressourcenverbrauch:
    so gering wie praktisch möglich

23. Regelungsintervall:
    zunächst ca. 5 Sekunden

24. RPM-Statusaktualisierung:
    zunächst ca. 2 Sekunden

25. Automatischer Start:
    systemd

26. Dashboard:
    maschinenlesbare Statusdaten

---

## 21. Wiedereinstieg

Der Hardwaretest des Lüfters ist abgeschlossen.

Der nächste Arbeitsschritt ist die Vervollständigung der Tacho-/RPM-Kalibrierung.

Aktueller Stand:

```text
Lüfter angeschlossen
      ↓
PWM auf GPIO18                 ✓
      ↓
25-kHz-Hardware-PWM            ✓
      ↓
verschiedene PWM-Stufen        ✓
      ↓
Tacho auf GPIO17               ✓
      ↓
Tacho-Flanken erfassen         ✓
      ↓
Tacho-Frequenz messen          ✓
      ↓
Frequenz → RPM kalibrieren     offen
      ↓
Temperaturregelung             offen
      ↓
Fehlererkennung                offen
      ↓
systemd                        offen
      ↓
Dashboard                      offen
```

Der zentrale aktuelle Hardwarebefund lautet:

```text
Raspberry Pi 4
      ↓
Linux 6.18.39+rpt-rpi-v8
      ↓
PWM-Controller pwmchip0
      ↓
PWM-Kanal pwm0
      ↓
GPIO18 / PWM0_0
      ↓
25 kHz Hardware-PWM
      ↓
Lüfter-Drehzahl regelbar

Lüfter Tacho
      ↓
GPIO17 / Pin 11
      ↓
gpiochip0 / Offset 17
      ↓
libgpiod / gpiomon
      ↓
regelmäßige Tacho-Flanken
      ↓
RPM-Kalibrierung noch offen
```

Damit sind inzwischen sowohl die eigentliche Hardware-PWM-Steuerung als auch die grundlegende Tacho-Erfassung auf dem realen OtterPi-System verifiziert.

Der nächste praktische Schritt ist nicht mehr die Suche nach einem geeigneten GPIO, sondern die saubere Kalibrierung der Tacho-Frequenz zu einer tatsächlichen RPM-Anzeige.
