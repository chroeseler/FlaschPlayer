import os
import logging
import dbm

from filelock import FileLock

logger = logging.getLogger("blinky.config")

work_dir = os.environ['WORK_DIR']

use_neopixel = 'NEOPIXEL' in os.environ

waiting_line = work_dir + "/config/waiting_line"

waiting_line_lock = work_dir + "/config/waiting_line.lock"

db_lock = FileLock(work_dir + '/config/db_lock')

def get_config(param: str) -> str:
    with db_lock:
        with dbm.open(f'{work_dir}/config/settings', 'r') as db:
            return db[param]

def set_config(param: str, value: str) -> None:
    with db_lock:
        with dbm.open(f'{work_dir}/config/settings', 'c') as db:
            db[param] = value

class ConfigVar:
    def __init__(self, key, default, coerce_fn) -> None:
        self.key = key
        self.default = default
        self.coerce_fn = coerce_fn

    def get(self):
        try:
            return self.coerce_fn(get_config(self.key))
        except KeyError:
            return self.coerce_fn(self.default)

    def set(self, val: str):
        logger.info("Setting config %s to %s", self.key, val)
        set_config(self.key, val)

def coerce_str(x) -> str:
    if isinstance(x, str):
        return x
    return x.decode('utf-8')

brightness = ConfigVar("brightness", 1, float)
playlistmode = ConfigVar("playlistmode", "mood", coerce_str)
mood = ConfigVar("mood", "default", coerce_str)
pattern = ConfigVar("pattern", "default", coerce_str)
text_speed = ConfigVar('text_speed', 70, int)
