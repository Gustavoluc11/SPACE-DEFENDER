"""Power-ups que caem dos inimigos: escudo e disparo melhorado."""
import math

import pygame

from settings import HEIGHT, WIDTH
from game.utils import clamp


class PowerUp(pygame.sprite.Sprite):
    def __init__(self, kind, image, pos):
        super().__init__()
        self.kind = kind            # "shield" ou "shot"
        self.image = image
        self.rect = image.get_rect(center=pos)
        self.hitbox = self.rect.inflate(8, 8)
        self.base_x = pos[0]
        self.y = float(pos[1])
        self.t = 0.0

    def update(self, dt):
        self.t += dt
        self.y += 110 * dt
        x = clamp(self.base_x + math.sin(self.t * 3) * 16, 20, WIDTH - 20)
        self.rect.center = (round(x), round(self.y))
        self.hitbox.center = self.rect.center
        if self.rect.top > HEIGHT:
            self.kill()
