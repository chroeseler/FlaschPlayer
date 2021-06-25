import os

work_dir = os.environ['WORK_DIR']

use_neopixel = 'NEOPIXEL' in os.environ

waiting_line = work_dir + "/config/waiting_line"

waiting_line_lock = work_dir + "/config/waiting_line.lock"
