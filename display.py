import os
import logging
import board
import layout
import time
import numpy as np

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger("blinky.display")

class MockDisplay:
    def __init__(self, led_count):
        self.width = 20
        self.height = 15

    def show(self):
        logger.info(self.width, "x", self.height)

    def set_xy(self, x, y):
        logger.info(f'x: {x}, y: {y}')

class NeoPixelDisplay:
    def __init__(self, led_count, x_boxes, y_boxes):
        if os.uname()[4][:3] == "arm":
            self.strip = __import__("neopixel").NeoPixel(board.D18, led_count, brightness=1, auto_write=False)
        else:
            self.strip = [None]*led_count
        self.matrix = layout.full_layout(x_boxes, y_boxes, vert=True)
        self.led_count = led_count

    def is_running(self):
        return True

    def show(self):
        if os.uname()[4][:3] != "arm":
            logger.error("Not an ARM thing!")
        self.strip.show()

    def set_xy(self, x, y, value):
        led_id = self.matrix[y][x]
        logger.debug(f'set_xy x: {x}, y: {y}, val: {value}, id: {led_id}')
        self.strip[led_id] = value

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

    def set_xy(self, x, y, color):
        x_offset = x * self.pixel_size
        y_offset = y * self.pixel_size
        self.pg.draw.rect(self.surface, color, self.pg.Rect(x_offset, y_offset, self.pixel_size, self.pixel_size))
