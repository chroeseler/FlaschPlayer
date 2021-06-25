import pygame as pg
from pygame.compat import xrange_

def show(image):
    screen = pg.display.get_surface()
    screen.fill((255, 255, 255))
    screen.blit(image, (0, 0))
    pg.display.flip()
    while 1:
        event = pg.event.wait()
        if event.type == pg.QUIT:
            raise SystemExit
        if event.type in [pg.MOUSEBUTTONDOWN, pg.KEYDOWN]:
            break

grid_x = 30
grid_y = 20

surface_x = grid_x * 10
surface_y = grid_y * 10

pg.init()

pg.display.set_mode((surface_x, surface_y))
surface = pg.Surface((surface_x, surface_y))

pg.display.flip()

pixels = [[(200,100,40), (11,33,210)]]
# TODO render pixels to pygame surface

# Create the PixelArray.
ar = pg.PixelArray(surface)

# Do some easy gradient effect.
for row in pixels:
    r, g, b = y*10, y*10, y
    ar[:, y*10] = (r, g, b)
del ar

show(surface)

