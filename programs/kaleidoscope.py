"""
Kaleidoscope

Symmetrical patterns with rotation and reflection, creating mesmerizing
geometric designs. Features multiple reflection axes and evolving colors.
"""

import math
import colorsys


def render(display, width, height, frame):
    """
    Render kaleidoscope effect with n-fold symmetry.

    Creates patterns by reflecting and rotating a base pattern
    multiple times around a center point.
    """
    # Time-based animation
    time = frame * 0.02

    # Number of symmetry segments (changes slowly over time)
    num_segments = 6 + int(math.sin(time * 0.1) * 2)

    # Rotation animation
    rotation = time * 0.5

    # Center of the display
    cx = width / 2
    cy = height / 2

    # Zoom/scale that pulses
    scale = 1.0 + math.sin(time * 0.3) * 0.3

    for y in range(height):
        for x in range(width):
            # Translate to center
            dx = x - cx
            dy = y - cy

            # Convert to polar coordinates
            distance = math.sqrt(dx * dx + dy * dy)
            angle = math.atan2(dy, dx)

            # Apply rotation
            angle += rotation

            # Create kaleidoscope effect by folding angle
            # This creates n-fold symmetry
            segment_angle = (2 * math.pi) / num_segments
            angle = angle % segment_angle

            # Mirror every other segment for more complexity
            segment_num = int((math.atan2(dy, dx) + rotation) / segment_angle)
            if segment_num % 2 == 1:
                angle = segment_angle - angle

            # Apply scale
            distance *= scale

            # Create pattern based on transformed coordinates
            # Use multiple overlapping patterns for complexity

            # Pattern 1: Concentric rings
            ring_pattern = math.sin(distance * 2) * 0.5 + 0.5

            # Pattern 2: Radial spokes
            spoke_pattern = math.sin(angle * 8) * 0.5 + 0.5

            # Pattern 3: Spiral
            spiral = math.sin(angle * 4 + distance * 1.5 + time) * 0.5 + 0.5

            # Pattern 4: Moving waves
            wave = math.sin(distance * 3 - time * 2) * 0.5 + 0.5

            # Combine patterns
            combined = (ring_pattern * 0.3 +
                       spoke_pattern * 0.3 +
                       spiral * 0.2 +
                       wave * 0.2)

            # Color based on pattern and angle
            # Create rainbow effect that rotates
            hue = (angle / (2 * math.pi) + time * 0.05) % 1.0

            # Saturation based on distance (more saturated toward edge)
            saturation = min(1.0, distance / (max(width, height) / 2))

            # Value/brightness based on combined pattern
            value = combined

            # Convert HSV to RGB
            rgb = colorsys.hsv_to_rgb(hue, saturation, value)
            color = tuple(int(c * 255) for c in rgb)

            display.set_xy(x, y, color)


def get_fps():
    """Run at 25 FPS for smooth kaleidoscope rotation."""
    return 25
