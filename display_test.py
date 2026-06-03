#!/usr/bin/env python3
"""Standalone display smoke-test: cycles solid colours on PyGameDisplay."""
import sys
import time

from display import PyGameDisplay

COLORS = [
    (255, 0, 0),    # red
    (0, 255, 0),    # green
    (0, 0, 255),    # blue
    (255, 255, 0),  # yellow
    (0, 255, 255),  # cyan
    (255, 0, 255),  # magenta
    (255, 255, 255),# white
    (0, 0, 0),      # off
]
HOLD_SECONDS = 0.5


def main():
    display = PyGameDisplay(x_pixels=25, y_pixels=12, pixel_size=30)

    try:
        for color in COLORS:
            if not display.is_running():
                break
            for y in range(display.y_pixels):
                for x in range(display.x_pixels):
                    display.set_xy(x, y, color)
            display.show()
            deadline = time.monotonic() + HOLD_SECONDS
            while time.monotonic() < deadline and display.is_running():
                display.show()
                time.sleep(0.016)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
