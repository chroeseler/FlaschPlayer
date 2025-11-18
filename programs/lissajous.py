"""
Lissajous Curves

Beautiful parametric curves created by combining sinusoidal motion
in X and Y directions. Frequencies slowly evolve creating mesmerizing
looping patterns.
"""

import math
import colorsys


def render(display, width, height, frame):
    """
    Render animated Lissajous curves.

    Lissajous curves are defined parametrically as:
    x = A*sin(a*t + δ)
    y = B*sin(b*t)

    Where a/b is the frequency ratio.
    """
    # Clear screen
    for y in range(height):
        for x in range(width):
            display.set_xy(x, y, (0, 0, 0))

    # Slowly evolving frequency ratios
    slow_time = frame * 0.01

    # Primary frequency ratio (creates different curve patterns)
    # Oscillate between simple ratios like 3/2, 4/3, 5/4
    freq_a = 3.0 + math.sin(slow_time * 0.3) * 1.0
    freq_b = 2.0 + math.cos(slow_time * 0.2) * 1.0

    # Phase offset (creates rotation effect)
    phase = slow_time * 0.5

    # Number of points to draw
    num_points = 100

    # Draw the Lissajous curve
    for i in range(num_points):
        t = (i / num_points) * 2 * math.pi

        # Calculate position using Lissajous equations
        x_pos = math.sin(freq_a * t + phase)
        y_pos = math.sin(freq_b * t)

        # Map from [-1, 1] to screen coordinates
        # Add some margin
        margin_x = width * 0.1
        margin_y = height * 0.1

        screen_x = (x_pos + 1) / 2 * (width - 2 * margin_x) + margin_x
        screen_y = (y_pos + 1) / 2 * (height - 2 * margin_y) + margin_y

        # Convert to integer pixel coordinates
        px = int(screen_x)
        py = int(screen_y)

        # Color based on position along curve (rainbow effect)
        hue = (i / num_points + slow_time * 0.1) % 1.0
        rgb = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
        color = tuple(int(c * 255) for c in rgb)

        # Draw point if in bounds
        if 0 <= px < width and 0 <= py < height:
            display.set_xy(px, py, color)

            # Draw slightly thicker line by filling adjacent pixels
            # This makes the curve more visible on low-res display
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    nx, ny = px + dx, py + dy
                    if 0 <= nx < width and 0 <= ny < height:
                        # Dimmer color for adjacent pixels
                        dim_color = tuple(int(c * 0.5) for c in color)
                        display.set_xy(nx, ny, dim_color)


def get_fps():
    """Run at 30 FPS for smooth curve animation."""
    return 30
