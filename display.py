import os
import logging
import time
import numpy as np
import board
import layout
from config import settings

logger = logging.getLogger("blinky.display")


class NeoPixelDisplay:
    def __init__(self, led_count: int, x_boxes: int, y_boxes: int, rotate_90: bool):

        if os.uname()[4][:3] == "arm":
            self.strip = __import__("neopixel").NeoPixel(board.D18, led_count, brightness=1, auto_write=False)
        else:
            self.strip = [None]*led_count
        self.matrix = layout.full_layout(x_boxes, y_boxes, rotate_90=rotate_90)

        self.led_count = led_count

    def is_running(self):
        return True

    def show(self):
        if os.uname()[4][:3] != "arm":
            logger.error("Not an ARM thing!")
        self.strip.show()

    def set_brightness(self):
        self.brightness = settings.brightness

    def set_xy(self, x, y, value):
        led_id = self.matrix[y][x]
        logger.debug('set_xy x: %s, y: %s, val: %s, id: %s', x, y, value, led_id)
        new_value = []
        dark = True
        for color in value:
            if color > 3:
                dark = False
        if dark:
            new_value = (0, 0, 0)
        else:
            new_value = value

        self.strip[led_id] =  tuple(self.brightness * x  for x in new_value)

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
        # TODO implement this as method on NeoPixelDisplay implementation
        delay = 0.05
        try:
            while True:
                for i in range(self.led_count):
                    self.strip[i] = (255, 255, 255)
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

    def is_running(self):
        return self.running

    def process_events(self):
        pg = self.pg
        for event in pg.event.get():
            logger.debug(event)
            if event.type == pg.QUIT:
                logger.info("Exiting PyGameDisplay")
                self.running = False
                pg.quit()

    def show(self):
        pg = self.pg
        screen = pg.display.get_surface()
        screen.blit(self.surface, (0, 0))
        pg.display.flip()
        self.process_events()

    def paint_random(self):
        color = tuple(np.random.choice(range(256), size=3))
        self.set_xy(np.random.choice(range(self.x_pixels)),
                np.random.choice(range(self.y_pixels)),
                color)

    def set_brightness(self):
        self.brightness = settings.brightness

    def set_xy(self, x, y, color):
        x_offset = x * self.pixel_size
        y_offset = y * self.pixel_size
        color  = tuple(self.brightness * x for x in color)
        self.pg.draw.rect(self.surface, color, self.pg.Rect(x_offset, y_offset, self.pixel_size, self.pixel_size))
