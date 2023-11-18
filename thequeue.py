import logging
import os

from filelock import FileLock

from config import main_constants as Constants

queue_txt = f"{Constants.work_dir}/queue.txt"
lock = FileLock(f"{queue_txt}.lock")

logger = logging.getLogger("blinky.queue")
logging.getLogger("filelock").setLevel(logging.WARN)

def setup() -> None:
    with open(queue_txt,"a", encoding='utf-8') as fl:
        fl.write("")

def mark_ready(path: str) -> None:
    with lock:
        logger.info("Queuing: %s", path)
        with open(queue_txt, "a", encoding='utf-8') as fl:
            fl.write(path + "\n")

def has_items() -> bool:
    if os.stat(queue_txt).st_size == 0:
        return False
    return True

def take():
    with lock:
        if not has_items():
            logger.info('Queue is empty')
            return None
        with open(queue_txt, 'r', encoding='utf-8') as fin:
            data = fin.read().splitlines(True)
        with open(queue_txt, 'w', encoding='utf-8') as fout:
            if len(data) == 1:
                fout.write('')
            else:
                fout.writelines(data[1:])
        return data[0].strip()
