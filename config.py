import dataclasses
import json
import logging
import os
from typing import Literal
from pathlib import Path
from typing import Literal

logger = logging.getLogger("blinky.config")


@dataclasses.dataclass(kw_only=True, frozen=True)
class Constants:
    work_dir: os.environ = os.environ['WORK_DIR']
    use_neopixel: bool = 'NEOPIXEL' in os.environ
    waiting_line: Path = Path(work_dir + "/config_files/waiting_line")
    waiting_line_lock: Path = Path(work_dir + "/config_files/waiting_line.lock")
    saved_config: Path = Path(work_dir + '/config_files/dumped_config')


@dataclasses.dataclass(kw_only=True)
class Options:
    brightness: float = 1
    text_speed: int = 70
    playlistmode: str = 'mood'
    mood: str = 'default'
    pattern: str = 'default'
    led_type: Literal['rgb', 'grb'] = 'grb'
    adtime: int = 1200
    init: bool = False

    def __post_init__(self):
        if os.path.exists(Constants.saved_config):
            with open(Constants.saved_config, 'r') as save_file:
                old_config = json.load(fp=save_file)
            for key, value in old_config.items():
                setattr(self, key, value)
        self.init = True

    def __setattr__(self, key, value):
        if self.init:
            super().__setattr__(key, value)
            with open(Constants.saved_config, 'w+') as save_file:
                json.dump(self, fp=save_file, default=lambda o: o.__dict__, sort_keys=True, indent=4)
        else:
            super().__setattr__(key, value)


main_options = Options()
