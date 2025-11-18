"""
Mandelbrot Fractal

Renders a zooming and panning view of the Mandelbrot set.
Colors based on escape-time algorithm with rainbow palette.
"""

import colorsys


def render(display, width, height, frame):
    """
    Render Mandelbrot set with smooth zooming animation.

    The Mandelbrot set is the set of complex numbers c for which
    the function f(z) = z^2 + c does not diverge.
    """
    # Zoom animation - exponential zoom in
    zoom = 1.0 + (frame * 0.02)

    # Pan slowly around interesting regions
    center_x = -0.5 + math.sin(frame * 0.01) * 0.3
    center_y = 0.0 + math.cos(frame * 0.01) * 0.3

    # Maximum iterations for escape-time algorithm
    max_iter = 50

    for y in range(height):
        for x in range(width):
            # Map pixel coordinates to complex plane
            # Scale based on zoom level
            cx = (x - width / 2) / (width / 4 * zoom) + center_x
            cy = (y - height / 2) / (height / 4 * zoom) + center_y

            # Mandelbrot iteration
            zx = 0.0
            zy = 0.0
            iteration = 0

            # Iterate until escape or max iterations
            while zx*zx + zy*zy < 4.0 and iteration < max_iter:
                # Complex number multiplication: (zx + zy*i)^2 + (cx + cy*i)
                xtemp = zx*zx - zy*zy + cx
                zy = 2*zx*zy + cy
                zx = xtemp
                iteration += 1

            # Color based on iteration count
            if iteration == max_iter:
                # Inside set - black
                color = (0, 0, 0)
            else:
                # Outside set - rainbow color based on escape time
                hue = iteration / max_iter
                # Add time-based color cycling
                hue = (hue + frame * 0.001) % 1.0

                # Convert HSV to RGB
                rgb = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
                color = tuple(int(c * 255) for c in rgb)

            display.set_xy(x, y, color)


def get_fps():
    """Run at 20 FPS (Mandelbrot calculation is more intensive)."""
    return 20


# Import math module for sin/cos
import math
