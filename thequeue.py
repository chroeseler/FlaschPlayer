from filelock import Timeout, FileLock
import logging
import config

queue_txt = f"{config.work_dir}/queue.txt"
lock = FileLock(f"{queue_txt}.lock")

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger("blinky.queue")
logging.getLogger("filelock").setLevel(logging.WARN)

open(queue_txt,"a").write("")

def mark_ready(path):
    with lock:
        logger.info("Queuing: %s", path)
        open(queue_txt, "a").write(path + "\n")

def has_items():
    with open(queue_txt, 'r') as fin:
        return fin.read().splitlines(True)


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

# mark_ready("asd")
# mark_ready("stay")
# take()
