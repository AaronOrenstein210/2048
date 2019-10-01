# Created on 23 September 2019

import pygame
from math import log2


class Square:
    def __init__(self, val, w):
        self.w = w
        self.val = val
        self.surface = pygame.Surface((w, w))
        self.drawSurface()

    def upgrade(self):
        self.val *= 2
        self.drawSurface()

    def changeVal(self, new_val):
        self.val = new_val
        self.drawSurface()

    def drawSurface(self):
        COLORS = ((255, 0, 0), (200, 80, 80), (255, 255, 0), (0, 255, 0), (64, 64, 255), (0, 0, 128), (200, 0, 200))
        color = COLORS[int(log2(self.val) - 1) % len(COLORS)]
        self.surface.fill((0, 0, 0))
        img = pygame.image.load("back.png")
        img = pygame.transform.scale(img, (self.w, self.w))
        self.surface.blit(img, (0, 0))
        text_dim = (int(self.w * 3 / 5), int(self.w * 3 / 5))
        font = getScaledFont("Times New Roman", text_dim, str(self.val))
        text = font.render(str(self.val), 1, color)
        text_rect = text.get_rect(center=(int(self.w / 2), int(self.w / 2)))
        self.surface.blit(text, text_rect)


def getScaledFont(font_type, dim, text):
    font_size = 0
    font = pygame.font.SysFont(font_type, font_size)
    w, h = font.size(text)
    while w < dim[0] and h < dim[1]:
        font_size += 1
        font = pygame.font.SysFont(font_type, font_size)
        w, h = font.size(text)
    return pygame.font.SysFont(font_type, font_size - 1)
