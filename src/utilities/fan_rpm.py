#!/usr/bin/env python3

import time
import gpiod
from gpiod.line import Edge

GPIO_CHIP = "/dev/gpiochip0"
GPIO_LINE = 17

PULSES_PER_REV = 2
MEASURE_SECONDS = 2.0


def main():
    request = gpiod.request_lines(
        GPIO_CHIP,
        consumer="otterpi-fan-rpm",
        config={
            GPIO_LINE: gpiod.LineSettings(
                direction=gpiod.line.Direction.INPUT,
                edge_detection=Edge.RISING,
            )
        },
    )

    try:
        start = time.monotonic()
        end = start + MEASURE_SECONDS
        pulses = 0

        while time.monotonic() < end:
            events = request.read_edge_events()

            for event in events:
                if event.event_type == gpiod.EdgeEvent.Type.RISING_EDGE:
                    pulses += 1

        elapsed = time.monotonic() - start

    finally:
        request.release()

    frequency = pulses / elapsed
    rpm = frequency * 60.0 / PULSES_PER_REV

    print(f"Pulse:    {pulses}")
    print(f"Zeit:     {elapsed:.3f} s")
    print(f"Frequenz: {frequency:.2f} Hz")
    print(f"RPM:      {rpm:.0f}")


if __name__ == "__main__":
    main()
