"""Conway's Game of Life on a toroidal grid. Respawns when population collapses."""
import random

_grid = None
_age = None
_gen = 0


def _random_grid(width, height):
    return [[random.random() < 0.35 for _ in range(width)] for _ in range(height)]


def _step(grid, width, height):
    new = [[False] * width for _ in range(height)]
    for y in range(height):
        for x in range(width):
            n = sum(
                grid[(y + dy) % height][(x + dx) % width]
                for dy in (-1, 0, 1) for dx in (-1, 0, 1)
                if dy or dx
            )
            new[y][x] = n == 3 or (grid[y][x] and n == 2)
    return new


def render(display, width, height, frame):
    global _grid, _age, _gen

    if _grid is None:
        _grid = _random_grid(width, height)
        _age  = [[0] * width for _ in range(height)]
        _gen  = 0

    _grid = _step(_grid, width, height)
    _gen += 1

    # Track cell age for color (young = bright, old = dimmer)
    for y in range(height):
        for x in range(width):
            if _grid[y][x]:
                _age[y][x] = min(_age[y][x] + 1, 30)
            else:
                _age[y][x] = 0

    population = sum(_grid[y][x] for y in range(height) for x in range(width))
    if population < 4 or _gen > 300:
        _grid = _random_grid(width, height)
        _age  = [[0] * width for _ in range(height)]
        _gen  = 0

    for y in range(height):
        for x in range(width):
            if _grid[y][x]:
                age = _age[y][x]
                # Newborn cells glow cyan-white, older cells shift to blue-green
                brightness = max(80, 255 - age * 4)
                r = max(0, 80 - age * 3)
                color = (r, brightness, brightness // 2)
            else:
                color = (0, 0, 0)
            display.set_xy(x, y, color)


def get_fps():
    return 8
