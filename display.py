import os
import board
import layout

class MockDisplay:
    # default constructor
    def __init__(self, led_count):
        self.width = 20
        self.height = 15

    # a method for printing data members
    def show(self):
        print(self.width, "x", self.height)

    def set_xy(self, x, y):
        print(f'x: {x}, y: {y}')

class NeoPixelDisplay:
    def __init__(self, led_count, x_boxes, y_boxes):
        if os.uname()[4][:3] == "arm":
            self.strip = __import__("neopixel").NeoPixel(board.D18, led_count, brightness=bright, auto_write=True)
        else:
            self.strip = [None]*led_count
        self.matrix = layout.full_layout(x_boxes, y_boxes, vert=True)

    # a method for printing data members
    def show(self):
        print(f"NeoPixel flush")

    def set_xy(self, x, y, value):
        led_id = self.matrix[y][x]
        print(f'x: {x}, y: {y}, val: {value}, id: {led_id}')
        self.strip[led_id] = value

