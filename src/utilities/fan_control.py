#!/usr/bin/env python3

import os
import time

PWMCHIP = "/sys/class/pwm/pwmchip0"
PWM = f"{PWMCHIP}/pwm0"

PERIOD = 40000          # 25 kHz
INTERVAL = 5            # Temperaturprüfung alle 5 s
HYSTERESIS = 3          # °C

STEPS = (
    (45, 20),
    (50, 30),
    (55, 40),
    (60, 50),
    (65, 60),
    (70, 70),
    (75, 80),
    (80, 90),
    (85, 100),
)


def write(path, value):
    with open(path, "w") as f:
        f.write(str(value))


def setup_pwm():
    # PWM0 nach einem Reboot ggf. erst exportieren.
    if not os.path.exists(PWM):
        write(f"{PWMCHIP}/export", 0)
        time.sleep(0.05)

    # Sicherer Startzustand.
    write(f"{PWM}/enable", 0)
    write(f"{PWM}/period", PERIOD)
    write(f"{PWM}/duty_cycle", 0)
    write(f"{PWM}/enable", 1)


def set_pwm(percent):
    duty = PERIOD * percent // 100
    write(f"{PWM}/duty_cycle", duty)


def get_temperature():
    with open("/sys/class/thermal/thermal_zone0/temp") as f:
        return int(f.read()) / 1000


def main():
    setup_pwm()

    pwm = 0
    set_pwm(0)

   # print("OtterPi Lüftersteuerung gestartet")
   # print("PWM: GPIO18 / 25 kHz")
   # print("Kennlinie: 45 °C / 20 % bis 85 °C / 100 %")
   # print("Hysterese: 3 °C")
   # print()

    try:
        while True:
            temp = get_temperature()

            # Lüfter ist aus
            if pwm == 0:
                if temp >= 45:
                    pwm = 20
                    set_pwm(pwm)

            # Lüfter läuft
            else:
                # Hochregeln sofort
                for limit, value in reversed(STEPS):
                    if temp >= limit:
                        if value > pwm:
                            pwm = value
                            set_pwm(pwm)
                        break

                # Herunterregeln mit Hysterese
                for i in range(len(STEPS) - 1, -1, -1):
                    limit, value = STEPS[i]

                    if value != pwm:
                        continue

                    if i == 0:
                        if temp < limit - HYSTERESIS:
                            pwm = 0
                            set_pwm(0)
                    else:
                        lower_limit, lower_value = STEPS[i - 1]

                        if temp < lower_limit - HYSTERESIS:
                            pwm = lower_value
                            set_pwm(pwm)

                    break

           # print(f"CPU: {temp:.1f} °C  |  Lüfter: {pwm} %")

            time.sleep(INTERVAL)

    except KeyboardInterrupt:
        #print("\nBeendet.")
        pass

    finally:
        try:
            set_pwm(0)
            write(f"{PWM}/enable", 0)
        except OSError:
            pass

        #print("Lüfter: 0 %")


if __name__ == "__main__":
    main()
