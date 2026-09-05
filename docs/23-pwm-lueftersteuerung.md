# 🦦 OtterPi – PWM-Lüftersteuerung

Stand: 05.09.2026

System: `otterpi`  
Hardware: Raspberry Pi 4 Model B Rev 1.5  
Betriebssystem: Debian GNU/Linux 13 „Trixie“  
Architektur: `arm64`

Geplanter Lüfter:

`Noctua NF-A4x10 5V PWM`

Status:

**Temperaturabhängige Lüfterregelung auf dem realen System erfolgreich implementiert und als systemd-Service eingerichtet. Die Regelung verwendet ausschließlich die CPU-Temperatur als Führungsgröße und setzt pro Temperaturstufe direkt den definierten PWM-Prozentwert. Eine RPM-Regelung findet nicht statt.**

**Hardware-PWM auf GPIO18 und Tacho-Erfassung auf GPIO17 sind erfolgreich verifiziert. Die RPM-Erfassung bleibt zunächst von der eigentlichen Lüfterregelung getrennt und soll später als separate, selten abgefragte Dashboard-Funktion ergänzt werden.**

Die Lüftersteuerung startet nach einem Reboot automatisch wieder über `pi-fan.service`. Die erforderliche PWM-Kanalinitialisierung bzw. der Export von `pwm0` wird durch die Software beim Start sichergestellt.

---

## 1. Zweck

Der Raspberry Pi soll mit einem temperaturabhängig geregelten 4-poligen PWM-Lüfter ausgestattet werden.

Der Lüfter soll nicht lediglich ein- und ausgeschaltet werden. Stattdessen wird seine Drehzahl über den separaten PWM-Steuereingang abhängig von der CPU-Temperatur geregelt.

Zusätzlich soll das Tacho-/RPM-Signal überwacht werden.

Die Lösung soll:

- möglichst wenig CPU-Leistung benötigen,
- möglichst wenig RAM benötigen,
- ohne hochfrequentes Python-Polling auskommen,
- Linux-/Hardware-PWM verwenden,
- die Lüfterdrehzahl ausschließlich anhand der CPU-Temperatur steuern,
- keine konstante RPM-Regelung durchführen,
- das Tacho-/RPM-Signal bei Bedarf separat auswerten können,
- als systemd-Service automatisch starten,
- nach einem Reboot die PWM-Steuerung selbstständig wieder initialisieren,
- Statusinformationen bei Bedarf für das bestehende Dashboard bereitstellen.

Die eigentliche Lüfterregelung soll bewusst klein, lokal und ressourcenschonend bleiben.

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

Die PWM wird nicht verwendet, um eine bestimmte Drehzahl konstant zu halten.

Der PWM-Sollwert wird direkt aus der aktuellen CPU-Temperatur und der definierten Temperaturkennlinie bestimmt.

Prinzip:

```text
CPU-Temperatur
      ↓
Temperaturstufe
      ↓
definierter PWM-Wert
      ↓
Hardware-PWM
      ↓
Lüfter
```

Eine Rückkopplung über die tatsächliche RPM ist ausdrücklich nicht Bestandteil der Lüfterregelung.

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

### 6.7 PWM-Initialisierung nach Reboot

Auf dem realen System wurde festgestellt, dass der PWM-Kanal `pwm0` nach einem Reboot nicht automatisch als:

```text
/sys/class/pwm/pwmchip0/pwm0/
```

vorhanden sein muss.

Der PWM-Controller `pwmchip0` ist vorhanden, der Kanal `pwm0` muss jedoch bei Bedarf zunächst über die Kernel-Schnittstelle exportiert werden.

Die `fan_control.py` übernimmt deshalb beim Start die notwendige PWM-Initialisierung.

Damit ist der Dienst unabhängig davon, ob `pwm0` bereits exportiert wurde.

Der gewünschte Startablauf ist:

```text
Boot
  ↓
systemd startet pi-fan.service
  ↓
fan_control.py
  ↓
PWM-Controller prüfen
  ↓
pwm0 bei Bedarf exportieren
  ↓
PWM konfigurieren
  ↓
CPU-Temperatur lesen
  ↓
PWM entsprechend Temperatur setzen
```

Damit soll die Lüftersteuerung nach jedem Reboot selbstständig wieder vollständig betriebsbereit sein.

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

Die CPU-Temperatur ist die alleinige Führungsgröße der Regelung.

Die Lüftersteuerung verwendet eine einfache Stufenkennlinie.

Für jede Temperaturstufe ist ein fester PWM-Prozentwert definiert:

| CPU-Temperatur | PWM |
|---:|---:|
| < 40 °C | 0 % |
| ab 40 °C | 20 % |
| ab 50 °C | 25 % |
| ab 60 °C | 35 % |
| ab 65 °C | 45 % |
| ab 70 °C | 60 % |
| ab 75 °C | 75 % |
| ab 80 °C | 90 % |
| ≥ 85 °C | 100 % |

Es findet keine lineare Interpolation zwischen den Temperaturpunkten statt.

Beispiel:

```text
45 °C → 20 %
55 °C → 25 %
68 °C → 45 %
73 °C → 60 %
77 °C → 75 %
```

Der jeweils gültige PWM-Wert wird anhand der höchsten erreichten Temperaturstufe bestimmt.

Die Kennlinie ist bewusst einfach gehalten und kann direkt im `fan_control.py` angepasst werden.

Die konkreten Werte können nach dem praktischen Betrieb des OtterPi verändert werden.

---

## 9. Hysterese

Die Regelung verwendet eine Hysterese, um unnötiges Umschalten zwischen benachbarten Zuständen bei kleinen Temperaturschwankungen zu vermeiden.

Die Hysterese wird auf die Temperaturstufen angewendet.

Dadurch kann die Temperatur beim Abkühlen unter eine Stufengrenze fallen, ohne dass der PWM-Wert sofort wieder auf die vorherige Stufe zurückspringt.

Die Hysterese ändert nicht die definierten PWM-Werte der Kennlinie.

Prinzip:

```text
Temperatur steigt
      ↓
nächste PWM-Stufe wird erreicht
      ↓
PWM wird erhöht
```

Beim Abkühlen:

```text
Temperatur fällt
      ↓
Hysterese berücksichtigt
      ↓
PWM bleibt zunächst auf aktueller Stufe
      ↓
erst bei ausreichend niedriger Temperatur
      ↓
PWM wird reduziert
```

Die konkrete Hysterese ist im `fan_control.py` definiert und kann dort angepasst werden.

---

## 10. Tacho / RPM

Der Tacho-Anschluss ist hardwareseitig verifiziert, gehört aber zunächst nicht zur eigentlichen Lüfterregelung.

Die Regelung verwendet ausschließlich:

```text
CPU-Temperatur
      ↓
Temperaturkennlinie
      ↓
PWM
```

Die tatsächliche Lüfterdrehzahl wird nicht geregelt und muss keinen konstanten RPM-Wert einhalten.

Das Tacho-Signal auf `GPIO17` bleibt für eine spätere RPM-Auswertung verfügbar.

Die RPM-Erfassung soll bewusst von der eigentlichen Lüftersteuerung getrennt werden.

Geplant ist daher eine separate, selten ausgeführte bzw. bedarfsgesteuerte RPM-Abfrage für Dashboard- oder Diagnosezwecke.

Damit bleibt `fan_control.py` möglichst klein und muss keine permanente RPM-Auswertung durchführen.

Die Tacho-Hardware und die Edge-Erfassung wurden bereits erfolgreich verifiziert. Die genaue RPM-Berechnung wird bei der späteren Dashboard-Funktion umgesetzt.

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

Die RPM-Erfassung ist bewusst nicht Bestandteil der permanent laufenden Temperaturregelung.

`fan_control.py` benötigt für die eigentliche Regelung weder die Tacho-Flanken noch einen RPM-Sollwert.

Die Tacho-Auswertung wird später als separate Funktion für seltene Dashboard- oder Diagnoseabfragen umgesetzt.

Die grundlegende Edge-Erfassung ist bereits verifiziert:

```bash
sudo gpiomon --chip gpiochip0 --edges rising --num-events 20 --localtime 17
```

Damit ist bestätigt, dass der Lüfter ein verwertbares Tacho-Signal auf `GPIO17` liefert.

Für die spätere RPM-Abfrage sind noch festzulegen:

- Tacho-Impulse pro Umdrehung,
- Messdauer bzw. Anzahl der auszuwertenden Flanken,
- Umgang mit sehr niedrigen Drehzahlen,
- Stillstandserkennung,
- Glättung des angezeigten RPM-Wertes.

Diese Funktion wird getrennt von der eigentlichen Lüftersteuerung implementiert.

Die Temperaturregelung bleibt unabhängig von der RPM-Messung.

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

Die CPU-Temperatur wird von `fan_control.py` in einem niedrigen, festen Intervall ausgewertet.

Die eigentliche PWM wird nur verändert, wenn sich der benötigte PWM-Sollwert tatsächlich ändert.

Die permanente Lüftersteuerung benötigt keine RPM-Auswertung.

Das Tacho-Signal wird nicht kontinuierlich durch Python gepollt.

Eine spätere RPM-Abfrage soll separat und nur bei Bedarf bzw. in größeren Intervallen für das Dashboard erfolgen.

Damit bleibt die permanente Regelung möglichst klein:

```text
CPU-Temperatur lesen
      ↓
PWM-Stufe bestimmen
      ↓
nur bei Änderung PWM aktualisieren
      ↓
warten
      ↓
wiederholen
```

Es werden keine permanenten RPM-Berechnungen, keine hochfrequenten GPIO-Abfragen und keine unnötigen Netzwerk- oder Logging-Aktivitäten durchgeführt.

---

## 13. Softwarearchitektur

Die permanente Lüftersteuerung wird durch einen kleinen Userspace-Dienst umgesetzt.

`fan_control.py` übernimmt ausschließlich die für die automatische Regelung erforderlichen Aufgaben:

- PWM-Kanal bei Bedarf initialisieren,
- CPU-Temperatur lesen,
- Temperaturstufe bestimmen,
- PWM-Sollwert setzen,
- Hysterese berücksichtigen,
- PWM beim Beenden sicher auf 0 % setzen.

Die eigentliche Lüfterdrehzahl wird nicht über RPM geregelt.

Die RPM-Erfassung wird später als separate Funktion für Dashboard- bzw. Diagnoseabfragen umgesetzt.

Der Dienst wird über systemd gestartet:

```text
pi-fan.service
```

Die Software liegt im Repository unter:

```text
src/utilities/fan_control.py
```

Auf dem laufenden System wird sie derzeit unter:

```text
/home/makki/fan_control.py
```

ausgeführt.

Der systemd-Service startet die Lüftersteuerung automatisch beim Systemstart und startet sie bei einem unerwarteten Prozessabbruch erneut.

---

## 13.1 Logging

`fan_control.py` erzeugt im normalen Betrieb keine Logausgaben.

Die früher vorhandenen `print()`-Ausgaben wurden bewusst nur auskommentiert und nicht gelöscht, damit sie bei späterem Debugging bei Bedarf wieder aktiviert werden können.

Auch der systemd-Service ist so konfiguriert, dass die Standardausgabe und Standardfehlerausgabe nicht in das Journal geschrieben werden.

Damit entstehen durch die permanente Lüftersteuerung keine fortlaufenden Journal-Einträge.

Das reduziert sowohl unnötige I/O-Aktivität als auch die Schreiblast des Systems.

Für die normale Temperaturregelung ist daher kein dauerhaftes Logging vorgesehen.

---

## 13.2 Repository und Deployment

Die Quellversion der Lüftersteuerung befindet sich im Repository unter:

```text
src/utilities/fan_control.py
```

Auf dem OtterPi wird die aktuell verwendete Version unter:

```text
/home/makki/fan_control.py
```

ausgeführt.

Der systemd-Service verwendet derzeit direkt diese lokale Datei:

```text
/usr/bin/python3 /home/makki/fan_control.py
```

Damit ist zwischen Repository-Quelle und auf dem Gerät ausgeführter Datei zu unterscheiden.

---

## 14. Statusdaten

Die permanente Lüftersteuerung benötigt intern mindestens:

```text
cpu_temperature
fan_pwm_percent
```

Eine spätere RPM-Abfrage kann zusätzlich liefern:

```text
fan_rpm
fan_status
```

Die RPM-/Fehlerbewertung ist bewusst von der Temperaturregelung getrennt.

Damit kann die eigentliche Lüftersteuerung auch dann vollständig funktionieren, wenn keine RPM-Auswertung aktiv ist.

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

**Erledigt.**

Die temperaturabhängige Regelung ist implementiert.

Die Regelung verwendet eine einfache Stufenkennlinie ohne Interpolation.

Die CPU-Temperatur bestimmt direkt den PWM-Sollwert.

Die Hysterese ist Bestandteil der Regelungslogik.

Die Regelung wurde im laufenden Betrieb erfolgreich getestet.

Beispiel:

```text
CPU-Temperatur
      ↓
Temperaturstufe
      ↓
PWM-Prozentwert
      ↓
Hardware-PWM GPIO18
```

Die Kennlinie kann direkt im `fan_control.py` angepasst werden.

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

### Phase 8 – systemd-Service

Die Lüftersteuerung läuft als:

```text
pi-fan.service
```

Der Service ist auf dem OtterPi eingerichtet und aktiviert.

Status:

```bash
systemctl status pi-fan.service
```

Der automatische Start ist aktiviert:

```bash
systemctl is-enabled pi-fan.service
```

Bei einem normalen Systemstart wird die Lüftersteuerung automatisch gestartet.

Der Service verwendet:

```text
Restart=on-failure
RestartSec=5
```

Damit wird der Dienst nach einem unerwarteten Prozessabbruch automatisch neu gestartet.

Die PWM-Initialisierung erfolgt innerhalb von `fan_control.py`, sodass die Lüftersteuerung auch dann korrekt starten kann, wenn `pwm0` nach einem Reboot zunächst nicht exportiert ist.

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

1. endgültige PWM-Kennlinie nach längerem Praxisbetrieb beurteilen,
2. sinnvollen minimalen Dauerbetriebswert festlegen,
3. Tacho-Impulse pro Umdrehung eindeutig bestimmen,
4. Frequenz → RPM kalibrieren,
5. separate RPM-Abfrage implementieren,
6. RPM-Anzeige für das Dashboard bereitstellen,
7. sinnvolle Anlauf- und Stillstandserkennung für die spätere RPM-Auswertung festlegen,
8. Dashboard-Integration der RPM-/Statusdaten.

Bereits verifiziert bzw. umgesetzt sind:

- Hardware-PWM auf GPIO18,
- 25-kHz-PWM,
- Lüfter-Drehzahländerung über den PWM-Duty-Cycle,
- Tacho-Signal auf GPIO17,
- Tacho-Erfassung über libgpiod,
- temperaturabhängige Lüfterregelung,
- einfache Stufenkennlinie ohne Interpolation,
- Hysterese,
- PWM-Initialisierung nach Bedarf,
- automatischer Start über systemd,
- automatischer Neustart des Dienstes bei Fehler,
- Abschalten des Lüfters beim regulären Beenden,
- keine permanenten Logausgaben,
- keine RPM-Rückkopplung in der Temperaturregelung.

---

## 19. Bewusst noch nicht umgesetzt

Folgende Funktionen bleiben bewusst außerhalb der permanenten Lüftersteuerung:

- RPM-Regelung,
- konstante RPM-Sollwerte,
- permanente RPM-Auswertung,
- hochfrequentes GPIO-Polling,
- zusätzlicher Monitoring-Stack,
- separater MQTT-Broker ausschließlich für die Lüftersteuerung.

Die RPM-Erfassung wird später als separate, ressourcenschonende Funktion für Dashboard- und Diagnosezwecke ergänzt.

Die eigentliche Lüfterregelung bleibt bewusst auf die CPU-Temperatur als Führungsgröße beschränkt.

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
    Monitoring / spätere separate RPM-Abfrage

15. Temperatur:
    alleinige Führungsgröße der Regelung

16. Temperaturbereich:
    zunächst 40–85 °C

17. PWM unter 40 °C:
    zunächst 0 %

18. GPIO-Chip:
    `gpiochip0`

19. Tacho-Flankenerfassung:
    `libgpiod / gpiomon`

20. Tacho-Auswertung:
    ereignisbasiert, später separat

21. RPM:
    nicht Bestandteil der Temperaturregelung

22. Ressourcenverbrauch:
    so gering wie praktisch möglich

23. Regelungsintervall:
    ca. 5 Sekunden

24. RPM-Statusaktualisierung:
    nicht Bestandteil des permanenten Regelungsdienstes

25. Automatischer Start:
    `systemd / pi-fan.service`

26. PWM-Initialisierung:
    beim Start des Dienstes, `pwm0` bei Bedarf exportieren

27. Logging:
    im normalen Betrieb deaktiviert

28. Temperaturkennlinie:
    feste Stufenwerte, keine Interpolation

29. PWM-Regelung:
    kein RPM-Regelkreis

30. Dashboard:
    RPM später über separate Status-/Abfragefunktion

---

## 21. Wiedereinstieg

Die eigentliche temperaturabhängige Lüftersteuerung ist inzwischen implementiert und läuft als systemd-Service.

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
Temperaturregelung             ✓
      ↓
Stufenkennlinie                ✓
      ↓
Hysterese                      ✓
      ↓
PWM-Initialisierung            ✓
      ↓
systemd-Service                ✓
      ↓
automatischer Start            ✓
      ↓
RPM-Kalibrierung               offen
      ↓
separate RPM-Abfrage           offen
      ↓
Dashboard-Integration          offen
```

Die permanente Regelung arbeitet nach folgendem Prinzip:

```text
CPU-Temperatur
      ↓
Temperaturstufe
      ↓
definierter PWM-Prozentwert
      ↓
pwmchip0 / pwm0
      ↓
GPIO18
      ↓
Lüfter
```

Die RPM wird dabei nicht als Regelgröße verwendet.

Die Tacho-Erfassung auf GPIO17 bleibt für eine spätere separate RPM-/Dashboard-Funktion verfügbar.

Der aktuelle praktische nächste Schritt ist daher die saubere RPM-Kalibrierung und anschließend die Implementierung einer davon getrennten RPM-Abfrage.
