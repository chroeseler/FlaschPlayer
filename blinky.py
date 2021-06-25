"""Blinky: Main contributer to FlaschPlayer"""
import time
import os
import sys
import random
import glob
import ast
import board
import display
from PIL import Image, ImageSequence
from filelock import FileLock
import layout
import config


def display_gif(strip, matrix, path_to_gif, display_resolution, lock):
    """Main action point

    The methods takes the background gif and sets frame by frame
    every pixel. After every frame the strip.show() method is called.
    Also the waiting list is checked. If a gif is in the list
    it will be displayed immediately. This repeats until no further
    gifs are in line"""


    def update_line(lock):
        with lock:
            with open(config.waiting_line, 'r') as f:
                line = f.read()
                if len(line) > 1:
                    print(f'waiting line: {line}')
                waiting_line = ast.literal_eval('[' + line[:-1] + ']')
            with open(config.waiting_line, 'w') as f:
                f.write('')
        return waiting_line


    def draw_frame(frame, display_resolution, bright):
        rgb_frame = frame.convert('RGB')
        for y in range(display_resolution[1]):
            for x in range(display_resolution[0]):
                print(f'x: {x}, y: {y}')
                strip.set_xy(x,y, tuple(int(x * bright) for x in rgb_frame.getpixel((x, y))))
        strip.show()
        if 'duration' in frame.info:
            if isinstance(frame.info['duration'], int):
                time.sleep(frame.info['duration']/1000)
            else:
                time.sleep(0.1)
        else:
            time.sleep(0.1)


    background_gif = Image.open(path_to_gif + '.gif')
    print(f'Back: {path_to_gif}.gif')
    if (background_gif.size[0] < display_resolution[0] or
            background_gif.size[1] < display_resolution[1]):
        #fallback gif should be placed if the background is wrongly composed
        background_gif = Image.open(f'{config.work_dir}/config/fallback.gif')

    #pylint: disable=too-many-nested-blocks
    for frame in ImageSequence.Iterator(background_gif):
        bright = set_brightness()
        draw_frame(frame, display_resolution, bright)
        waiting_line = update_line(lock)
        while waiting_line:
            for media in waiting_line:
                bright = set_brightness()
                foreground_gif = Image.open(f'{config.work_dir}/gifs/{media}.gif')
                print(f'Front: {media}.gif')
                if 'duration' in foreground_gif.info:
                    #Adding the durations of every frame until at least 5 sec runtime
                    runtime = 0
                    while runtime <= 5000:
                        #pylint: disable=redefined-outer-name
                        for frame in ImageSequence.Iterator(foreground_gif):
                            runtime += frame.info['duration']
                            draw_frame(frame, display_resolution, bright)
                else:
                    #photos in gif container get shown 5 seconds
                    for _ in range(50):
                        draw_frame(foreground_gif, display_resolution, bright)
                os.rename(f'{config.work_dir}/gifs/{media}.gif',
                          f'{config.work_dir}/graveyard/{time.time()}.gif')
            waiting_line = update_line(lock)


def set_brightness():
    """Lists all files in config folder and extracts the option from
    the file name."""
    options = [f for f in files(f"{config.work_dir}/config/")]
    try:
        brightness = float([i for i in options if 'BRIGHTNESS' in i][0][11:])
    except ValueError:
        brightness = 1.0
        print(f'ERROR: Reset Brightness: {brightness}')
    except:
        brightness = 1.0
        print("Something broken, should fix some time")
    return brightness


def debug(delay, x_boxes=5, y_boxes=3, bright=1.0):
    """Debug Mode to test all RGB colors at any led"""
    display_resolution, strip, matrix, led_count = init(x_boxes, y_boxes, bright, n_led=True)
    # strip = neopixel.NeoPixel(board.D18, led_count, brightness=bright, auto_write=True)
    strip = display.MockDisplay(led_count)
    try:
        while True:
            for i in range(led_count):
                strip[i] = (255, 255, 255)
                time.sleep(delay)
            for i in range(led_count):
                strip[i] = (255, 0, 0)
                time.sleep(delay)
            for i in range(led_count):
                strip[i] = (0, 255, 0)
                time.sleep(delay)
            for i in range(led_count):
                strip[i] = (0, 0, 255)
                time.sleep(delay)
    except KeyboardInterrupt:
        for y in range(display_resolution[1]):
            for x in range(display_resolution[0]):
                #It's not a bug it's a feature
                strip.set_xy(x,y,(0,0,0))
                #strip[matrix[y][x]] = (0, 0, 0)



def files(path):
    """generator object to list files in folder(config)"""
    for file in os.listdir(path):
        if os.path.isfile(os.path.join(path, file)):
            yield file


def init(x_boxes, y_boxes, brightness=1, n_led=False):
    """initializing the strip and calclate the mapping"""
    led_count = x_boxes * y_boxes * 20
    display_resolution = (x_boxes * 4, y_boxes * 5)

    #Setup LED stripe
    #strip = neopixel.NeoPixel(board.D18, led_count, brightness=brightness, auto_write=False)
    strip = display.NeoPixelDisplay(led_count, x_boxes, y_boxes)

    #Setup Display Matrix
    #matrix[y][x] = led_id
    matrix = layout.full_layout(x_boxes, y_boxes, vert=True)
    with open(config.waiting_line, 'w') as f:
        f.write('')
    if n_led:
        return display_resolution, strip, matrix, led_count
    else:
        return display_resolution, strip, matrix


def main(x_boxes=5, y_boxes=3):
    """initializing folders, filelock, background gifs and runing the display"""

    display_resolution, strip, matrix = init(x_boxes, y_boxes)


    #Setup Media Wait list

    os.makedirs(f"{config.work_dir}/graveyard", exist_ok=True)
    # os.chown(f"{config.work_dir}/graveyard", uid=1000, gid=1000)
    os.makedirs(f"{config.work_dir}/gifs", exist_ok=True)
    # os.chown(f"{config.work_dir}/gifs", uid=1000, gid=1000)

    lock = FileLock(config.waiting_line_lock, timeout=5)
    mylist = [f[:-4] for f in glob.glob(f"{config.work_dir}/backgrounds/*.gif")]

    while mylist:
        display_gif(strip, matrix, random.choice(mylist), display_resolution, lock)

    if not mylist:
        sys.exit(f"No gif in {config.work_dir}/backgrounds")

if __name__ == '__main__':
    print('############################################')
    print('Starting Blinky')
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
