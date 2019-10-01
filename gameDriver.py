# Created on 24 September 2019

from square import Square, getScaledFont
from random import randint
from math import cos, sin, pi, atan, copysign
from pygame.mixer import *
from pygame.draw import rect
from pygame.locals import *
from pygame.time import Clock
from pygame.display import update
from pygame.mouse import get_pos


class GameDriver:
    def __init__(self, dim, w):
        self.dim = dim
        self.w = w
        self.squares = []
        self.vals = []
        # Stores sets of ((x,y): (#Squares to slide, surface))
        self.slides = {}
        self.slide_duration = 300
        self.v = (0, 0)
        self.score = 0
        self.prev_score = 0
        for y in range(dim[1]):
            row = []
            val = []
            for x in range(dim[0]):
                row.append(None)
                val.append(-1)
            self.squares.append(row)
            self.vals.append(val)

    def drawBoard(self, display):
        for y, row in enumerate(self.squares):
            for x, s in enumerate(row):
                if s != None:
                    display.blit(s.surface, (x * self.w, y * self.w))
                else:
                    rect(display, (0, 0, 0), (x * self.w, y * self.w, self.w, self.w))
                    rect(display, (255, 255, 255), (x * self.w, y * self.w, self.w, self.w), 2)
        update()

    def move(self, display, undo):
        if len(self.slides) == 0:
            return
        if undo:
            self.score = self.prev_score
            for y, (row1, row2) in enumerate(zip(self.squares, self.vals)):
                for x, (s, val) in enumerate(zip(row1, row2)):
                    if val == -1 and s != None:
                        self.squares[y][x] = None
                    elif val != -1 and s == None:
                        self.squares[y][x] = Square(val, self.w)
                    elif val != -1 and s != None:
                        self.squares[y][x].changeVal(val)
        updates = 20
        for i in range(updates):
            for x, y in self.slides.keys():
                v, surface = self.slides[(x, y)]
                xf, yf = x + v[0], y + v[1]
                if undo:
                    v = (-v[0], -v[1])
                    x, xf = xf, x
                    y, yf = yf, y
                v = (v[0] * self.w, v[1] * self.w)
                x1, y1 = x * self.w, y * self.w
                dx, dy = v[0] * i / updates, v[1] * i / updates
                rect(display, (0, 0, 0), (x1 + dx, y1 + dy, self.w, self.w))
                dx, dy = v[0] * (i + 1) / updates, v[1] * (i + 1) / updates
                display.blit(surface, (x1 + dx, y1 + dy))
            update()
            Clock().tick(updates * 1000 / self.slide_duration)
        self.drawBoard(display)

    def addSquares(self, display):
        nones = []
        for y, row in enumerate(self.squares):
            for x, s in enumerate(row):
                if s == None:
                    nones.append((x, y))
        for i in range(min(len(nones), 2)):
            idx = randint(0, len(nones) - 1)
            x, y = nones[idx]
            s = Square(2, self.w)
            self.squares[y][x] = s
            display.blit(s.surface, (x * self.w, y * self.w))
            nones.pop(idx)
        update()

    def lost(self):
        for y, row in enumerate(self.squares):
            for x, s in enumerate(row):
                if s == None:
                    return False
                else:
                    adjacent = []
                    for delta in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                        x1, y1 = x + delta[0], y + delta[1]
                        in_range = 0 <= x1 < self.dim[0] and 0 <= y1 < self.dim[1]
                        if in_range and self.squares[y1][x1] != None:
                            adjacent.append(self.squares[y1][x1].val)
                    if s.val in adjacent:
                        return False
        return True

    def updateScore(self, display, score_rect):
        font = getScaledFont("Times New Roman", (score_rect.w, score_rect.h), str(self.score))
        text = font.render(str(self.score), 1, (255, 255, 255))
        text_rect = text.get_rect(center=(score_rect.centerx, score_rect.centery))
        rect(display, (0, 0, 0), text_rect)
        display.blit(text, text_rect)

    def run(self, display, events, undo_rect, score_rect):
        for e in events:
            if e.type == MOUSEBUTTONUP and e.button == BUTTON_LEFT and \
                    undo_rect.collidepoint(get_pos()):
                self.move(display, True)
                self.slides.clear()
            elif e.type == KEYUP:
                if e.key == K_LEFT:
                    self.v = (-1, 0)
                elif e.key == K_RIGHT:
                    self.v = (1, 0)
                elif e.key == K_UP:
                    self.v = (0, -1)
                elif e.key == K_DOWN:
                    self.v = (0, 1)
                else:
                    continue
                self.slides.clear()
                self.prev_score = self.score
                move_x = self.v[0] != 0
                is_neg = -1 in self.v
                idx = 0 if move_x else 1
                lb = 0 if is_neg else -abs(self.dim[idx] * self.v[idx]) + 1
                ub = abs(self.dim[idx] * self.v[idx]) if is_neg else 1
                blanks = []
                merges = []
                prev = []
                for v1 in range(lb, ub):
                    for v2 in range(self.dim[1 - idx]):
                        if len(blanks) <= v2:
                            blanks.append(0)
                            prev.append(0)
                            merges.append(0)
                        x = abs(v1) if move_x else v2
                        y = v2 if move_x else abs(v1)
                        s = self.squares[y][x]
                        self.vals[y][x] = -1 if s == None else s.val
                        if s == None:
                            blanks[v2] += 1
                        else:
                            offset = blanks[v2] + merges[v2]
                            dx, dy = self.v[0] * offset, self.v[1] * offset
                            last_val = prev[v2]
                            prev[v2] = s.val
                            if last_val == s.val:
                                offset += 1
                                dx1, dy1 = self.v[0] * offset, self.v[1] * offset
                                self.slides[(x, y)] = ((dx1, dy1), s.surface)
                                self.squares[y + dy1][x + dx1].upgrade()
                                self.squares[y][x] = None
                                prev[v2] = 0
                                merges[v2] += 1
                                self.score += s.val * 2
                            elif offset != 0:
                                self.slides[(x, y)] = ((dx, dy), s.surface)
                                self.squares[y + dy][x + dx] = s
                                self.squares[y][x] = None
                self.move(display, False)
                self.addSquares(display)
                if sum(merges) >= 3:
                    music.load("bomb.mp3")
                    music.play()
            self.updateScore(display, score_rect)
            return self.lost()
