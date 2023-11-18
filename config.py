import dataclasses
import logging
import os
from copy import copy
from pathlib import Path

logger = logging.getLogger("blinky.config")


@dataclasses.dataclass
class Constants:
    work_dir: os.environ = os.environ['WORK_DIR']
    use_neopixel: bool = 'NEOPIXEL' in os.environ
    waiting_line: Path = Path(work_dir + "/config/waiting_line")
    waiting_line_lock: Path = Path(work_dir + "/config/waiting_line.lock")

@dataclasses.dataclass
class Options:
    brightness: int = 1
    text_speed: int = 70
    playlistmode: str = 'mood'
    mood: str = 'default'
    pattern: str = 'default'

    def update_options(self) -> 'Options':
        return copy(self)


main_options = Options()
main_constants = Constants()
