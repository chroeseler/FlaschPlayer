"""Fake spectrum-analyser with organic bar motion and white peak dots."""
import math
import colorsys

# Each bar has its own phase offset so they don't all move together
_PHASES = [i * 0.71 for i in range(25)]


def _bar_height(x, t, max_h):
    # Combine two sine waves per column for a non-repeating feel
    v = (math.sin(t * (0.5 + x * 0.12) + _PHASES[x]) * 0.5 +
         math.sin(t * 0.3 + x * 0.4) * 0.3 +
         math.sin(t * 1.1 + _PHASES[x] * 0.5) * 0.2)
    # v is in [-1, 1]; map to [1, max_h]
    return max(1, int((v + 1) / 2 * (max_h - 1)) + 1)


def render(display, width, height, frame):
    t = frame * 0.07

    for x in range(width):
        bh = _bar_height(x, t, height)

        for y in range(height):
            # Distance from the top of the bar
            bar_top = height - bh
            if y < bar_top:
                display.set_xy(x, y, (0, 0, 0))
            elif y == bar_top:
                display.set_xy(x, y, (255, 255, 255))   # peak dot
            else:
                # Colour: green at bottom, yellow in middle, red at top of bar
                rel = (y - bar_top) / max(bh - 1, 1)    # 0 = top of bar, 1 = bottom
                hue = 0.33 * rel                          # red → yellow → green
                r, g, b = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
                display.set_xy(x, y, (int(r * 255), int(g * 255), int(b * 255)))


def get_fps():
    return 30
