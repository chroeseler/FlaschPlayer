# FlaschPlayer

FlaschPlayer turns a grid of WS2812B LED strips built into beer-crate boxes into a
25×12-pixel animated display. It plays GIF animations, scrolls text sent by a
Telegram bot, shows programmatic animations, and lets a web interface inject text
from a browser — all running on a Raspberry Pi.

---

## Table of Contents

- [Hardware](#hardware)
- [System Architecture](#system-architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Directory Structure](#directory-structure)
- [Configuration](#configuration)
- [Running the System](#running-the-system)
- [Telegram Bot](#telegram-bot)
- [Web Interface](#web-interface)
- [Programmatic Animations](#programmatic-animations)
- [Development Mode (no hardware)](#development-mode-no-hardware)
- [Running as a systemd Service](#running-as-a-systemd-service)
- [Background GIF Library](#background-gif-library)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)

---

## Hardware

### Bill of Materials

| Part | Notes |
|------|-------|
| Raspberry Pi 3B+ or 4 | Any ARM model works; Pi Zero 2 W also confirmed |
| WS2812B LED strip | 60 LEDs/m density works well |
| Beer crate boxes | Standard Eurobox 300×200 mm |
| 5V power supply | At least 3A per 60 LEDs at full brightness |
| Logic level shifter | 3.3V → 5V for the data line (some setups skip this) |

### Wiring

```
Pi GPIO 18 (pin 12) ──[level shifter]──> LED strip DIN
Pi GND               ──────────────────> LED strip GND
5V PSU +             ──────────────────> LED strip +5V
5V PSU GND           ──────────────────> Pi GND (common ground)
```

> **Power:** Never power the LED strip directly from the Pi's 5V rail.
> Use a dedicated PSU rated for `LEDs × 60mA` at peak white.

### Physical Layout

Each beer crate holds one 4×5 box of 20 LEDs wired in a snake pattern.
Boxes tile into a grid. Default configuration:

```
5 boxes wide × 3 boxes tall = 15 boxes = 300 LEDs = 25×12 pixels
```

Supported resolutions (determined by box count and orientation):

| Config | Boxes | Pixels |
|--------|-------|--------|
| 5×3 horizontal | 15 | 25×12 |
| 3×5 vertical | 15 | 20×15 |
| 4×3 horizontal | 12 | 20×12 |

The `layout.py` module computes the mapping from (x, y) pixel coordinates to
LED strip indices for any grid size and rotation.

---

## System Architecture

```
┌───────────────────────────────────────────────────────┐
│                    entry_point.py                     │
│  starts the three components as threads/processes     │
└──────────┬────────────────┬──────────────────┬────────┘
           │                │                  │
     Thread│          Thread│        Process   │
           ▼                ▼                  ▼
    ┌────────────┐  ┌──────────────┐  ┌──────────────────┐
    │  blinky.py │  │blinky_bot.py │  │blinky_interface  │
    │ GIF player │  │Telegram bot  │  │  Flask web UI    │
    └─────┬──────┘  └──────┬───────┘  └────────┬─────────┘
          │                │                    │
          │reads           │writes              │writes
          │                │                    │
    ┌─────▼──────┐   ┌─────▼──────────────────┐ │
    │  thequeue  │   │       text_queue        │◄┘
    │  (GIF q.)  │   │   (text overlay q.)     │
    └─────┬──────┘   └──────────┬──────────────┘
          │                     │
          └──────────┬──────────┘
                     │
               ┌─────▼───────┐
               │  display.py  │
               │  NeoPixel or │
               │  PyGame sim  │
               └─────────────┘
```

**`blinky.py`** — main display loop. Reads the GIF queue, plays backgrounds,
overlays scrolling text, and drives the display at frame rate.

**`blinky_bot.py`** — Telegram bot. Accepts GIFs/photos/text from authorised
users, resizes them with FFmpeg, and enqueues them.

**`blinky_interface.py`** — lightweight Flask web app on port 5000. Lets
anyone on the local network type text that gets queued for the display.

**`programmatic_player.py`** — standalone player for mathematical/procedural
animations. Runs independently of the main stack.

---

## Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) package manager
- `ffmpeg` system package (for GIF/video resizing in the bot)
- On the Pi: `libopenjp2-7` for Pillow JPEG-2000 support

```bash
# Raspberry Pi OS
sudo apt update
sudo apt install ffmpeg libopenjp2-7
```

Install uv:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

---

## Installation

```bash
git clone https://github.com/yourname/flaschplayer.git
cd flaschplayer
uv sync
```

`uv sync` creates `.venv/` and installs all Python dependencies from `uv.lock`.

To also install dev tools (pytest, mypy):

```bash
uv sync --group dev
```

---

## Directory Structure

FlaschPlayer separates its runtime data from the source tree. You choose a
**work directory** (`WORK_DIR`) where queues, config, uploaded GIFs, and
backgrounds live.

### Source tree

```
flaschplayer/
├── blinky.py              # Main display loop
├── blinky_bot.py          # Telegram bot
├── blinky_interface.py    # Flask web UI
├── entry_point.py         # Process launcher
├── programmatic_player.py # Standalone animation player
├── display.py             # NeoPixelDisplay / PyGameDisplay
├── layout.py              # LED index mapping
├── config.py              # Config dataclasses
├── thequeue.py            # GIF file queue
├── text_queue.py          # Text overlay queue
├── neopixel_debug.py      # Hardware LED test script
├── display_test.py        # PyGame colour-cycle smoke test
├── programs/              # Programmatic animation modules
│   ├── aurora.py
│   ├── clock.py
│   ├── flow_field.py
│   ├── kaleidoscope.py
│   ├── lissajous.py
│   ├── mandelbrot.py
│   ├── plasma.py
│   └── starfield.py
├── templates/             # Flask HTML templates
│   ├── landing.html
│   └── wait.html
├── tests/
│   └── test_layout.py
└── pyproject.toml
```

### Work directory (`WORK_DIR`)

Create this wherever you like (e.g. `/home/pi/flaschdata`):

```bash
WORK_DIR=/home/pi/flaschdata

mkdir -p $WORK_DIR/config_files
mkdir -p $WORK_DIR/gifs
mkdir -p $WORK_DIR/graveyard
mkdir -p $WORK_DIR/data/backgrounds/25_12/default
mkdir -p $WORK_DIR/data/backgrounds/25_12/chill
mkdir -p $WORK_DIR/data/backgrounds/25_12/disco
mkdir -p $WORK_DIR/data/backgrounds/25_12/rainbow

# Initialise the queue files
touch $WORK_DIR/queue.txt
touch $WORK_DIR/text_queue.txt
```

The background resolution directory name is `{width}_{height}` matching your
pixel resolution. For a 5×3 horizontal grid that is `25_12`.

---

## Configuration

All runtime configuration is provided via environment variables. The easiest
way to manage them is with [direnv](https://direnv.net/):

```bash
cp .envrc.example .envrc   # if provided, otherwise create manually
direnv allow
```

Or export them in your shell / systemd unit:

### Required variables

| Variable | Example | Description |
|----------|---------|-------------|
| `WORK_DIR` | `/home/pi/flaschdata` | Path to the work directory (see above) |
| `BOT_TOKEN` | `123456:ABC-...` | Telegram bot token from @BotFather |
| `AD_LINK` | `mybot` | Telegram username shown in periodic ad messages (`t.me/<AD_LINK>`) |
| `ROOT` | `987654321` | Your Telegram user ID — grants admin access to the bot |

### Optional variables

| Variable | Effect when set |
|----------|----------------|
| `NEOPIXEL` | Any non-empty value enables hardware output via NeoPixel. Unset → PyGame simulator |

### Persistent runtime settings

The following are stored in `$WORK_DIR/config_files/dumped_config` (JSON) and
updated automatically when changed via bot commands. They are not env vars.

| Setting | Default | Bot command |
|---------|---------|-------------|
| `brightness` | `1.0` (100%) | `/brightness <0–100>` |
| `text_speed` | `70` | `/text_speed <n>` |
| `mood` | `default` | `/mood <name>` |
| `playlistmode` | `mood` | `/mood` or `/play` |
| `adtime` | `1200` s | (edit source) |
| `allowed_ids` | `[ROOT]` | Send contact card to add/remove |

---

## Running the System

### Start everything

```bash
uv run python3 entry_point.py
```

`entry_point.py` is the single entry point for the full system. It launches:

| Component | Type | Description |
|-----------|------|-------------|
| `blinky.py` | Thread | Display loop — plays GIFs, scrolls text, drives LEDs |
| `blinky_bot.py` | Thread | Telegram bot — receives commands and media |
| `blinky_interface.py` | Process | Flask web UI on port 5000 |

`blinky_interface` runs as a separate OS process because Flask's development
server is not thread-safe. The other two components share memory as threads,
which is why `thequeue` and `text_queue` use file-based IPC to communicate
across the process boundary.

Press **Ctrl-C** or send **SIGTERM** to stop everything cleanly.

### Individual components (debug / development)

```bash
# Display loop only (requires WORK_DIR and background GIFs)
uv run python3 blinky.py

# Telegram bot only
uv run python3 blinky_bot.py

# Web interface only
uv run python3 blinky_interface.py
```

---

## Telegram Bot

### Setup

1. Message [@BotFather](https://t.me/BotFather) on Telegram
2. Send `/newbot` and follow the prompts
3. Copy the token into `BOT_TOKEN`
4. Find your Telegram user ID (message @userinfobot) and set `ROOT`

### Access control

Only users in the `allowed_ids` list can control the display.
The `ROOT` user is always in the list.

To grant access to another user: ask them to send their **contact card** to the
bot. The bot toggles them in/out of the allowed list.

### Commands

| Command | Who | Effect |
|---------|-----|--------|
| `/start` | Anyone | Greeting |
| `/help` | Anyone | Help message |
| `/brightness <0–100>` | Allowed | Set LED brightness percentage |
| `/text_speed <n>` | Allowed | Text scroll speed (higher = slower; default 70) |
| `/mood <name>` | Allowed | Switch playlist mood (`default`, `chill`, `disco`, `rainbow`) |
| `/play <pattern>` | Allowed | Play GIFs whose filename contains `<pattern>` |
| `/skip` | Allowed | Skip the current GIF immediately |

### Sending media

| What you send | What happens |
|---------------|-------------|
| MP4 / GIF file (≤20 MB) | Resized to display resolution and enqueued |
| Photo | Resized and enqueued as a still frame (shown 5 s) |
| Contact card | Admin toggles that user's access |
| Plain text | Scrolled as text overlay on the current GIF |

Files are resized by FFmpeg to `25x12` pixels and stored in
`$WORK_DIR/gifs/`. After playback they are moved to `$WORK_DIR/graveyard/`.

---

## Web Interface

The Flask app runs on **port 5000** of the Pi's IP address.

Open `http://<pi-ip>:5000` in a browser, type a message, and submit.
The text appears as a scrolling overlay on the current GIF within seconds.

No authentication is required by default — suitable for a local network kiosk.

---

## Programmatic Animations

The `programmatic_player.py` runs algorithmic animations without needing the
full bot/queue stack.

```bash
# Auto-discover and cycle through all programs
uv run python3 programmatic_player.py

# Start with a specific program
uv run python3 programmatic_player.py programs.plasma

# Custom box grid (10 wide × 4 tall = 50×16 pixels)
uv run python3 programmatic_player.py -x 10 -y 4

# Rotate display 90°
uv run python3 programmatic_player.py --rotate
```

In the PyGame window use **← → ↑ ↓** arrow keys to cycle programs.
Close the window or press **Ctrl-C** to exit.

### Available programs

| Program | Description |
|---------|-------------|
| `aurora` | Northern-lights colour waves |
| `clock` | Four clock visualisations cycling every 20 s |
| `flow_field` | Particles tracing a Perlin-noise vector field |
| `kaleidoscope` | Rotationally symmetric colour patterns |
| `lissajous` | Parametric Lissajous curves |
| `mandelbrot` | Zooming Mandelbrot set with rainbow colouring |
| `plasma` | Classic sine-wave plasma |
| `starfield` | Flying-through-stars effect |

### Writing a custom program

Create `programs/myprog.py`:

```python
def get_fps():
    return 30

def render(display, width, height, frame):
    for y in range(height):
        for x in range(width):
            r = int((x / width) * 255)
            g = int((y / height) * 255)
            b = int((frame % 256))
            display.set_xy(x, y, (r, g, b))
```

Run with:

```bash
uv run python3 programmatic_player.py programs.myprog
```

The player hot-reloads the module each time you switch to it with the arrow
keys, so edit-and-switch is instant.

---

## Development Mode (no hardware)

When `NEOPIXEL` is not set, all display output is rendered in a **PyGame
window** instead of driving physical LEDs. This works on any desktop.

```bash
# Full display smoke test — cycles solid colours
uv run python3 display_test.py

# Programmatic player in dev mode
uv run python3 programmatic_player.py

# blinky.py in dev mode (needs WORK_DIR and background GIFs)
uv run python3 blinky.py
```

The PyGame window pixel size is 50px per LED, so a 25×12 display appears as a
1250×600 px window.

---

## Running as a systemd Service

A template service file is at `config_files/blinky.service`.

1. Copy and edit it:

```bash
sudo cp config_files/blinky.service /etc/systemd/system/blinky.service
sudo nano /etc/systemd/system/blinky.service
```

Replace the placeholder paths and tokens:

```ini
[Unit]
Description=FlaschPlayer LED display

[Service]
Type=simple
WorkingDirectory=/home/pi/flaschplayer
ExecStart=/home/pi/flaschplayer/.venv/bin/python3 /home/pi/flaschplayer/entry_point.py
Restart=always
RestartSec=5
User=pi
Environment="WORK_DIR=/home/pi/flaschdata"
Environment="NEOPIXEL=1"
Environment="BOT_TOKEN=your-token-here"
Environment="AD_LINK=yourbotusername"
Environment="ROOT=your-telegram-id"

[Install]
WantedBy=multi-user.target
```

2. Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable blinky
sudo systemctl start blinky
sudo journalctl -u blinky -f   # follow logs
```

### NeoPixel permissions

The NeoPixel library requires raw GPIO access. The service runs as `root` by
default (see service file). If you prefer a non-root user, add the `gpio` and
`spi` groups and use `raspi-config` to enable SPI:

```bash
sudo adduser pi gpio
sudo raspi-config   # Interface Options → SPI → Enable
```

---

## Background GIF Library

Backgrounds are GIFs organised into mood subdirectories under:

```
$WORK_DIR/data/backgrounds/{width}_{height}/{mood}/
```

For a 25×12 display the path is `$WORK_DIR/data/backgrounds/25_12/`.

Built-in moods: `default`, `chill`, `disco`, `rainbow`.

Any GIF placed in a mood folder becomes part of that playlist. The bot command
`/mood chill` switches to the `chill` playlist. `/mood default` goes back to
the default.

### Preparing backgrounds

GIFs must be exactly `{width}×{height}` pixels. Resize with FFmpeg:

```bash
ffmpeg -i input.gif -s 25x12 -loop 0 output.gif
mv output.gif $WORK_DIR/data/backgrounds/25_12/default/
```

---

## Testing

```bash
# Run the layout test suite
uv run --group dev pytest

# Check types
uv run --group dev mypy layout.py blinky.py display.py config.py text_queue.py --ignore-missing-imports

# Colour-cycle display smoke test (opens PyGame window)
uv run python3 display_test.py

# Hardware LED test (Pi only — walks through colours LED by LED)
NEOPIXEL=1 uv run python3 neopixel_debug.py
```

---

## Troubleshooting

### `FileNotFoundError: No background with fitting resolution`

The background directory for your resolution doesn't exist or is empty.
Create it and add at least one GIF:

```bash
mkdir -p $WORK_DIR/data/backgrounds/25_12/default
ffmpeg -i some.gif -s 25x12 $WORK_DIR/data/backgrounds/25_12/default/bg.gif
```

### `KeyError: 'WORK_DIR'` (or `BOT_TOKEN`, `ROOT`, `AD_LINK`)

A required environment variable is not set. Export it or use direnv.

### NeoPixels not lighting up

- Confirm `NEOPIXEL` is set in the environment
- Check GPIO 18 wiring and the level shifter
- The service must run as `root` or the `gpio` group must be configured
- Test with: `sudo NEOPIXEL=1 uv run python3 neopixel_debug.py`

### Display looks mirrored or upside down

Adjust `fliplr` / `flipud` / `rotate_90` in your `blinky.py` call to `init()`
or pass `--rotate` to `programmatic_player.py`. The correct values depend on
how you physically mounted and wired the LED matrix.

### Telegram bot not responding

- Check `BOT_TOKEN` is correct
- Confirm the Pi has outbound internet access on port 443
- Check logs: `journalctl -u blinky -n 100`

### PyGame window doesn't open

Ensure a display is connected or `DISPLAY` is set. On a headless Pi, use
`Xvfb` or run display-related commands on your desktop instead.

### Text doesn't scroll

- Check the `letter/` directory exists in `WORK_DIR` and contains the `thin4_*.png` font files
- `text_queue.txt` must exist in `WORK_DIR` (created automatically by `setup()`)
