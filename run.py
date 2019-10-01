# Created on 24 Spetember 2019

import pygame, sys
from pygame.locals import *
from gameDriver import GameDriver

pygame.init()

dim = (4, 4)
width = 50
w, h = dim[0] * width, dim[1] * width
display = pygame.display.set_mode((w, h + width))

undo = pygame.image.load("undo.png")
undo = pygame.transform.scale(undo, (width, width))
undo_rect = Rect(w - width, h, width, width)
pygame.draw.rect(display, (0, 200, 0), undo_rect)
display.blit(undo, (undo_rect.x, undo_rect.y))

score_rect = Rect(0, h, w - width, width)

driver = GameDriver(dim, width)
driver.drawBoard(display)

lost = False
while True:
    events = pygame.event.get()

    if QUIT in [e.type for e in events]:
        pygame.quit()
        sys.exit(0)

    if not lost:
        lost = driver.run(display, events, undo_rect, score_rect)
        if lost:
            lose = pygame.Surface((w, h))
            lose.set_alpha(0)
            display.blit(lose, (0, 0))
            img = pygame.image.load("lost.png")
            width = int(min(w, h) * 2 / 5)
            img = pygame.transform.scale(img, (width, width))
            display.blit(img, (int((w - width) / 2), int((h - width) / 2)))

    pygame.display.update()
