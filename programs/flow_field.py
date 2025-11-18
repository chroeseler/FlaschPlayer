"""
Perlin Noise Flow Field

Particles flow along a smooth Perlin noise field, creating organic,
fluid-like motion patterns with rainbow color trails.
"""

import math
import random


class Particle:
    """A particle that follows the flow field."""

    def __init__(self, width, height):
        self.x = random.uniform(0, width - 1)
        self.y = random.uniform(0, height - 1)
        self.vx = 0
        self.vy = 0
        self.hue = random.random()
        self.history = []
        self.max_history = 3

    def update(self, field, width, height):
        """Update particle position based on flow field."""
        # Get flow direction from field
        x_idx = int(self.x) % width
        y_idx = int(self.y) % height
        angle = field[y_idx][x_idx]

        # Update velocity
        self.vx = math.cos(angle) * 0.3
        self.vy = math.sin(angle) * 0.3

        # Update position
        self.x += self.vx
        self.y += self.vy

        # Wrap around edges
        if self.x < 0:
            self.x = width - 1
        elif self.x >= width:
            self.x = 0
        if self.y < 0:
            self.y = height - 1
        elif self.y >= height:
            self.y = 0

        # Update hue over time
        self.hue = (self.hue + 0.005) % 1.0


def perlin_noise_2d(x, y, seed=0):
    """Simple 2D Perlin-like noise function."""
    # Simple hash-based noise
    def noise(x, y):
        n = int(x) + int(y) * 57 + seed * 131
        n = (n << 13) ^ n
        return (1.0 - ((n * (n * n * 15731 + 789221) + 1376312589) & 0x7fffffff) / 1073741824.0)

    # Get integer and fractional parts
    x_int = int(x)
    y_int = int(y)
    x_frac = x - x_int
    y_frac = y - y_int

    # Smooth interpolation
    x_smooth = x_frac * x_frac * (3.0 - 2.0 * x_frac)
    y_smooth = y_frac * y_frac * (3.0 - 2.0 * y_frac)

    # Get corner values
    n1 = noise(x_int, y_int)
    n2 = noise(x_int + 1, y_int)
    n3 = noise(x_int, y_int + 1)
    n4 = noise(x_int + 1, y_int + 1)

    # Interpolate
    i1 = n1 * (1 - x_smooth) + n2 * x_smooth
    i2 = n3 * (1 - x_smooth) + n4 * x_smooth

    return i1 * (1 - y_smooth) + i2 * y_smooth


# Global particles list
particles = []
flow_field = []
initialized = False


def render(display, width, height, frame):
    """Render flowing particles following Perlin noise field."""
    global particles, flow_field, initialized

    # Initialize on first frame
    if not initialized or len(particles) == 0:
        particles = [Particle(width, height) for _ in range(20)]
        flow_field = [[0 for _ in range(width)] for _ in range(height)]
        initialized = True

    # Update flow field based on Perlin noise
    time_scale = frame * 0.01
    for y in range(height):
        for x in range(width):
            # Generate angle from Perlin noise
            noise_val = perlin_noise_2d(x * 0.3, y * 0.3, int(time_scale * 10))
            angle = noise_val * math.pi * 2
            flow_field[y][x] = angle

    # Fade entire display for trail effect
    for y in range(height):
        for x in range(width):
            # Darken all pixels (creates trail effect)
            display.set_xy(x, y, (0, 0, 0))

    # Update and draw particles
    for particle in particles:
        particle.update(flow_field, width, height)

        # Convert HSV to RGB for particle color
        hue = particle.hue
        c = 1.0  # Chroma
        h_prime = hue * 6.0
        x_color = c * (1 - abs(h_prime % 2 - 1))

        if h_prime < 1:
            r, g, b = c, x_color, 0
        elif h_prime < 2:
            r, g, b = x_color, c, 0
        elif h_prime < 3:
            r, g, b = 0, c, x_color
        elif h_prime < 4:
            r, g, b = 0, x_color, c
        elif h_prime < 5:
            r, g, b = x_color, 0, c
        else:
            r, g, b = c, 0, x_color

        color = (int(r * 255), int(g * 255), int(b * 255))

        # Draw particle
        px = int(particle.x)
        py = int(particle.y)
        if 0 <= px < width and 0 <= py < height:
            display.set_xy(px, py, color)


def get_fps():
    """Run at 30 FPS for smooth particle motion."""
    return 30
