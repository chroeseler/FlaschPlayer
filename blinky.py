"""Blinky: Main contributer to FlaschPlayer"""
import time
import os
import logging
import sys
import random
import glob
import ast
import board
import thequeue as q
import display as d
from PIL import Image, ImageSequence
import layout
import config

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger("blinky.led")

def display_gif(display, filepath, display_resolution):
    """Main action point

    The methods takes the background gif and sets frame by frame
    every pixel. After every frame the display.show() method is called.
    Also the waiting list is checked. If a gif is in the list
    it will be displayed immediately. This repeats until no further
    gifs are in line"""


    def draw_frame(frame):
        rgb_frame = frame.convert('RGB')
        default_frame_rate = 0.1
        for y in range(display_resolution[1]):
            for x in range(display_resolution[0]):
                display.set_xy(x,y, rgb_frame.getpixel((x, y)))
        if display.is_running():
            display.show()
        else:
            logger.warning("display.show() called but display not running")
        if 'duration' in frame.info:
            if isinstance(frame.info['duration'], int):
                time.sleep(frame.info['duration']/1000)
            else:
                time.sleep(default_frame_rate)
        else:
            time.sleep(default_frame_rate)

    def bury_in_graveyard():
        os.rename(filepath, f'{config.work_dir}/graveyard/{time.time()}.gif')

    def show_photo(image):
        # photos in gif container get shown 5 seconds
        for _ in range(50):
            draw_frame(image)

    def is_background():
        return "backgrounds" in filepath

    def should_abort():
        return is_background() and q.has_items()

    def loop_gif(image, duration):
        runtime = 0
        while runtime <= duration and not should_abort() and display.is_running():
            display.set_brightness()
            for frame in ImageSequence.Iterator(image):
                if not display.is_running():
                    break
                runtime += frame.info['duration']
                draw_frame(frame)
                if should_abort():
                    break

    def draw_gif(path):
        total_loop_duration = 5000
        logger.info(f'Playing: {filepath}')
        img = Image.open(filepath)
        if 'duration' in img.info:
            #Adding the durations of every frame until at least 5 sec runtime
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
    """generator object to list files in folder(config)"""
    for file in os.listdir(path):
        if os.path.isfile(os.path.join(path, file)):
            yield file


def init(x_boxes, y_boxes, n_led=False):
    """initializing the display"""
    led_count = x_boxes * y_boxes * 20
    x_res, y_res = (x_boxes * 4, y_boxes * 5)
    display_resolution = (x_res, y_res)

    if config.use_neopixel:
        display = d.NeoPixelDisplay(led_count, x_boxes, y_boxes)
    else:
        display = d.PyGameDisplay(x_res, y_res, 50)

    # TODO set_brightness for display based on argument

    if n_led:
        return display_resolution, display, led_count
    else:
        return display_resolution, display


def main(x_boxes=5, y_boxes=3):
    """initializing folders, background gifs and runing the display"""

    display_resolution, display = init(x_boxes, y_boxes)

    #Setup Media Wait list

    os.makedirs(f"{config.work_dir}/graveyard", exist_ok=True)
    # os.chown(f"{config.work_dir}/graveyard", uid=1000, gid=1000)
    os.makedirs(f"{config.work_dir}/gifs", exist_ok=True)
    # os.chown(f"{config.work_dir}/gifs", uid=1000, gid=1000)

    while display.is_running():
        waiting_line = glob.glob(f"{config.work_dir}/gifs/*.gif")
        backgrounds = glob.glob(f"{config.work_dir}/backgrounds/*.gif")
        try:
            next_gif = q.take() or random.choice(backgrounds)
        except:
            logger.error(f"No gif in {config.work_dir}/backgrounds or {config.work_dir}/gifs")
            sys.exit(1)

        display_gif(display, next_gif, display_resolution)

if __name__ == '__main__':
    logger.info('############################################')
    logger.info('Starting Blinky')
    import argparse
    PARSER = argparse.ArgumentParser()
    PARSER.add_argument("-d", "--debug", action="store_true", default=False,
                        help="debug mode")
    PARSER.add_argument("-dl", "--delay", type=float, default=0.01,
                        help="delay between set")
    PARSER.add_argument("-b", "--brightness", type=float, default=1.0,
                        help="Set brightness")
    ARGS = PARSER.parse_args()


    if not ARGS.debug:
        main()
    elif ARGS.debug:
        debug(ARGS.delay)
