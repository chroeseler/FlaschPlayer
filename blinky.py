"""Blinky: Main contributor to FlaschPlayer"""
import glob
import logging
import os
import random
import sys
import threading
import time
from collections.abc import Generator, Iterator
from pathlib import Path
from typing import cast

from apscheduler.schedulers.background import BackgroundScheduler
from PIL import Image, ImageSequence

import display as d
from display import Display
import text_queue as txt_q
import thequeue as q
from config import Constants, Main_Options as Options

logger = logging.getLogger("blinky.led")

SKIP = Path(f'{Constants.work_dir}/config_files/skip')


class GifPlayer:
    """Plays GIF files and background images on a Display.

    Encapsulates per-play state (text overlay generator, ad timer) so that
    text scrolls smoothly across GIF transitions without leaking globals.
    """

    def __init__(self, display: Display, display_resolution: tuple[int, int]) -> None:
        self._display = display
        self._resolution = display_resolution
        self._text_gen: Iterator | None = None
        self._scheduler = BackgroundScheduler()
        self._scheduler.add_job(
            self._enqueue_ad,
            trigger='interval',
            seconds=Options.adtime,
            id='ad',
        )
        self._scheduler.start()

    def _enqueue_ad(self) -> None:
        txt_q.put(f'Write me at t.me/{Constants.ad_link}')

    def stop(self) -> None:
        self._scheduler.shutdown(wait=False)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def play(self, filepath: str) -> None:
        self._filepath = filepath
        self._draw_gif(filepath)

    # ------------------------------------------------------------------
    # Frame rendering
    # ------------------------------------------------------------------

    def _draw_frame(self, frame: Image.Image) -> None:
        rgb_frame = frame.convert('RGB')
        txt = self._get_text()
        for y in range(self._resolution[1]):
            for x in range(self._resolution[0]):
                pixel = cast(tuple[int, int, int], rgb_frame.getpixel((x, y)))
                if not txt:
                    self._display.set_xy(x, y, pixel)
                else:
                    new_rgb = tuple(ch * 0.15 for ch in pixel)
                    self._display.set_xy(x, y, new_rgb)
        if txt:
            self._write_text(txt)
        if self._display.is_running():
            self._display.show()
        else:
            logger.warning("display.show() called but display not running")
        if 'duration' in frame.info:
            if isinstance(frame.info['duration'], int):
                if frame.info['duration'] > 100:
                    time.sleep((frame.info['duration'] - 100) / 1000)

    def _write_text(self, text) -> None:
        if not text:
            return
        for coord in text:
            if coord[0] < self._resolution[0]:
                self._display.set_xy(coord[0], coord[1], (255, 255, 255))

    # ------------------------------------------------------------------
    # Text overlay state machine
    # ------------------------------------------------------------------

    def _get_text(self):
        if not self._text_gen and txt_q.has_items():
            text = txt_q.pop()
            self._text_gen = self._text_generator(text, self._resolution)
            return next(self._text_gen, None)
        elif self._text_gen is not None:
            text = next(self._text_gen, None)
            if text:
                return text
            self._text_gen = None
        return None

    def _text_generator(
        self,
        text: list[list[int]],
        screen_resolution: tuple[int, int],
    ) -> Generator:
        """Shifts text dots one x-column per text_speed frames until all are off screen."""
        frame_counter = 0
        for dot in range(len(text)):
            text[dot][0] += screen_resolution[0]
        while text:
            frame_counter += 1
            if frame_counter % Options.text_speed != 0:
                yield text
            else:
                remove = []
                for dot in range(len(text)):
                    if text[dot][0] == 0:
                        remove.append(text[dot])
                    else:
                        text[dot][0] -= 1
                text = [x for x in text if x not in remove]
                yield text

    # ------------------------------------------------------------------
    # GIF lifecycle helpers
    # ------------------------------------------------------------------

    def _is_background(self) -> bool:
        return "backgrounds" in self._filepath

    def _should_abort(self) -> bool:
        if SKIP.exists():
            os.remove(SKIP)
            return True
        return self._is_background() and q.has_items()

    def _show_photo(self, image: Image.Image) -> None:
        for _ in range(50):
            self._draw_frame(image)

    def _loop_gif(self, image: Image.Image, duration: int) -> None:
        runtime = 0
        while runtime <= duration and not self._should_abort() and self._display.is_running():
            for frame in ImageSequence.Iterator(image):
                self._display.set_brightness()
                if not self._display.is_running():
                    break
                runtime += frame.info['duration']
                self._draw_frame(frame)
                if self._should_abort():
                    break

    def _bury_in_graveyard(self) -> None:
        os.rename(self._filepath, f'{Constants.work_dir}/graveyard/{time.time()}.gif')

    def _draw_gif(self, gif_path: str) -> None:
        total_loop_duration = 500
        logger.info('Playing: %s', gif_path)
        img = Image.open(gif_path)
        if 'duration' in img.info:
            self._loop_gif(img, total_loop_duration)
        else:
            self._show_photo(img)

        if not self._is_background():
            logger.info("Moving to graveyard: %s", gif_path)
            self._bury_in_graveyard()


def init(x_boxes: int, y_boxes: int, rotate_90: bool) -> tuple[tuple[int, int], Display]:
    led_count = x_boxes * y_boxes * 20
    x_res, y_res = (x_boxes * 5, y_boxes * 4) if not rotate_90 else (x_boxes * 4, y_boxes * 5)
    display_resolution = (x_res, y_res)

    display: Display
    if Constants.use_neopixel:
        logger.info("Setting up NeoPixel display")
        display = d.NeoPixelDisplay(led_count, x_boxes, y_boxes, rotate_90)
    else:
        logger.info("Setting up PyGame Debug display")
        display = d.PyGameDisplay(x_res, y_res, 50)

    return display_resolution, display


def matches_pattern(filepath: str, pattern: str) -> bool:
    filepath = filepath.lower()
    tokens = pattern.lower().split(" ")
    matches = True
    for token in tokens:
        if token not in filepath:
            matches = False
    return matches


def main(pill: threading.Event = threading.Event(), x_boxes: int = 5, y_boxes: int = 3, rotate_90: bool = False) -> None:
    display_resolution, display = init(x_boxes, y_boxes, rotate_90)
    res_str = f'{display_resolution[0]}_{display_resolution[1]}'
    if not os.path.isdir(f"{Constants.work_dir}/data/backgrounds/{res_str}/"):
        raise FileNotFoundError(f'No background with fitting resolution available at {Constants.work_dir}/data/backgrounds/{res_str}/')

    os.makedirs(f"{Constants.work_dir}/graveyard", exist_ok=True)
    os.makedirs(f"{Constants.work_dir}/gifs", exist_ok=True)

    player = GifPlayer(display, display_resolution)
    try:
        _run_loop(player, display, display_resolution, pill, res_str)
    finally:
        player.stop()


def _run_loop(
    player: GifPlayer,
    display: Display,
    display_resolution: tuple[int, int],
    pill: threading.Event,
    res_str: str,
) -> None:
    while display.is_running() and not pill.is_set():
        if not (next_gif := q.take()):
            mood = Options.mood
            pattern = Options.pattern
            if Options.playlistmode == "mood":
                backgrounds = glob.glob(f"{Constants.work_dir}/data/backgrounds/{res_str}/{mood}/*.gif")
            else:
                backgrounds = glob.glob(f"{Constants.work_dir}/data/backgrounds/{res_str}/*/*.gif")
                backgrounds = list(filter(lambda f: matches_pattern(f, pattern), backgrounds))
                if not backgrounds:
                    logger.warning("No gif in %s/data/%s/backgrounds/%s or %s/gifs", Constants.work_dir, res_str, mood, Constants.work_dir)
                    backgrounds = glob.glob(f"{Constants.work_dir}/data/backgrounds/{res_str}/default/*.gif")
            next_gif = random.choice(backgrounds)
        try:
            player.play(next_gif)
        except KeyboardInterrupt:
            logger.info("Interrupted, exit, over and out")
            sys.exit()
        except AttributeError:
            logger.exception('Background gifs setup failed. Check folders')
            time.sleep(2)


def debug(x_boxes: int = 5, y_boxes: int = 3, rotate_90: bool = False) -> None:
    _resolution, display = init(x_boxes, y_boxes, rotate_90)
    cast(d.NeoPixelDisplay, display).run_debug()


if __name__ == '__main__':
    logger.info('#####  blinky   ###########################')
    import argparse

    PARSER = argparse.ArgumentParser()
    PARSER.add_argument("-d", "--debug", action="store_true", default=False,
                        help="debug mode")
    PARSER.add_argument("-dl", "--delay", type=float, default=0.01,
                        help="delay between set")
    PARSER.add_argument("-b", "--brightness", type=float, default=1.0,
                        help="Set brightness")
    PARSER.add_argument("-r", "--rotate", type=float, default=False,
                        help="Set box rotation to vertical")
    ARGS = PARSER.parse_args()

    if ARGS.debug:
        debug(1, 1)
    elif ARGS.rotate:
        main(rotate_90=True)
    else:
        main()
