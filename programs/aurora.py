"""
Aurora Borealis

Flowing, waving lights reminiscent of the Northern Lights.
Uses Perlin noise and sine waves to create organic, ethereal movement
in green, blue, and purple hues.
"""

import math


def perlin_noise(x, y, z=0):
    """
    Simple 3D Perlin-like noise function.

    Returns a value roughly in the range [-1, 1].
    """
    def noise(x, y, z):
        """Hash-based noise function."""
        n = int(x) + int(y) * 57 + int(z) * 131
        n = (n << 13) ^ n
        return (1.0 - ((n * (n * n * 15731 + 789221) + 1376312589) & 0x7fffffff) / 1073741824.0)

    # Get integer and fractional parts
    x_int, y_int, z_int = int(x), int(y), int(z)
    x_frac, y_frac, z_frac = x - x_int, y - y_int, z - z_int

    # Smooth interpolation (smoothstep)
    x_smooth = x_frac * x_frac * (3.0 - 2.0 * x_frac)
    y_smooth = y_frac * y_frac * (3.0 - 2.0 * y_frac)
    z_smooth = z_frac * z_frac * (3.0 - 2.0 * z_frac)

    # Sample noise at 8 corners of the cube
    n000 = noise(x_int, y_int, z_int)
    n001 = noise(x_int, y_int, z_int + 1)
    n010 = noise(x_int, y_int + 1, z_int)
    n011 = noise(x_int, y_int + 1, z_int + 1)
    n100 = noise(x_int + 1, y_int, z_int)
    n101 = noise(x_int + 1, y_int, z_int + 1)
    n110 = noise(x_int + 1, y_int + 1, z_int)
    n111 = noise(x_int + 1, y_int + 1, z_int + 1)

    # Trilinear interpolation
    i00 = n000 * (1 - x_smooth) + n100 * x_smooth
    i01 = n001 * (1 - x_smooth) + n101 * x_smooth
    i10 = n010 * (1 - x_smooth) + n110 * x_smooth
    i11 = n011 * (1 - x_smooth) + n111 * x_smooth

    i0 = i00 * (1 - y_smooth) + i10 * y_smooth
    i1 = i01 * (1 - y_smooth) + i11 * y_smooth

    return i0 * (1 - z_smooth) + i1 * z_smooth


def render(display, width, height, frame):
    """
    Render aurora borealis effect.

    Creates flowing waves of green, blue, and purple light using
    layered Perlin noise and sine waves.
    """
    # Time factor for animation
    time = frame * 0.05

    # Clear to dark sky
    for y in range(height):
        for x in range(width):
            # Very dark blue background (night sky)
            display.set_xy(x, y, (0, 0, 5))

    # Draw aurora in multiple layers
    for y in range(height):
        for x in range(width):
            # Normalized coordinates
            nx = x / width
            ny = y / height

            # Layer 1: Primary aurora waves (green)
            # Use Perlin noise for organic movement
            wave1 = perlin_noise(nx * 3, ny * 2 + time * 0.3, time * 0.2)
            wave1 += math.sin(nx * 6 + time) * 0.3
            wave1 = (wave1 + 1) / 2  # Normalize to [0, 1]

            # Layer 2: Secondary waves (blue-green)
            wave2 = perlin_noise(nx * 4 + 10, ny * 3 + time * 0.4, time * 0.15)
            wave2 += math.cos(nx * 4 + time * 1.2) * 0.4
            wave2 = (wave2 + 1) / 2

            # Layer 3: Accent waves (purple)
            wave3 = perlin_noise(nx * 2 + 20, ny * 4 + time * 0.5, time * 0.1)
            wave3 = (wave3 + 1) / 2

            # Aurora intensity increases toward the middle height
            # and has vertical waves
            vertical_factor = 1.0 - abs(ny - 0.6) * 2
            vertical_factor = max(0, vertical_factor) ** 2

            # Combine waves with intensity falloff
            intensity1 = wave1 * vertical_factor * 0.8
            intensity2 = wave2 * vertical_factor * 0.6
            intensity3 = wave3 * vertical_factor * 0.4

            # Only show aurora where intensity is significant
            threshold = 0.2
            if intensity1 > threshold or intensity2 > threshold or intensity3 > threshold:
                # Green component (primary aurora color)
                green = max(0, min(255, int(intensity1 * 255)))

                # Blue component
                blue = max(0, min(255, int((intensity2 * 0.6 + intensity3 * 0.4) * 255)))

                # Red component (for purple accents)
                red = max(0, min(255, int(intensity3 * 180)))

                # Ensure some brightness
                if green < 20 and blue < 20 and red < 20:
                    continue

                color = (red, green, blue)
                display.set_xy(x, y, color)

            # Add some "stars" in the background (sparse white pixels)
            import random
            random.seed(x * 1000 + y)  # Deterministic based on position
            if random.random() > 0.98 and intensity1 < 0.1:
                star_brightness = int(random.random() * 100 + 50)
                display.set_xy(x, y, (star_brightness, star_brightness, star_brightness))


def get_fps():
    """Run at 20 FPS (aurora is slower, more meditative)."""
    return 20
