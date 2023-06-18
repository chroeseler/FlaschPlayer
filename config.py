import os
import logging
import json
from dataclasses import dataclass, asdict

logger = logging.getLogger('blinky.config')


@dataclass
class Config:
    display_resolution: tuple[int, int] = (25, 12)
    brightness: float = 1.0
    playlistmode: str = 'mood'
    mood: str = 'default'
    pattern: str = 'default'
    text_speed: int = 70

    work_dir = os.environ['WORK_DIR']
    waiting_line = work_dir + '/config/waiting_line'
    waiting_line_lock = work_dir + '/config/waiting_line.lock'
    config_file = f'{work_dir}/config/settings'

    use_neopixel = 'NEOPIXEL' in os.environ

    def __init__(self):
        if os.path.exists(self.config_file):
            logger.info('Old config file found; loading')
            with open(self.config_file, 'r', encoding='utf-8') as settings_file:
                old_settings = json.load(settings_file)
                for key, value in old_settings.items():
                    setattr(self, key, value)

    def __setattr__(self, name, value):
        super()
        with open(self.config_file, 'w', encoding='utf-8') as settings_file:
            json.dump(asdict(self), settings_file)


settings = Config()
