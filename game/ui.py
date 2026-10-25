"""Menu navegável por teclado e mouse."""
import pygame

from settings import GREY, WHITE, WIDTH
from game.utils import draw_text


class Menu:
    def __init__(self, options, font, top, spacing=58, center_x=WIDTH // 2):
        self.options = list(options)
        self.font = font
        self.top = top
        self.spacing = spacing
        self.center_x = center_x
        self.selected = 0
        self.rects = []
        self.layout()

    def layout(self):
        self.rects = []
        for i, text in enumerate(self.options):
            w, h = self.font.size(text)
            rect = pygame.Rect(0, 0, max(w + 60, 340), h + 14)
            rect.center = (self.center_x, self.top + i * self.spacing)
            self.rects.append(rect)

    def handle_event(self, event):
        """Retorna (ação, índice) ou None. Ações: move, select, left, right."""
        self.layout()
        count = len(self.options)
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.selected = (self.selected - 1) % count
                return ("move", self.selected)
            if event.key in (pygame.K_DOWN, pygame.K_s):
                self.selected = (self.selected + 1) % count
                return ("move", self.selected)
            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                return ("select", self.selected)
            if event.key in (pygame.K_LEFT, pygame.K_a):
                return ("left", self.selected)
            if event.key in (pygame.K_RIGHT, pygame.K_d):
                return ("right", self.selected)
        elif event.type == pygame.MOUSEMOTION:
            for i, rect in enumerate(self.rects):
                if rect.collidepoint(event.pos) and self.selected != i:
                    self.selected = i
                    return ("move", i)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, rect in enumerate(self.rects):
                if rect.collidepoint(event.pos):
                    self.selected = i
                    return ("select", i)
        return None

    def draw(self, surface):
        self.layout()
        for i, (text, rect) in enumerate(zip(self.options, self.rects)):
            selected = i == self.selected
            if selected:
                pygame.draw.rect(surface, (30, 70, 160), rect, border_radius=12)
                pygame.draw.rect(surface, (120, 190, 255), rect, 2, border_radius=12)
            draw_text(surface, text, self.font, WHITE if selected else GREY, rect.center)
