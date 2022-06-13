from filelock import Timeout, FileLock
import logging
import config
import numpy as np
import letters
import json

queue_txt = f"{config.work_dir}/text_queue.txt"
lock = FileLock(f"{queue_txt}.lock")

logger = logging.getLogger(__name__)

def setup():
    open(queue_txt,"a").write("")

def put(text):
    def add_char_coord(char, width, text):
        if (char_dict := letters.get_coords(char)):
            for coords in char_dict['dots']:
                text.append([coords[0]+width, coords[1]])
            width += char_dict['size'][0]
        return text, width

    logger.info(text)
    text_matrix = []
    width = 0
    for character in text:
        text_matrix, width = add_char_coord(character, width, text_matrix)
    if width > 0:
        with lock:
            with open(queue_txt, 'a') as f:
                json.dump(text_matrix, f)
                f.write('\n')

def has_items():
    #TODO check empty file
    with open(queue_txt, 'r') as fin:
        return fin.readline()

def pop():
    with lock:
        with open(queue_txt, 'r+') as f: # open file in read / write mode
            firstLine = f.readline() # read the first line and throw it out
            data = f.read() # read the rest
            f.seek(0) # set the cursor to the top of the file
            f.write(data) # write the data back
            f.truncate() # set the file size to the current size
            return json.loads(firstLine)

