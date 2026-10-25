"""Projéteis (tanto do jogador quanto dos inimigos)."""
import pygame

from settings import HEIGHT, WIDTH

_AREA = pygame.Rect(-60, -60, WIDTH + 120, HEIGHT + 120)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos, velocity, image, damage=1, from_player=True):
        super().__init__()
        self.image = image
        self.rect = image.get_rect(center=(round(pos[0]), round(pos[1])))
        self.pos = pygame.Vector2(pos)
        self.vel = pygame.Vector2(velocity)
        self.damage = damage
        self.from_player = from_player

    def update(self, dt):
        self.pos += self.vel * dt
        self.rect.center = (round(self.pos.x), round(self.pos.y))
        if not _AREA.colliderect(self.rect):
            self.kill()
