"""Auto-playing Pong with colorful ball trail and gradient paddles."""
import colorsys
import math

_state = None

_PADDLE_LEN = 3
_TRAIL_LEN = 8


def _init(width, height):
    return {
        'ball_x': float(width // 2),
        'ball_y': float(height // 2),
        'vx': 0.5,
        'vy': 0.4,
        'left_y': float(height // 2 - _PADDLE_LEN // 2),
        'right_y': float(height // 2 - _PADDLE_LEN // 2),
        'trail': [],
        'hue': 0.0,
        'score_flash': 0,
    }


def _move_paddle(paddle_y, ball_y, height, speed=0.35):
    center = paddle_y + _PADDLE_LEN / 2
    if center < ball_y - 0.5:
        paddle_y = min(paddle_y + speed, height - _PADDLE_LEN)
    elif center > ball_y + 0.5:
        paddle_y = max(paddle_y - speed, 0)
    return paddle_y


def render(display, width, height, frame):
    global _state
    if _state is None:
        _state = _init(width, height)

    s = _state
    s['hue'] = (s['hue'] + 0.008) % 1.0

    # Move paddles
    s['left_y']  = _move_paddle(s['left_y'],  s['ball_y'], height)
    s['right_y'] = _move_paddle(s['right_y'], s['ball_y'], height)

    # Record trail before moving ball
    s['trail'].append((s['ball_x'], s['ball_y'], s['hue']))
    if len(s['trail']) > _TRAIL_LEN:
        s['trail'].pop(0)

    # Move ball
    s['ball_x'] += s['vx']
    s['ball_y'] += s['vy']

    # Top / bottom bounce
    if s['ball_y'] <= 0:
        s['ball_y'] = 0
        s['vy'] = abs(s['vy'])
    if s['ball_y'] >= height - 1:
        s['ball_y'] = height - 1
        s['vy'] = -abs(s['vy'])

    # Left paddle (x=1)
    if s['ball_x'] <= 1.5 and s['left_y'] <= s['ball_y'] <= s['left_y'] + _PADDLE_LEN:
        s['ball_x'] = 1.5
        s['vx'] = abs(s['vx']) * 1.03
        offset = (s['ball_y'] - (s['left_y'] + _PADDLE_LEN / 2)) / (_PADDLE_LEN / 2)
        s['vy'] += offset * 0.15
        s['vy'] = max(-1.2, min(1.2, s['vy']))

    # Right paddle (x=width-2)
    if s['ball_x'] >= width - 2.5 and s['right_y'] <= s['ball_y'] <= s['right_y'] + _PADDLE_LEN:
        s['ball_x'] = width - 2.5
        s['vx'] = -abs(s['vx']) * 1.03
        offset = (s['ball_y'] - (s['right_y'] + _PADDLE_LEN / 2)) / (_PADDLE_LEN / 2)
        s['vy'] += offset * 0.15
        s['vy'] = max(-1.2, min(1.2, s['vy']))

    # Cap speed
    speed = math.hypot(s['vx'], s['vy'])
    if speed > 1.4:
        s['vx'] *= 1.4 / speed
        s['vy'] *= 1.4 / speed

    # Ball out of bounds → reset
    if s['ball_x'] < 0 or s['ball_x'] >= width:
        s['ball_x'] = float(width // 2)
        s['ball_y'] = float(height // 2)
        s['vx'] = 0.5 * (1 if s['ball_x'] < 0 else -1)
        s['vy'] = 0.4
        s['trail'].clear()
        s['score_flash'] = 8

    if s['score_flash'] > 0:
        s['score_flash'] -= 1

    # --- Render ---
    for y in range(height):
        for x in range(width):
            display.set_xy(x, y, (0, 0, 0))

    # Centre dashed line
    for y in range(0, height, 2):
        display.set_xy(width // 2, y, (20, 20, 20))

    # Trail
    for i, (tx, ty, th) in enumerate(s['trail']):
        fade = (i + 1) / len(s['trail'])
        r, g, b = colorsys.hsv_to_rgb((th + 0.5) % 1.0, 1.0, fade * 0.9)
        px, py = int(tx), int(ty)
        if 0 <= px < width and 0 <= py < height:
            display.set_xy(px, py, (int(r * 255), int(g * 255), int(b * 255)))

    # Ball (bright, saturated)
    bx, by = int(s['ball_x']), int(s['ball_y'])
    if 0 <= bx < width and 0 <= by < height:
        br, bg, bb = colorsys.hsv_to_rgb(s['hue'], 1.0, 1.0)
        display.set_xy(bx, by, (int(br * 255), int(bg * 255), int(bb * 255)))

    # Left paddle with gradient
    for i in range(_PADDLE_LEN):
        py = int(s['left_y']) + i
        if 0 <= py < height:
            hue = (s['hue'] + i * 0.1) % 1.0
            r, g, b = colorsys.hsv_to_rgb(hue, 0.8, 1.0)
            display.set_xy(0, py, (int(r * 255), int(g * 255), int(b * 255)))
            display.set_xy(1, py, (int(r * 180), int(g * 180), int(b * 180)))

    # Right paddle with gradient
    for i in range(_PADDLE_LEN):
        py = int(s['right_y']) + i
        if 0 <= py < height:
            hue = (s['hue'] + 0.5 + i * 0.1) % 1.0
            r, g, b = colorsys.hsv_to_rgb(hue, 0.8, 1.0)
            display.set_xy(width - 1, py, (int(r * 255), int(g * 255), int(b * 255)))
            display.set_xy(width - 2, py, (int(r * 180), int(g * 180), int(b * 180)))

    # Score flash: full white row flash
    if s['score_flash'] > 0:
        intensity = int(s['score_flash'] / 8 * 80)
        for x in range(width):
            display.set_xy(x, height // 2, (intensity, intensity, intensity))


def get_fps():
    return 30
