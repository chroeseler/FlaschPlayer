"""
Clock Variants

Multiple clock visualization styles that cycle between different modes:
- Binary clock
- Progress bars
- Radial clock
- Pixel digits
"""

import math
from datetime import datetime


# Clock mode cycles every 20 seconds
SECONDS_PER_MODE = 20


def draw_binary_clock(display, width, height, now):
    """
    Binary clock representation.

    Each row represents hours, minutes, or seconds in binary.
    """
    # Clear screen
    for y in range(height):
        for x in range(width):
            display.set_xy(x, y, (0, 0, 5))

    hours = now.hour
    minutes = now.minute
    seconds = now.second

    # Draw hours (top section)
    # Use 5 bits for hours (0-23)
    y_hours = height // 4
    for bit in range(5):
        if hours & (1 << bit):
            x = width // 2 - 2 + bit
            if 0 <= x < width:
                display.set_xy(x, y_hours, (255, 100, 100))

    # Draw minutes (middle section)
    # Use 6 bits for minutes (0-59)
    y_minutes = height // 2
    for bit in range(6):
        if minutes & (1 << bit):
            x = width // 2 - 3 + bit
            if 0 <= x < width:
                display.set_xy(x, y_minutes, (100, 255, 100))

    # Draw seconds (bottom section)
    # Use 6 bits for seconds (0-59)
    y_seconds = 3 * height // 4
    for bit in range(6):
        if seconds & (1 << bit):
            x = width // 2 - 3 + bit
            if 0 <= x < width:
                display.set_xy(x, y_seconds, (100, 100, 255))


def draw_progress_bars(display, width, height, now):
    """Progress bar representation of time."""
    # Clear to dark background
    for y in range(height):
        for x in range(width):
            display.set_xy(x, y, (0, 0, 0))

    hours = now.hour
    minutes = now.minute
    seconds = now.second

    # Hours progress (0-23)
    hours_progress = hours / 24.0
    hours_width = int(hours_progress * width)
    y_hours = height // 4
    for x in range(hours_width):
        display.set_xy(x, y_hours, (255, 50, 50))

    # Minutes progress (0-59)
    minutes_progress = minutes / 60.0
    minutes_width = int(minutes_progress * width)
    y_minutes = height // 2
    for x in range(minutes_width):
        display.set_xy(x, y_minutes, (50, 255, 50))

    # Seconds progress (0-59)
    seconds_progress = seconds / 60.0
    seconds_width = int(seconds_progress * width)
    y_seconds = 3 * height // 4
    for x in range(seconds_width):
        display.set_xy(x, y_seconds, (50, 50, 255))


def draw_radial_clock(display, width, height, now):
    """Analog-style radial clock."""
    # Clear to dark background
    for y in range(height):
        for x in range(width):
            display.set_xy(x, y, (0, 0, 10))

    cx = width / 2
    cy = height / 2
    max_radius = min(width, height) / 2 - 1

    hours = now.hour % 12
    minutes = now.minute
    seconds = now.second

    # Draw clock face (outer ring)
    for angle_deg in range(0, 360, 30):
        angle_rad = math.radians(angle_deg - 90)
        x = int(cx + max_radius * 0.9 * math.cos(angle_rad))
        y = int(cy + max_radius * 0.9 * math.sin(angle_rad))
        if 0 <= x < width and 0 <= y < height:
            display.set_xy(x, y, (100, 100, 100))

    # Hour hand (short, red)
    hour_angle = math.radians((hours + minutes / 60.0) * 30 - 90)
    hour_length = max_radius * 0.5
    for r in range(int(hour_length)):
        x = int(cx + r * math.cos(hour_angle))
        y = int(cy + r * math.sin(hour_angle))
        if 0 <= x < width and 0 <= y < height:
            display.set_xy(x, y, (255, 100, 100))

    # Minute hand (medium, green)
    minute_angle = math.radians((minutes + seconds / 60.0) * 6 - 90)
    minute_length = max_radius * 0.7
    for r in range(int(minute_length)):
        x = int(cx + r * math.cos(minute_angle))
        y = int(cy + r * math.sin(minute_angle))
        if 0 <= x < width and 0 <= y < height:
            display.set_xy(x, y, (100, 255, 100))

    # Second hand (long, blue)
    second_angle = math.radians(seconds * 6 - 90)
    second_length = max_radius * 0.9
    for r in range(int(second_length)):
        x = int(cx + r * math.cos(second_angle))
        y = int(cy + r * math.sin(second_angle))
        if 0 <= x < width and 0 <= y < height:
            display.set_xy(x, y, (100, 100, 255))

    # Center dot
    display.set_xy(int(cx), int(cy), (255, 255, 255))


def draw_pulsing_time(display, width, height, now, frame):
    """
    Pulsing circles that represent time.
    Size pulses with seconds, brightness with minutes, color with hours.
    """
    # Clear to dark background
    for y in range(height):
        for x in range(width):
            display.set_xy(x, y, (0, 0, 0))

    cx = width / 2
    cy = height / 2

    hours = now.hour
    minutes = now.minute
    seconds = now.second

    # Calculate smooth second (with milliseconds)
    smooth_seconds = seconds + (frame % 30) / 30.0

    # Pulsing radius based on seconds
    pulse = math.sin(smooth_seconds * math.pi / 30.0)
    max_radius = min(width, height) / 2 - 1
    radius = max_radius * (0.5 + pulse * 0.3)

    # Color based on hours (rainbow)
    hue = (hours % 12) / 12.0
    import colorsys
    base_color = colorsys.hsv_to_rgb(hue, 1.0, 1.0)

    # Brightness based on minutes
    brightness = 0.3 + (minutes / 60.0) * 0.7

    # Draw pulsing circle
    for y in range(height):
        for x in range(width):
            dx = x - cx
            dy = y - cy
            distance = math.sqrt(dx * dx + dy * dy)

            # Draw if within current radius (with soft edge)
            if distance < radius:
                edge_fade = 1.0 - (distance / radius) ** 2
                intensity = brightness * edge_fade
                color = tuple(int(c * 255 * intensity) for c in base_color)
                display.set_xy(x, y, color)


def render(display, width, height, frame):
    """
    Render clock, cycling through different visualization modes.

    Modes change every 20 seconds.
    """
    now = datetime.now()

    # Determine which mode based on current time
    total_seconds = now.minute * 60 + now.second
    mode = (total_seconds // SECONDS_PER_MODE) % 4

    if mode == 0:
        draw_binary_clock(display, width, height, now)
    elif mode == 1:
        draw_progress_bars(display, width, height, now)
    elif mode == 2:
        draw_radial_clock(display, width, height, now)
    else:
        draw_pulsing_time(display, width, height, now, frame)


def get_fps():
    """Run at 30 FPS for smooth second hand movement."""
    return 30
