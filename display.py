import logging
import os
import time

import board
import numpy as np

import layout
from config import Main_Options as Options

logger = logging.getLogger("blinky.display")


class NeoPixelDisplay:
    resolution: set[int, int]
    led_count: int

    def __init__(self, led_count: int, x_boxes: int, y_boxes: int, rotate_90: bool):

        if os.uname()[4][:3] == "arm" or os.uname()[4] == 'aarch64':
            self.strip = __import__("neopixel").NeoPixel(board.D18, led_count, brightness=1, auto_write=False)
        else:
            self.strip = [None] * led_count
        self.matrix = layout.full_layout(x_boxes, y_boxes, rotate_90=rotate_90)
        self.resolution = {x_boxes * 5, y_boxes * 4} if not rotate_90 else {x_boxes * 4, y_boxes * 5}
        self.led_count = led_count
        self.brightness = Options.brightness
        self.led_type = Options.led_type

    @staticmethod
    def is_running():
        return True

    def show(self):
        if os.uname()[4][:3] != "arm" and os.uname()[4] != 'aarch64':
            logger.error("Not an ARM thing!")
        self.strip.show()
        return None  # No keyboard events on NeoPixel display

    def set_brightness(self):
        self.brightness = Options.brightness

    def set_xy(self, x: int, y: int, value: list[int, int, int]):
        led_id = self.matrix[y][x]
        logger.debug('set_xy x: %s, y: %s, val: %s, id: %s', x, y, value, led_id)
        dark = True
        for color in value:
            if color > 3:
                dark = False
        if dark:
            value = (0, 0, 0)

        if self.led_type == 'grb':
            value = [value[1], value[0], value[2]]

        self.strip[led_id] = tuple(self.brightness * x for x in value)

    def flash(self):
        for i in range(self.led_count):
            self.strip[i] = (255, 255, 255)
        self.show()
        time.sleep(0.5)
        for i in range(self.led_count):
            self.strip[i] = (0, 0, 0)
        self.show()
        time.sleep(0.5)
        for i in range(self.led_count):
            self.strip[i] = (255, 255, 255)
        self.show()
        time.sleep(0.5)
        for i in range(self.led_count):
            self.strip[i] = (0, 0, 0)
        self.show()

    def run_debug(self):
        delay = 0.05
        try:
            while True:
                for i in range(self.led_count):
                    self.strip[i] = (255, 255, 255)
                    self.show()
                    time.sleep(delay)
                for i in range(self.led_count):
                    self.strip[i] = (0, 0, 0)
                    self.show()
                    time.sleep(delay)
                for i in range(self.led_count):
                    self.strip[i] = (255, 0, 0)
                    self.show()
                    time.sleep(delay)
                for i in range(self.led_count):
                    self.strip[i] = (0, 255, 0)
                    self.show()
                    time.sleep(delay)
                for i in range(self.led_count):
                    self.strip[i] = (0, 0, 255)
                    self.show()
                    time.sleep(delay)
        except KeyboardInterrupt:
            self.flash()


class PyGameDisplay:

    def __init__(self, x_pixels, y_pixels, pixel_size):
        self.pg = __import__("pygame")
        pg = self.pg
        pg.init()
        surface_x = x_pixels * pixel_size
        surface_y = y_pixels * pixel_size
        pg.display.set_mode((surface_x, surface_y))
        self.surface = pg.Surface((surface_x, surface_y))
        pg.display.flip()
        self.pixel_size = pixel_size
        self.x_pixels = x_pixels
        self.y_pixels = y_pixels
        self.running = True
        self.brightness = Options.brightness

    def is_running(self):
        return self.running

    def process_events(self):
        """Process pygame events and return any special commands."""
        pg = self.pg
        command = None
        for event in pg.event.get():
            logger.debug(event)
            if event.type == pg.QUIT:
                logger.info("Exiting PyGameDisplay")
                self.running = False
                pg.quit()
            elif event.type == pg.KEYDOWN:
                # Handle arrow keys for program switching
                if event.key == pg.K_RIGHT or event.key == pg.K_DOWN:
                    command = 'next_program'
                elif event.key == pg.K_LEFT or event.key == pg.K_UP:
                    command = 'prev_program'
        return command

    def show(self):
        pg = self.pg
        screen = pg.display.get_surface()
        screen.blit(self.surface, (0, 0))
        pg.display.flip()
        command = self.process_events()
        return command

    def paint_random(self):
        color = tuple(np.random.choice(range(256), size=3))
        self.set_xy(np.random.choice(range(self.x_pixels)),
                    np.random.choice(range(self.y_pixels)),
                    color)

    def set_brightness(self):
        self.brightness = Options.brightness

    def set_xy(self, x, y, color):
        x_offset = x * self.pixel_size
        y_offset = y * self.pixel_size
        color = tuple(self.brightness * x for x in color)
        self.pg.draw.rect(self.surface, color, self.pg.Rect(x_offset, y_offset, self.pixel_size, self.pixel_size))
