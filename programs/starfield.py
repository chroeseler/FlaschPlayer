"""
Starfield

Classic flying-through-space effect with stars zooming from center outward.
Features parallax layers and color-coded depth for enhanced 3D effect.
"""

import random


class Star:
    """A star in the starfield with position and depth."""

    def __init__(self, width, height):
        self.reset(width, height, random_z=True)

    def reset(self, width, height, random_z=False):
        """Reset star to center with random depth."""
        # Position in 3D space
        # Start from center and spread out
        angle = random.uniform(0, 6.283185)  # 2*pi
        distance = random.uniform(0, 1) if random_z else 0

        self.x = distance * (width / 2) * random.uniform(-1, 1)
        self.y = distance * (height / 2) * random.uniform(-1, 1)
        self.z = random.uniform(1, 20) if random_z else random.uniform(15, 20)

    def update(self, speed):
        """Move star toward viewer."""
        self.z -= speed

    def project(self, width, height):
        """Project 3D position to 2D screen coordinates."""
        if self.z <= 0:
            return None, None, None

        # Perspective projection
        factor = 200 / self.z
        screen_x = self.x * factor + width / 2
        screen_y = self.y * factor + height / 2

        # Calculate brightness based on depth (closer = brighter)
        brightness = max(0, min(1, (20 - self.z) / 20))

        return screen_x, screen_y, brightness


# Global stars list
stars = []
initialized = False


def render(display, width, height, frame):
    """Render flying starfield with depth."""
    global stars, initialized

    # Initialize stars on first frame
    if not initialized or len(stars) == 0:
        stars = [Star(width, height) for _ in range(50)]
        initialized = True

    # Clear screen (black space)
    for y in range(height):
        for x in range(width):
            display.set_xy(x, y, (0, 0, 0))

    # Speed varies slightly over time for dynamic feel
    import math
    base_speed = 0.15
    speed_variation = math.sin(frame * 0.02) * 0.05
    speed = base_speed + speed_variation

    # Update and draw stars
    for star in stars:
        star.update(speed)

        # Reset star if it's behind the camera
        if star.z <= 0:
            star.reset(width, height, random_z=False)

        # Project to screen
        sx, sy, brightness = star.project(width, height)

        if sx is None:
            continue

        # Convert to integer pixel coordinates
        px = int(sx)
        py = int(sy)

        # Skip if out of bounds
        if not (0 <= px < width and 0 <= py < height):
            # Reset star if it went off screen
            star.reset(width, height, random_z=False)
            continue

        # Color based on depth
        # Distant stars = blue, close stars = white/yellow
        if brightness < 0.3:
            # Distant - blue tint
            color = (
                int(brightness * 100),
                int(brightness * 150),
                int(brightness * 255)
            )
        elif brightness < 0.6:
            # Medium - white
            color = (
                int(brightness * 255),
                int(brightness * 255),
                int(brightness * 255)
            )
        else:
            # Close - yellow/white
            color = (
                int(brightness * 255),
                int(brightness * 255),
                int(brightness * 200)
            )

        display.set_xy(px, py, color)

        # Draw motion trail for faster stars (brightness > 0.7)
        if brightness > 0.7 and star.z < 5:
            # Calculate previous position for trail
            trail_z = star.z + speed * 2
            if trail_z > 0:
                trail_factor = 200 / trail_z
                trail_x = int(star.x * trail_factor + width / 2)
                trail_y = int(star.y * trail_factor + height / 2)

                if 0 <= trail_x < width and 0 <= trail_y < height:
                    trail_color = tuple(int(c * 0.5) for c in color)
                    display.set_xy(trail_x, trail_y, trail_color)


def get_fps():
    """Run at 30 FPS for smooth star motion."""
    return 30
