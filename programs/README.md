# FlaschPlayer Programmatic Programs

This directory contains Python programs that render mathematical shapes, fractals, and procedural animations on the LED display.

## Program API

Each program is a Python module that implements the following interface:

### Required Function

```python
def render(display, width, height, frame):
    """
    Called every frame to render content to the display.

    Args:
        display: Display object with set_xy() and show() methods
        width: Display width in pixels (int)
        height: Display height in pixels (int)
        frame: Current frame number, starts at 0 (int)

    Returns:
        None
    """
    # Your rendering code here
    for y in range(height):
        for x in range(width):
            # Calculate color based on position and frame
            color = (r, g, b)  # RGB values 0-255
            display.set_xy(x, y, color)
```

### Optional Function

```python
def get_fps():
    """
    Return desired frames per second.

    Returns:
        int: FPS (default: 30 if not implemented)
    """
    return 30
```

## Display API

The `display` object passed to `render()` has these methods:

- `display.set_xy(x, y, (r, g, b))` - Set pixel color at coordinates
  - `x`: X coordinate (0 to width-1)
  - `y`: Y coordinate (0 to height-1)
  - `(r, g, b)`: RGB color tuple, values 0-255

- `display.show()` - Flush pixel buffer to display (called automatically by player)

- `display.set_brightness()` - Update brightness from settings (called automatically)

## Usage

Using `uv` (recommended):

```bash
# Run a program in development mode (PyGame window)
uv run --no-project --with pygame --with numpy --with pillow programmatic_player.py programs.plasma

# Run mandelbrot
uv run --no-project --with pygame --with numpy --with pillow programmatic_player.py programs.mandelbrot

# Custom display size
uv run --no-project --with pygame --with numpy --with pillow programmatic_player.py programs.plasma -x 5 -y 3

# Rotate display 90 degrees
uv run --no-project --with pygame --with numpy --with pillow programmatic_player.py programs.plasma --rotate

# Run on hardware (set NEOPIXEL environment variable)
NEOPIXEL=1 uv run --no-project --with pygame --with numpy --with pillow programmatic_player.py programs.mandelbrot
```

Or using `python3` with virtual environment:

```bash
# First activate your virtual environment, then:
python3 programmatic_player.py programs.plasma
python3 programmatic_player.py programs.mandelbrot
```

## Example Programs

- **plasma.py** - Colorful plasma wave effects using sine functions
- **mandelbrot.py** - Zooming Mandelbrot fractal with rainbow coloring

## Creating a New Program

1. Create a new `.py` file in the `programs/` directory
2. Implement the `render(display, width, height, frame)` function
3. Optionally implement `get_fps()` to control frame rate
4. Test with: `python3 programmatic_player.py programs.yourprogram`

### Simple Example

```python
# programs/rainbow.py
def render(display, width, height, frame):
    """Scrolling rainbow pattern"""
    for y in range(height):
        for x in range(width):
            hue = ((x + frame) % width) / width
            # Convert hue to RGB (0-255)
            if hue < 0.33:
                color = (255, int(hue * 3 * 255), 0)
            elif hue < 0.66:
                color = (int((0.66 - hue) * 3 * 255), 255, 0)
            else:
                color = (0, int((1.0 - hue) * 3 * 255), 255)
            display.set_xy(x, y, color)

def get_fps():
    return 60
```

## Tips

- Use the `frame` parameter to animate over time
- Keep computations efficient - you're rendering every frame
- Test with PyGame first before deploying to hardware
- Use `math` and `colorsys` modules for color and geometric calculations
- Display resolution varies (typically 25x12 or 20x15 pixels)
- Low resolution means simple patterns often work best
