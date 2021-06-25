import os
import logging
import dbm

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger("blinky.config")

work_dir = os.environ['WORK_DIR']

use_neopixel = 'NEOPIXEL' in os.environ

waiting_line = work_dir + "/config/waiting_line"

waiting_line_lock = work_dir + "/config/waiting_line.lock"

def get_config(param):
    with dbm.open(f'{work_dir}/config/settings', 'c') as db:
        return db[param]

def set_config(param, value):
    with dbm.open(f'{work_dir}/config/settings', 'c') as db:
        db[param] = str(value)

class ConfigVar:
    def __init__(self, key, default, coerce_fn):
        self.key = key
        self.coerce_fn = coerce_fn
        self.default = default

    def get(self):
        try:
            return self.coerce_fn(get_config(self.key))
        except KeyError:
            return self.coerce_fn(self.default)

    def set(self, val):
        logger.info("Setting config %s to %s", self.key, val)
        set_config(self.key, str(val))

def coerce(x):
    if isinstance(x, str):
        return x
    else:
        return x.decode('utf-8')


brightness = ConfigVar("brightness", 1, float)
mood = ConfigVar("mood", "default", coerce)
