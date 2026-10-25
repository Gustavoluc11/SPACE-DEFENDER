"""A nave do jogador."""
import math
import random

import pygame

from settings import (HEIGHT, INVULNERABLE_TIME, PLAYER_BULLET_SPEED,
                      PLAYER_LIVES, PLAYER_SHOOT_DELAY, PLAYER_SPEED,
                      SHIELD_TIME, SHOT_BOOST_TIME, WIDTH)
from game.bullet import Bullet

# (deslocamento_x, ângulo) de cada tiro, por nível de disparo
SHOT_PATTERNS = {
    1: [(0, 0)],
    2: [(-11, 0), (11, 0)],
    3: [(0, 0), (-14, -10), (14, 10)],
}


class Player(pygame.sprite.Sprite):
    def __init__(self, image, bullet_image):
        super().__init__()
        self.image = image
        self.bullet_image = bullet_image
        self._rotated = {}
        self.rect = image.get_rect(midbottom=(WIDTH // 2, HEIGHT - 30))
        self.pos = pygame.Vector2(self.rect.center)
        self.hitbox = pygame.Rect(0, 0, int(self.rect.w * 0.45),
                                  int(self.rect.h * 0.55))
        self.hitbox.center = self.rect.center
        self.lives = PLAYER_LIVES
        self.cooldown = 0.0
        self.invulnerable = 0.0
        self.shield_time = 0.0
        self.shot_level = 1
        self.shot_time = 0.0
        self.dead = False
        self.t = 0.0

    # ---------- lógica ----------
    def update(self, dt, keys):
        self.t += dt
        self.cooldown = max(0.0, self.cooldown - dt)
        self.invulnerable = max(0.0, self.invulnerable - dt)
        self.shield_time = max(0.0, self.shield_time - dt)
        if self.shot_time > 0:
            self.shot_time -= dt
            if self.shot_time <= 0:
                self.shot_time = 0.0
                self.shot_level = 1

        dx = (keys[pygame.K_RIGHT] or keys[pygame.K_d]) - (keys[pygame.K_LEFT] or keys[pygame.K_a])
        dy = (keys[pygame.K_DOWN] or keys[pygame.K_s]) - (keys[pygame.K_UP] or keys[pygame.K_w])
        direction = pygame.Vector2(dx, dy)
        if direction.length_squared() > 0:
            direction.normalize_ip()
        self.pos += direction * PLAYER_SPEED * dt
        half_w, half_h = self.rect.w / 2, self.rect.h / 2
        self.pos.x = max(half_w, min(WIDTH - half_w, self.pos.x))
        self.pos.y = max(HEIGHT * 0.3, min(HEIGHT - half_h - 4, self.pos.y))
        self.rect.center = (round(self.pos.x), round(self.pos.y))
        self.hitbox.center = self.rect.center

    def shoot(self):
        """Retorna a lista de projéteis criados (vazia se ainda em recarga)."""
        if self.dead or self.cooldown > 0:
            return []
        self.cooldown = PLAYER_SHOOT_DELAY
        bullets = []
        for offset_x, angle in SHOT_PATTERNS[self.shot_level]:
            velocity = pygame.Vector2(0, -PLAYER_BULLET_SPEED).rotate(angle)
            if angle not in self._rotated:
                self._rotated[angle] = pygame.transform.rotate(self.bullet_image, -angle)
            bullets.append(Bullet((self.rect.centerx + offset_x, self.rect.top + 10),
                                  velocity, self._rotated[angle], 1, True))
        return bullets

    def take_hit(self):
        """Tenta aplicar dano. Retorna True se perdeu vida."""
        if self.dead or self.invulnerable > 0 or self.shield_time > 0:
            return False
        self.lives -= 1
        self.shot_level, self.shot_time = 1, 0.0
        if self.lives <= 0:
            self.lives = 0
            self.dead = True
        else:
            self.invulnerable = INVULNERABLE_TIME
        return True

    def apply_powerup(self, kind):
        if kind == "shield":
            self.shield_time = SHIELD_TIME
        elif kind == "shot":
            self.shot_level = min(3, self.shot_level + 1)
            self.shot_time = SHOT_BOOST_TIME

    # ---------- desenho ----------
    def draw(self, surface):
        if self.dead:
            return
        # chamas dos 3 propulsores (azuis, combinam com a arte)
        by = self.rect.bottom - 6
        for dx in (-0.17, 0.0, 0.17):
            bx = self.rect.centerx + int(dx * self.rect.w)
            length = 6 + random.randint(0, 7)
            pygame.draw.polygon(surface, (70, 170, 255), [(bx - 4, by), (bx + 4, by), (bx, by + length)])
            pygame.draw.polygon(surface, (210, 240, 255), [(bx - 2, by), (bx + 2, by), (bx, by + length * 0.6)])

        blink = self.invulnerable > 0 and int(self.t * 14) % 2 == 0
        if not blink:
            surface.blit(self.image, self.rect)

        if self.shield_time > 0 and (self.shield_time > 2 or int(self.t * 10) % 2 == 0):
            r = 44 + int(math.sin(self.t * 6) * 2)
            bubble = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
            pygame.draw.circle(bubble, (80, 170, 255, 55), (r + 2, r + 2), r)
            pygame.draw.circle(bubble, (170, 225, 255, 210), (r + 2, r + 2), r, 2)
            surface.blit(bubble, bubble.get_rect(center=self.rect.center))
