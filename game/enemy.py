"""Inimigos: Scout, Zigzag, Tank e o Chefão (Boss)."""
import math
import random

import pygame

from settings import HEIGHT, WIDTH
from game.bullet import Bullet
from game.utils import clamp, flash_version


def _aim(origin, target):
    """Ângulo (graus) de 'origin' até 'target'. 90 = para baixo."""
    direction = pygame.Vector2(target) - origin
    return direction.as_polar()[1] if direction.length_squared() > 0 else 90


def _shot(pos, angle, speed, image):
    return Bullet(pos, pygame.Vector2(speed, 0).rotate(angle), image, 1, False)


class Enemy(pygame.sprite.Sprite):
    score_value = 100
    drop_chance = 0.1
    explosion_color = (255, 120, 60)

    def __init__(self, image, pos, hp):
        super().__init__()
        self.base_image = image
        self.flash_image = flash_version(image)
        self.image = image
        self.rect = image.get_rect(center=(round(pos[0]), round(pos[1])))
        self.hitbox = self.rect.inflate(-int(self.rect.w * 0.25), -int(self.rect.h * 0.25))
        self.pos = pygame.Vector2(pos)
        self.hp = self.max_hp = hp
        self.flash = 0.0
        self.t = random.uniform(0, 6)

    def take_damage(self, amount=1):
        """Retorna True se o inimigo morreu."""
        self.hp -= amount
        self.flash = 0.07
        return self.hp <= 0

    def _sync(self, dt):
        self.t += dt
        self.flash = max(0.0, self.flash - dt)
        self.image = self.flash_image if self.flash > 0 else self.base_image
        self.rect.center = (round(self.pos.x), round(self.pos.y))
        self.hitbox.center = self.rect.center

    def update(self, dt, target, bullet_image):
        raise NotImplementedError


class Scout(Enemy):
    """Rápido e frágil: só mergulha na tela."""
    score_value = 100
    drop_chance = 0.08
    explosion_color = (255, 90, 80)

    def __init__(self, image, x, difficulty):
        super().__init__(image, (x, -30), 1)
        self.speed = 170 * difficulty

    def update(self, dt, target, bullet_image):
        self.pos.y += self.speed * dt
        self._sync(dt)
        if self.rect.top > HEIGHT + 10:
            self.kill()
        return []


class Zigzag(Enemy):
    """Ondula de um lado para o outro e atira para baixo."""
    score_value = 200
    drop_chance = 0.14
    explosion_color = (255, 170, 50)

    def __init__(self, image, x, difficulty):
        super().__init__(image, (x, -30), 2)
        self.x0 = clamp(x, 90, WIDTH - 90)
        self.speed = 95 * difficulty
        self.fire_delay = max(1.0, 2.4 / difficulty)
        self.fire_timer = random.uniform(0.8, self.fire_delay)
        self.bullet_speed = 230 * min(difficulty, 1.4)

    def update(self, dt, target, bullet_image):
        self.pos.y += self.speed * dt
        self.pos.x = self.x0 + math.sin(self.t * 2.2) * 70
        self._sync(dt)
        out = []
        self.fire_timer -= dt
        if self.fire_timer <= 0 and self.rect.top > 0:
            self.fire_timer = self.fire_delay
            out.append(_shot(self.pos + (0, 20), _aim(self.pos, target), self.bullet_speed, bullet_image))
        if self.rect.top > HEIGHT + 10:
            self.kill()
        return out


class Tank(Enemy):
    """Lento e resistente: para no alto da tela e dispara em leque."""
    score_value = 350
    drop_chance = 0.30
    explosion_color = (190, 120, 255)

    def __init__(self, image, x, difficulty):
        super().__init__(image, (clamp(x, 60, WIDTH - 60), -40), 5)
        self.d = difficulty
        self.target_y = random.randint(90, 170)
        self.vx = random.choice((-1, 1)) * 60 * difficulty
        self.fire_delay = max(1.3, 2.7 / difficulty)
        self.fire_timer = 1.2
        self.bullet_speed = 210 * min(difficulty, 1.4)

    def update(self, dt, target, bullet_image):
        if self.pos.y < self.target_y:
            self.pos.y += 70 * dt
        else:
            self.pos.x += self.vx * dt
            if self.pos.x < 50 or self.pos.x > WIDTH - 50:
                self.vx = -self.vx
                self.pos.x = clamp(self.pos.x, 50, WIDTH - 50)
        self._sync(dt)
        out = []
        self.fire_timer -= dt
        if self.fire_timer <= 0 and self.rect.top > 0:
            self.fire_timer = self.fire_delay
            base = _aim(self.pos, target)
            origin = self.pos + (0, self.rect.h / 2 - 6)
            for offset in (-18, 0, 18):
                out.append(_shot(origin, base + offset, self.bullet_speed, bullet_image))
        return out


class Boss(Enemy):
    """Chefão com 3 fases de ataque, conforme a vida diminui."""
    drop_chance = 1.0
    explosion_color = (255, 200, 80)

    def __init__(self, image, level, difficulty):
        super().__init__(image, (WIDTH / 2, -image.get_height()), 45 + 25 * level)
        self.hitbox = self.rect.inflate(-int(self.rect.w * 0.2), -int(self.rect.h * 0.3))
        self.score_value = 1500 + 500 * level
        self.entering = True
        self.fire_timer = 1.5
        self.toggle = False
        self.spiral = 0.0
        self.bullet_speed = 230 * min(difficulty, 1.4)

    @property
    def phase(self):
        ratio = self.hp / self.max_hp
        return 1 if ratio > 0.66 else 2 if ratio > 0.33 else 3

    def update(self, dt, target, bullet_image):
        out = []
        if self.entering:
            self.pos.y += 90 * dt
            if self.pos.y >= 145:
                self.entering = False
            self._sync(dt)
            return out

        amplitude = WIDTH / 2 - self.rect.w / 2 - 20
        self.pos.x = WIDTH / 2 + math.sin(self.t * 0.8) * amplitude
        self.pos.y = 145 + math.sin(self.t * 1.6) * 10
        self._sync(dt)

        muzzle = self.pos + (0, 50)
        speed = self.bullet_speed
        self.fire_timer -= dt
        if self.fire_timer > 0:
            return out

        if self.phase == 1:                       # leque mirado
            base = _aim(muzzle, target)
            for offset in (-30, -15, 0, 15, 30):
                out.append(_shot(muzzle, base + offset, speed, bullet_image))
            self.fire_timer = 1.3
        elif self.phase == 2:                     # alterna círculo e leque
            self.toggle = not self.toggle
            if self.toggle:
                start = random.uniform(0, 360)
                for i in range(14):
                    out.append(_shot(muzzle, start + i * 360 / 14, speed * 0.85, bullet_image))
            else:
                base = _aim(muzzle, target)
                for offset in (-24, -12, 0, 12, 24):
                    out.append(_shot(muzzle, base + offset, speed, bullet_image))
            self.fire_timer = 1.1
        else:                                     # espiral
            self.spiral += 22
            for extra in (0, 180):
                out.append(_shot(muzzle, self.spiral + extra, speed * 0.9, bullet_image))
            self.fire_timer = 0.11
        return out
