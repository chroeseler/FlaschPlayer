import pygame as pg
import display
import time

d = display.PyGameDisplay(20,10,50)

running = True
while running:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False

    for n in range (100):
        d.paint_random()
    d.show()

# Done! Time to quit.
pg.quit()
