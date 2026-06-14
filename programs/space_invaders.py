"""Auto-playing Space Invaders demo with colorful rows and laser effects."""
import random
import colorsys

# Invader sprite: 3 wide x 2 tall pixels (scaled to fit grid)
_INVADER = [
    [0, 1, 0],
    [1, 1, 1],
]
_INV_W = 3
_INV_H = 2

_state = None

_ROW_HUES = [0.0, 0.08, 0.17, 0.55, 0.75]  # red, orange, yellow, cyan, purple


def _init(width, height):
    cols = 7
    rows = 4
    inv_spacing_x = width // cols
    inv_spacing_y = 3
    top_margin = 1

    invaders = []
    for row in range(rows):
        for col in range(cols):
            x = col * inv_spacing_x + (inv_spacing_x - _INV_W) // 2
            y = top_margin + row * inv_spacing_y
            hue = _ROW_HUES[row % len(_ROW_HUES)]
            invaders.append({'x': x, 'y': y, 'hue': hue, 'alive': True})

    return {
        'invaders': invaders,
        'dx': 1,
        'move_timer': 0,
        'move_interval': 8,
        'lasers': [],
        'laser_timer': 0,
        'laser_interval': 20,
        'cannon_x': width // 2,
        'cannon_hue': 0.33,
        'exploding': [],
        'hue_shift': 0.0,
    }


def render(display, width, height, frame):
    global _state
    if _state is None:
        _state = _init(width, height)

    s = _state
    s['hue_shift'] = (s['hue_shift'] + 0.005) % 1.0

    alive = [inv for inv in s['invaders'] if inv['alive']]
    if not alive:
        _state = _init(width, height)
        return

    # Move invaders
    s['move_timer'] += 1
    if s['move_timer'] >= s['move_interval']:
        s['move_timer'] = 0
        min_x = min(inv['x'] for inv in alive)
        max_x = max(inv['x'] + _INV_W - 1 for inv in alive)
        if s['dx'] > 0 and max_x >= width - 1:
            for inv in alive:
                inv['y'] += 1
            s['dx'] = -1
        elif s['dx'] < 0 and min_x <= 0:
            for inv in alive:
                inv['y'] += 1
            s['dx'] = 1
        else:
            for inv in alive:
                inv['x'] += s['dx']

    # Fire laser from cannon toward a random invader
    s['laser_timer'] += 1
    if s['laser_timer'] >= s['laser_interval']:
        s['laser_timer'] = 0
        target = random.choice(alive)
        tx = target['x'] + _INV_W // 2
        ty = target['y']
        s['lasers'].append({
            'x': s['cannon_x'],
            'y': float(height - 2),
            'tx': tx,
            'ty': ty,
            'hue': (s['hue_shift'] + 0.5) % 1.0,
        })
        # Move cannon toward target
        if s['cannon_x'] < tx:
            s['cannon_x'] = min(s['cannon_x'] + 2, width - 1)
        elif s['cannon_x'] > tx:
            s['cannon_x'] = max(s['cannon_x'] - 2, 0)

    # Move lasers upward
    for laser in s['lasers']:
        laser['y'] -= 0.8

    # Collision detection
    new_lasers = []
    for laser in s['lasers']:
        lx, ly = int(laser['x']), int(laser['y'])
        hit = False
        for inv in alive:
            if inv['x'] <= lx <= inv['x'] + _INV_W - 1 and inv['y'] <= ly <= inv['y'] + _INV_H - 1:
                inv['alive'] = False
                s['exploding'].append({'x': inv['x'] + 1, 'y': inv['y'], 'ttl': 6, 'hue': inv['hue']})
                hit = True
                break
        if not hit and ly >= 0:
            new_lasers.append(laser)
    s['lasers'] = new_lasers

    # Tick explosions
    s['exploding'] = [e for e in s['exploding'] if e['ttl'] > 0]
    for e in s['exploding']:
        e['ttl'] -= 1

    # --- Render ---
    for y in range(height):
        for x in range(width):
            display.set_xy(x, y, (0, 0, 0))

    # Invaders
    for inv in s['invaders']:
        if not inv['alive']:
            continue
        hue = (inv['hue'] + s['hue_shift']) % 1.0
        for dy in range(_INV_H):
            for dx in range(_INV_W):
                if _INVADER[dy][dx]:
                    px, py = inv['x'] + dx, inv['y'] + dy
                    if 0 <= px < width and 0 <= py < height:
                        r, g, b = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
                        display.set_xy(px, py, (int(r * 255), int(g * 255), int(b * 255)))

    # Lasers
    for laser in s['lasers']:
        lx, ly = int(laser['x']), int(laser['y'])
        hue = (laser['hue'] + s['hue_shift']) % 1.0
        r, g, b = colorsys.hsv_to_rgb(hue, 0.5, 1.0)
        for py in [ly, ly + 1]:
            if 0 <= py < height:
                display.set_xy(lx, py, (int(r * 255), int(g * 255), int(b * 255)))

    # Explosions
    for e in s['exploding']:
        bright = e['ttl'] / 6.0
        hue = (e['hue'] + s['hue_shift']) % 1.0
        r, g, b = colorsys.hsv_to_rgb(hue, 0.3, bright)
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                px, py = e['x'] + dx, e['y'] + dy
                if 0 <= px < width and 0 <= py < height:
                    display.set_xy(px, py, (int(r * 255), int(g * 255), int(b * 255)))

    # Cannon
    cx = s['cannon_x']
    cy = height - 1
    hue = (s['cannon_hue'] + s['hue_shift']) % 1.0
    r, g, b = colorsys.hsv_to_rgb(hue, 0.6, 1.0)
    col = (int(r * 255), int(g * 255), int(b * 255))
    for dx in [-1, 0, 1]:
        px = cx + dx
        if 0 <= px < width:
            display.set_xy(px, cy, col)
    display.set_xy(cx, cy - 1, col)


def get_fps():
    return 15
