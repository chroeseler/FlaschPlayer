import json
import logging
from pathlib import Path

from PIL import Image
from filelock import FileLock

from config import Constants

queue_txt = f"{Constants.work_dir}/text_queue.txt"
lock = FileLock(f"{queue_txt}.lock")

logger = logging.getLogger(__name__)
LETTERS = Path(f'{Constants.work_dir}/letter')


def setup():
    open(queue_txt, "a").write("")


def put(text: str):
    def add_char_coord(char, width, t_char):
        if ord(char) == 32:
            return t_char, width + 3
        char_dict = get_coords(char)
        if char_dict:
            for coords in char_dict['dots']:
                t_char.append([coords[0] + width, coords[1]])
            width += char_dict['size'][0]
        return t_char, width + 1

    logger.info('Adding "%s" to text queue', text)
    text_matrix = []
    text_width = 0
    for character in text:
        text_matrix, text_width = add_char_coord(character, text_width, text_matrix)
    if text_width > 0:
        with lock:
            with open(queue_txt, 'a') as f:
                json.dump(text_matrix, f)
                f.write('\n')


def has_items():
    # TODO check empty file
    with open(queue_txt, 'r') as fin:
        return fin.readline()


def pop():
    with lock:
        with open(queue_txt, 'r+') as f:  # open file in read / write mode
            first_line = f.readline()  # read the first line and throw it out
            data = f.read()  # read the rest
            f.seek(0)  # set the cursor to the top of the file
            f.write(data)  # write the data back
            f.truncate()  # set the file size to the current size
            return json.loads(first_line)


def dotting(path: Path):
    img = Image.open(path)
    dots = img.convert('L')
    letter_matrix = {'dots': []}
    furthest_x = 0
    for x in range(img.size[0]):
        for y in range(img.size[1]):
            g_scale_value = dots.getpixel((x, y))
            if g_scale_value > 100:
                furthest_x = x
                letter_matrix['dots'].append((x, y + 1))

    letter_matrix['size'] = (furthest_x, dots.size[1])
    return letter_matrix


def get_coords(char: str):
    try:
        return dotting(LETTERS.joinpath('thin4_' + '{:05d}'.format(ord(char)) + '.png'))
    except FileNotFoundError:
        logger.info('Letter not found')
        return None
