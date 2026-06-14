import dataclasses
import json
import logging
import os
from pathlib import Path
from typing import Literal

logger = logging.getLogger('blinky.config')


@dataclasses.dataclass
class Settings:
    """Lightweight settings for the programmatic player (no env var deps)."""
    use_neopixel: bool = dataclasses.field(default_factory=lambda: 'NEOPIXEL' in os.environ)
    display_resolution: tuple = (25, 12)


settings = Settings()


@dataclasses.dataclass(kw_only=True, frozen=True)
class Constants:
    work_dir: str = os.environ.get('WORK_DIR', '')
    use_neopixel: bool = 'NEOPIXEL' in os.environ
    waiting_line: Path = Path(work_dir + "/config_files/waiting_line")
    waiting_line_lock: Path = Path(work_dir + "/config_files/waiting_line.lock")
    ad_link: str = os.environ.get('AD_LINK', '')
    root: int = int(os.environ.get('ROOT', '0'))
    saved_config: Path = Path(work_dir + '/config_files/dumped_config')


@dataclasses.dataclass(kw_only=True)
class Options:
    brightness: float = 1
    text_speed: int = 70
    playlistmode: str = 'mood'
    mood: str = 'default'
    pattern: str = 'default'
    program: str = ''  # '' = cycle all programs, 'plasma' = specific program
    led_type: Literal['rgb', 'grb'] = 'grb'
    adtime: int = 1200
    allowed_ids: list[int] = dataclasses.field(default_factory=lambda: [int(os.environ.get('ROOT', '0'))])
    user_names: dict = dataclasses.field(default_factory=dict)  # str(id) -> display name

    def __post_init__(self):
        if os.path.exists(Constants.saved_config):
            with open(Constants.saved_config, 'r') as save_file:
                old_config = json.load(fp=save_file)
            for key, value in old_config.items():
                object.__setattr__(self, key, value)
        # Mark initialisation complete; __setattr__ guards on this flag.
        # Use object.__setattr__ so the flag itself doesn't trigger a save.
        object.__setattr__(self, '_initialized', True)

    def __setattr__(self, key, value):
        super().__setattr__(key, value)
        if getattr(self, '_initialized', False):
            self.__save_config()

    def add_id(self, telegram_id: int, name: str = ''):
        self.allowed_ids.append(telegram_id)
        if name:
            self.user_names[str(telegram_id)] = name
        self.__save_config()

    def remove_id(self, telegram_id: int):
        self.allowed_ids.remove(telegram_id)
        self.user_names.pop(str(telegram_id), None)
        self.__save_config()

    def __save_config(self):
        data = {k: v for k, v in self.__dict__.items() if not k.startswith('_')}
        with open(Constants.saved_config, 'w+') as save_file:
            json.dump(data, fp=save_file, sort_keys=True, indent=4)


Main_Options = Options()
