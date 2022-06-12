from filelock import Timeout, FileLock
import logging
import config
import numpy as np
import letters

queue_txt = f"{config.work_dir}/text_queue.txt"
lock = FileLock(f"{queue_txt}.lock")

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger("blinky.text_queue")
logging.getLogger("filelock").setLevel(logging.WARN)

def setup():
    open(queue_txt,"a").write("")

def put(text):
    def add_char_coord(char, width, text):
        char_dict = letters.dotting(char)
        for coords in char_dict['dots']:
            text.append([coords(0)+width, coords(1)])
        width += char_dict['size'][0]
        return text, width

    text_matrix = []
    width = 0
    for character in text:
        text_matrix, width = add_char_coord(character, width, text_matrix)
    with lock:
        with open(queue_txt, 'a') as f:
            f.write(str(text_matrix) + '\n')

def has_items():
    #TODO check empty file
    with open(queue_txt, 'r') as fin:
        return fin.readline()

def pop(file):
    with open(file, 'r+') as f: # open file in read / write mode
        firstLine = f.readline() # read the first line and throw it out
        data = f.read() # read the rest
        f.seek(0) # set the cursor to the top of the file
        f.write(data) # write the data back
        f.truncate() # set the file size to the current size
        return firstLine



def take():
    with lock:
        with open(queue_txt, 'r') as fin:
            data = fin.read().splitlines(True)
        with open(queue_txt, 'w') as fout:
            fout.writelines(data[1:])
        if data:
            logger.info("Took: %s", data[0].strip())
            return data[0].strip()
        else:
            logger.info("No item in queue")
            return None
