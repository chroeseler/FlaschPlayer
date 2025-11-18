"""
Plasma Effect

Colorful plasma waves created by combining sine functions.
Uses HSV color space for smooth color transitions.
"""

import math
import colorsys


def render(display, width, height, frame):
    """
    Render plasma effect using sine wave interference.

    Creates a psychedelic plasma effect by combining multiple sine waves
    with different frequencies and phases, then mapping to rainbow colors.
    """
    # Animation speed
    time = frame * 0.05

    for y in range(height):
        for x in range(width):
            # Normalize coordinates to 0-1 range
            nx = x / width
            ny = y / height

            # Combine multiple sine waves for plasma effect
            # Each sine wave has different frequency and phase
            value1 = math.sin(nx * 10 + time)
            value2 = math.sin(ny * 10 - time * 0.7)
            value3 = math.sin((nx + ny) * 8 + time * 0.5)
            value4 = math.sin(math.sqrt(nx*nx + ny*ny) * 12 + time)

            # Combine waves
            plasma = (value1 + value2 + value3 + value4) / 4.0

            # Map plasma value to hue (0-1)
            hue = (plasma + 1.0) / 2.0

            # Convert HSV to RGB
            # Full saturation and value for vibrant colors
            rgb = colorsys.hsv_to_rgb(hue, 1.0, 1.0)

            # Convert to 0-255 range
            color = tuple(int(c * 255) for c in rgb)

            display.set_xy(x, y, color)


def get_fps():
    """Run at 30 FPS for smooth animation."""
    return 30
