"""Blinky: Main contributer to FlaschPlayer"""
import glob
import logging
import os
import random
import sys
import time
from pathlib import Path

from PIL import Image, ImageSequence

import config
import display as d
import text_queue as txt_q
import thequeue as q

logger = logging.getLogger("blinky.led")

TEXT = None
SKIP = Path(f'{config.work_dir}/config/skip')


def display_gif(display, filepath, display_resolution):
    """Main action point

    The methods takes the background gif and sets frame by frame
    every pixel. After every frame the display.show() method is called.
    Also the waiting list is checked. If a gif is in the list
    it will be displayed immediately. This repeats until no further
    gifs are in line"""

    def draw_frame(frame):
        rgb_frame = frame.convert('RGB')
        txt = get_text()
        for y in range(display_resolution[1]):
            for x in range(display_resolution[0]):
                if not txt:
                    display.set_xy(x, y, rgb_frame.getpixel((x, y)))
                else:
                    old_rgb = list(rgb_frame.getpixel((x, y)))
                    new_rgb = tuple([x * 0.15 for x in old_rgb])
                    display.set_xy(x, y, new_rgb)
        if txt:
            write_text(txt, display_resolution)
        if display.is_running():
            display.show()
        else:
            logger.warning("display.show() called but display not running")
        if 'duration' in frame.info:
            if isinstance(frame.info['duration'], int):
                if frame.info['duration'] > 100:
                    time.sleep((frame.info['duration'] - 100) / 1000)

    def write_text(text, display_resolution):
        for coord in text:
            if coord[0] < display_resolution[0]:
                display.set_xy(coord[0], coord[1], (255, 255, 255))

    def get_text():
        global TEXT
        if not TEXT and txt_q.has_items():
            text = txt_q.pop()
            TEXT = text_generator(text, display_resolution)
            text = next(TEXT, None)
            return text
        elif TEXT is not None:
            text = next(TEXT, None)
            if text:
                return text
            else:
                TEXT = None
                return None

    def text_generator(text, display_resolution):
        """The generator gets a list with the dot coordinates of the text letters.
        They all get moved on the x axis to the be outside on the of the display
        and then get moved back one x coordinate per yield. If an x coordinate reaches 0
        it gets removes from the list. The generator stops if the list is empty"""
        frame_counter = 0
        for dot in range(len(text)):
            text[dot][0] += display_resolution[0]
        while text:
            frame_counter += 1
            if frame_counter % config.text_speed.get() != 0:
                yield text
            else:
                remove = []
                for dot in range(len(text)):
                    if text[dot][0] == 0:
                        remove.append(text[dot])
                    else:
                        text[dot][0] -= 1
                text = [x for x in text if (x not in remove)]
                yield text

    def bury_in_graveyard():
        os.rename(filepath, f'{config.work_dir}/graveyard/{time.time()}.gif')

    def show_photo(image):
        # photos in gif container get shown 5 seconds
        for _ in range(50):
            draw_frame(image)

    def is_background():
        return "backgrounds" in filepath

    def should_abort():
        if SKIP.exists():
            os.remove(SKIP)
            return True
        return is_background() and q.has_items()

    def loop_gif(image, duration):
        runtime = 0
        while runtime <= duration and not should_abort() and display.is_running():
            for frame in ImageSequence.Iterator(image):
                display.set_brightness()
                if not display.is_running():
                    break
                runtime += frame.info['duration']
                draw_frame(frame)
                if should_abort():
                    break

    def draw_gif(filepath):
        total_loop_duration = 500
        logger.info('Playing: %s', filepath)
        img = Image.open(filepath)
        if 'duration' in img.info:
            # Adding the durations of every frame until at least 5 sec runtime
            loop_gif(img, total_loop_duration)
        else:
            show_photo(img)

        if not is_background():
            logger.info("Moving to graveyard: %s", filepath)
            bury_in_graveyard()

    draw_gif(filepath)


# periodically fetch brightness setting from file in config/

# def set_brightness():
#     """Lists all files in config folder and extracts the option from
#     the file name."""
#     options = [f for f in files(f"{config.work_dir}/config/")]
#     try:
#         brightness = float([i for i in options if 'BRIGHTNESS' in i][0][11:])
#     except ValueError:
#         brightness = 1.0
#         logger.error(f'ERROR: Reset Brightness: {brightness}')
#     except:
#         brightness = 1.0
#         logger.error("Something broken, should fix some time")
#     return brightness


def files(path):
    for file in os.listdir(path):
        if os.path.isfile(os.path.join(path, file)):
            yield file


def init(x_boxes: int, y_boxes: int, rotate_90: bool):
    led_count = x_boxes * y_boxes * 20
    x_res, y_res = (x_boxes * 5, y_boxes * 4) if not rotate_90 else (x_boxes * 4, y_boxes * 5)
    display_resolution = (x_res, y_res)

    if config.use_neopixel:
        display = d.NeoPixelDisplay(led_count, x_boxes, y_boxes, rotate_90)
    else:
        display = d.PyGameDisplay(x_res, y_res, 50)

    return display_resolution, display, led_count


def matches_pattern(filepath, pattern):
    filepath = filepath.lower()
    tokens = pattern.lower().split(" ")
    matches = True
    for token in tokens:
        if token not in filepath:
            matches = False
    return matches


def main(x_boxes: int=5, y_boxes: int=3, rotate_90:bool=False) -> None:
    display_resolution, display, _ = init(x_boxes, y_boxes, rotate_90)
    res_str = f'{display_resolution[0]}_{display_resolution[1]}'
    if not os.path.isdir(f"{config.work_dir}/backgrounds/{res_str}/"):
        raise FileNotFoundError(f'No background with fitting resolution availabel at {config.work_dir}/backgrounds/{res_str}/')
    # Setup Media Wait list

    os.makedirs(f"{config.work_dir}/graveyard", exist_ok=True)
    # os.chown(f"{config.work_dir}/graveyard", uid=1000, gid=1000)
    os.makedirs(f"{config.work_dir}/gifs", exist_ok=True)
    # os.chown(f"{config.work_dir}/gifs", uid=1000, gid=1000)

    while display.is_running():
        if not (next_gif := q.take()):
            mood = config.mood.get()
            pattern = config.pattern.get()
            if config.playlistmode.get() == "mood":
                backgrounds = glob.glob(f"{config.work_dir}/backgrounds/{res_str}/{mood}/*.gif")
            else:
                backgrounds = glob.glob(f"{config.work_dir}/backgrounds/{res_str}/*/*.gif")
                backgrounds = list(filter(lambda f: matches_pattern(f, pattern), backgrounds))
                if not backgrounds:
                    logger.exception("No gif in %s/backgrounds/%s or %s/gifs", config.work_dir, mood, config.work_dir)
                    backgrounds = glob.glob(f"{config.work_dir}/backgrounds/{res_str}/default/*.gif")
            next_gif = random.choice(backgrounds)
        try:
            display_gif(display, next_gif, display_resolution)
        except KeyboardInterrupt:
            logger.info("Interrupted, exit, over and out")
            sys.exit()
        except AttributeError:
            logger.exception('Background gifs setup failed. Check folders')
            time.sleep(2)


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
        print('No debug mode implemented atm')
    elif ARGS.rotate:
        main(rotate_90=True)
    else:
        main()

