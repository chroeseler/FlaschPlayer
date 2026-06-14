import random

_heat = None


def _to_color(h):
    if h < 85:
        return (h * 3, 0, 0)
    elif h < 170:
        t = (h - 85) / 85
        return (255, int(t * 200), 0)
    else:
        t = (h - 170) / 85
        return (255, 200 + int(t * 55), int(t * 255))


def render(display, width, height, frame):
    global _heat
    if _heat is None:
        _heat = [[0] * width for _ in range(height)]

    # Seed bottom two rows with fresh heat
    for x in range(width):
        _heat[height - 1][x] = random.randint(180, 255)
        _heat[height - 2][x] = random.randint(100, 200)

    # Propagate heat upward (lower y = further from base = cooler)
    for y in range(height - 2):
        for x in range(width):
            below = _heat[y + 1][x]
            left  = _heat[y + 1][max(0, x - 1)]
            right = _heat[y + 1][min(width - 1, x + 1)]
            avg   = (below * 3 + left + right) // 5
            _heat[y][x] = max(0, avg - random.randint(5, 30))

    for y in range(height):
        for x in range(width):
            display.set_xy(x, y, _to_color(_heat[y][x]))


def get_fps():
    return 20
