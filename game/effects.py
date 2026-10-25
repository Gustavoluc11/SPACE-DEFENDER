"""Efeitos visuais: fundo de estrelas e partículas de explosão."""
import random

import pygame

from settings import HEIGHT, WIDTH


class Starfield:
    # (velocidade, tamanho, brilho, quantidade) de cada camada (efeito parallax)
    LAYERS = ((28, 1, 90, 70), (60, 1, 150, 90), (115, 2, 225, 50))

    def __init__(self, background=None):
        self.background = background
        self.scroll = 0.0
        self.stars = []
        for speed, size, bright, count in self.LAYERS:
            for _ in range(count):
                self.stars.append([random.uniform(0, WIDTH), random.uniform(0, HEIGHT),
                                   speed, size, bright])

    def update(self, dt, boost=1.0):
        for star in self.stars:
            star[1] += star[2] * dt * boost
            if star[1] > HEIGHT:
                star[1] -= HEIGHT
                star[0] = random.uniform(0, WIDTH)
        if self.background:
            self.scroll = (self.scroll + 30 * dt * boost) % self.background.get_height()

    def draw(self, surface):
        if self.background:
            tile_h = self.background.get_height()
            y = int(self.scroll) - tile_h
            while y < HEIGHT:
                surface.blit(self.background, (0, y))
                y += tile_h
        for x, y, speed, size, bright in self.stars:
            if self.background and speed < 100:      # com fundo: só as estrelas rápidas (parallax)
                continue
            surface.fill((bright, bright, min(255, bright + 30)), (int(x), int(y), size, size))


class ParticleSystem:
    def __init__(self):
        self.items = []   # [pos, vel, vida, vida_max, cor, tamanho]

    def explosion(self, pos, color=(255, 170, 60), count=24, speed=230, size=4.0):
        palette = (color, (255, 255, 210), (255, 110, 50))
        for _ in range(count):
            vel = pygame.Vector2(random.uniform(speed * 0.15, speed), 0).rotate(random.uniform(0, 360))
            life = random.uniform(0.3, 0.85)
            self.items.append([pygame.Vector2(pos), vel, life, life,
                               random.choice(palette), random.uniform(size * 0.5, size * 1.3)])

    def update(self, dt):
        drag = 0.1 ** dt
        for p in self.items:
            p[0] += p[1] * dt
            p[1] *= drag
            p[2] -= dt
        self.items = [p for p in self.items if p[2] > 0]

    def draw(self, surface):
        for pos, _vel, life, max_life, color, size in self.items:
            k = life / max_life
            shade = (int(color[0] * k), int(color[1] * k), int(color[2] * k))
            pygame.draw.circle(surface, shade, (int(pos.x), int(pos.y)), max(1, int(size * k + 0.5)))
