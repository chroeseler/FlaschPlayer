"""AI-controlled snake with rainbow body chasing bright food pixels."""
import random
import colorsys

_snake = None
_food = None
_direction = None
_hue_offset = 0.0


def _place_food(width, height, snake):
    occupied = set(snake)
    while True:
        pos = (random.randint(0, width - 1), random.randint(0, height - 1))
        if pos not in occupied:
            return pos


def _init(width, height):
    cx, cy = width // 2, height // 2
    snake = [(cx - i, cy) for i in range(6)]
    food = _place_food(width, height, snake)
    direction = (1, 0)
    return snake, food, direction


def _next_dir(snake, food, width, height, current):
    hx, hy = snake[0]
    fx, fy = food
    dx = fx - hx
    dy = fy - hy

    candidates = []
    if abs(dx) >= abs(dy):
        candidates = [(1 if dx > 0 else -1, 0), (0, 1 if dy > 0 else -1)]
    else:
        candidates = [(0, 1 if dy > 0 else -1), (1 if dx > 0 else -1, 0)]

    # Add perpendiculars as fallback
    cx, cy = current
    perp = [(-cy, cx), (cy, -cx)]
    candidates += perp
    candidates += [(-cx, -cy)]  # reverse last resort

    body = set(snake[:-1])
    for d in candidates:
        nx, ny = (hx + d[0]) % width, (hy + d[1]) % height
        if (nx, ny) not in body:
            return d
    return current


def render(display, width, height, frame):
    global _snake, _food, _direction, _hue_offset

    if _snake is None:
        _snake, _food, _direction = _init(width, height)

    _hue_offset = (_hue_offset + 0.015) % 1.0

    _direction = _next_dir(_snake, _food, width, height, _direction)
    hx, hy = _snake[0]
    nx, ny = (hx + _direction[0]) % width, (hy + _direction[1]) % height
    _snake.insert(0, (nx, ny))

    if (nx, ny) == _food:
        _food = _place_food(width, height, _snake)
    else:
        _snake.pop()

    # Clear
    for y in range(height):
        for x in range(width):
            display.set_xy(x, y, (0, 0, 0))

    # Draw snake with rainbow gradient along body
    for i, (sx, sy) in enumerate(_snake):
        hue = (_hue_offset + i / max(len(_snake), 1) * 0.7) % 1.0
        sat = 1.0
        val = 1.0 if i == 0 else max(0.4, 1.0 - i * 0.03)
        r, g, b = colorsys.hsv_to_rgb(hue, sat, val)
        display.set_xy(sx, sy, (int(r * 255), int(g * 255), int(b * 255)))

    # Draw food: bright white-yellow pulsing dot
    pulse = 0.7 + 0.3 * ((frame % 10) / 10)
    fx, fy = _food
    fhue = (_hue_offset + 0.5) % 1.0
    fr, fg, fb = colorsys.hsv_to_rgb(fhue, 0.3, pulse)
    display.set_xy(fx, fy, (int(fr * 255), int(fg * 255), int(fb * 255)))


def get_fps():
    return 8
