import math
import colorsys
import random

_balls = None

_BALL_COUNT = 5


def _make_ball(width, height, hue):
    angle = random.uniform(0, math.tau)
    speed = random.uniform(0.3, 0.7)
    return {
        'x':   random.uniform(1.5, width  - 1.5),
        'y':   random.uniform(1.5, height - 1.5),
        'vx':  math.cos(angle) * speed,
        'vy':  math.sin(angle) * speed,
        'hue': hue,
    }


def render(display, width, height, frame):
    global _balls
    if _balls is None:
        _balls = [_make_ball(width, height, i / _BALL_COUNT) for i in range(_BALL_COUNT)]

    for y in range(height):
        for x in range(width):
            display.set_xy(x, y, (0, 0, 0))

    hue_shift = frame * 0.003

    for ball in _balls:
        ball['x'] += ball['vx']
        ball['y'] += ball['vy']

        if ball['x'] < 1.5:
            ball['vx'] =  abs(ball['vx'])
        if ball['x'] > width - 1.5:
            ball['vx'] = -abs(ball['vx'])
        if ball['y'] < 1.5:
            ball['vy'] =  abs(ball['vy'])
        if ball['y'] > height - 1.5:
            ball['vy'] = -abs(ball['vy'])

        hue = (ball['hue'] + hue_shift) % 1.0
        base_r, base_g, base_b = colorsys.hsv_to_rgb(hue, 1.0, 1.0)

        cx, cy = ball['x'], ball['y']
        for dy in range(-2, 3):
            for dx in range(-2, 3):
                px = int(cx) + dx
                py = int(cy) + dy
                if not (0 <= px < width and 0 <= py < height):
                    continue
                dist = math.hypot(cx - px, cy - py)
                if dist > 2.2:
                    continue
                bright = max(0.0, 1.0 - dist / 2.2)
                display.set_xy(px, py, (
                    int(base_r * 255 * bright),
                    int(base_g * 255 * bright),
                    int(base_b * 255 * bright),
                ))


def get_fps():
    return 30
