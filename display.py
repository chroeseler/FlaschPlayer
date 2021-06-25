import os
import logging
import board
import layout
import numpy as np
import pygame as pg

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
            self.strip = __import__("neopixel").NeoPixel(board.D18, led_count, brightness=bright, auto_write=False)
        else:
            self.strip = [None]*led_count
        self.matrix = layout.full_layout(x_boxes, y_boxes, vert=True)

    def is_running(self):
        return True

    def show(self):
        logger.info("NeoPixel flush")

    def set_xy(self, x, y, value):
        led_id = self.matrix[y][x]
        logger.debug(f'set_xy x: {x}, y: {y}, val: {value}, id: {led_id}')
        self.strip[led_id] = value

class PyGameDisplay:
    def __init__(self, x_pixels, y_pixels, pixel_size):
        pg.init()
        surface_x = x_pixels * pixel_size
        surface_y = y_pixels * pixel_size
        pg.display.set_mode((surface_x, surface_y))
        self.surface = pg.Surface((surface_x, surface_y))
        pg.display.flip()
        self.ar = pg.PixelArray(self.surface)
        self.pixel_size = pixel_size
        self.x_pixels = x_pixels
        self.y_pixels = y_pixels
        self.running = True

    def is_running(self):
        return self.running

    def process_events(self):
        for event in pg.event.get():
            logger.debug(event)
            if event.type == pg.QUIT:
                logger.info("Exiting PyGameDisplay")
                self.running = False
                pg.quit()

    def show(self):
        del self.ar
        screen = pg.display.get_surface()
        screen.blit(self.surface, (0, 0))
        pg.display.flip()
        self.ar = pg.PixelArray(self.surface)
        self.process_events()

    def paint_random(self):
        color = tuple(np.random.choice(range(256), size=3))
        self.set_xy(np.random.choice(range(self.x_pixels)),
                np.random.choice(range(self.y_pixels)),
                color)

    def set_xy(self, x, y, color):
        x_offset = x * self.pixel_size
        y_offset = y * self.pixel_size
        for tx in range(x_offset, x_offset + self.pixel_size):
            for ty in range(y_offset, y_offset + self.pixel_size):
                # this log line will slow down frame renders a lot
                # print(f"translated {x},{y} -> {tx},{ty}")
                self.ar[tx,ty] = color
