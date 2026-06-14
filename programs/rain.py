"""Matrix-style green rain drops falling from top to bottom."""
import random

_drops = None


def _new_drop(width, height):
    length = random.randint(3, 8)
    return {
        'x': random.randint(0, width - 1),
        'y': float(random.randint(-length, -1)),
        'speed': random.uniform(0.25, 0.8),
        'length': length,
    }


def render(display, width, height, frame):
    global _drops
    if _drops is None:
        _drops = [_new_drop(width, height) for _ in range(width // 2 + 3)]

    for y in range(height):
        for x in range(width):
            display.set_xy(x, y, (0, 0, 0))

    for drop in _drops:
        drop['y'] += drop['speed']
        if drop['y'] - drop['length'] > height:
            drop.update(_new_drop(width, height))

        head = int(drop['y'])
        for i in range(drop['length']):
            py = head - i
            if not (0 <= py < height):
                continue
            if i == 0:
                color = (180, 255, 180)          # bright white-green head
            else:
                fade = (1.0 - i / drop['length']) ** 2
                color = (0, int(200 * fade), 0)
            display.set_xy(drop['x'], py, color)


def get_fps():
    return 15
