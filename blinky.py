"""Blinky: Main contributer to FlaschPlayer"""
import time
import os
import logging
import sys
import random
import glob
import ast
import board
import display as d
from PIL import Image, ImageSequence
import layout
import config

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger("blinky.led")

def get_next_in_waiting_line():
    # TODO order waiting_line by something
    print("queue", glob.glob(f"{config.work_dir}/gifs/*.gif"))
    return next(iter(glob.glob(f"{config.work_dir}/gifs/*.gif")), False)

def display_gif(display, filepath, display_resolution):
    """Main action point

    The methods takes the background gif and sets frame by frame
    every pixel. After every frame the display.show() method is called.
    Also the waiting list is checked. If a gif is in the list
    it will be displayed immediately. This repeats until no further
    gifs are in line"""


    def draw_frame(frame, display_resolution):
        rgb_frame = frame.convert('RGB')
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
                time.sleep(0.1)
        else:
            time.sleep(0.1)

            time.sleep(0.05)

    def bury_in_graveyard():
        os.rename(filepath, f'{config.work_dir}/graveyard/{time.time()}.gif')

    def show_photo(image):
        # photos in gif container get shown 5 seconds
        for _ in range(50):
            draw_frame(image)

    def is_background():
        return "backgrounds" in filepath

    def should_abort():
        return is_background() and get_next_in_waiting_line()

    def loop_gif(image, duration):
        runtime = 0
        while runtime <= duration and not should_abort():
            for frame in ImageSequence.Iterator(image):
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


# TODO implement this as method on NeoPixelDisplay implementation
#def debug(delay, x_boxes=5, y_boxes=3, bright=1.0):
#    """Debug Mode to test all RGB colors at any led"""
#    display_resolution, strip, led_count = init(x_boxes, y_boxes, bright, n_led=True)
#    # strip = neopixel.NeoPixel(board.D18, led_count, brightness=bright, auto_write=True)
#    strip = display.MockDisplay(led_count)
#    try:
#        while True:
#            for i in range(led_count):
#                strip[i] = (255, 255, 255)
#                time.sleep(delay)
#            for i in range(led_count):
#                strip[i] = (255, 0, 0)
#                time.sleep(delay)
#            for i in range(led_count):
#                strip[i] = (0, 255, 0)
#                time.sleep(delay)
#            for i in range(led_count):
#                strip[i] = (0, 0, 255)
#                time.sleep(delay)
#    except KeyboardInterrupt:
#        for y in range(display_resolution[1]):
#            for x in range(display_resolution[0]):
#                #It's not a bug it's a feature
#                strip.set_xy(x,y,(0,0,0))



def files(path):
    """generator object to list files in folder(config)"""
    for file in os.listdir(path):
        if os.path.isfile(os.path.join(path, file)):
            yield file


def init(x_boxes, y_boxes, brightness=1, n_led=False):
    """initializing the display"""
    led_count = x_boxes * y_boxes * 20
    x_res, y_res = (x_boxes * 4, y_boxes * 5)
    display_resolution = (x_res, y_res)

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
            next_gif = get_next_in_waiting_line() or random.choice(backgrounds)
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
