"""Carrega as imagens do jogo.

Se existir um PNG em assets/images/ com o nome certo, ele é usado.
Se não existir, o jogo desenha uma versão provisória por código.
"""
import math

import pygame

from settings import HEIGHT, IMAGES_DIR, WIDTH

# nome do arquivo (sem .png) -> tamanho em pixels (largura, altura)
SIZES = {
    "player": (64, 64),
    "enemy_scout": (32, 36),
    "enemy_zigzag": (48, 46),
    "enemy_tank": (60, 64),
    "boss": (120, 128),
    "bullet_player": (8, 24),
    "bullet_enemy": (12, 12),
    "powerup_shield": (34, 34),
    "powerup_shot": (34, 34),
}


def _surface(size):
    return pygame.Surface(size, pygame.SRCALPHA)


def _build_player(size):
    w, h = size
    cx = w // 2
    s = _surface(size)
    wings = [(cx, 16), (w - 2, h - 8), (w - 12, h - 3), (cx, h - 17), (12, h - 3), (2, h - 8)]
    pygame.draw.polygon(s, (35, 100, 205), wings)
    pygame.draw.polygon(s, (150, 210, 255), wings, 2)
    pygame.draw.rect(s, (255, 70, 70), (2, h - 13, 8, 5), border_radius=2)
    pygame.draw.rect(s, (255, 70, 70), (w - 10, h - 13, 8, 5), border_radius=2)
    body = [(cx, 0), (cx + 9, h - 18), (cx + 7, h - 5), (cx - 7, h - 5), (cx - 9, h - 18)]
    pygame.draw.polygon(s, (205, 228, 255), body)
    pygame.draw.polygon(s, (255, 255, 255), body, 2)
    pygame.draw.ellipse(s, (30, 190, 255), (cx - 5, 17, 10, 20))
    pygame.draw.ellipse(s, (200, 250, 255), (cx - 3, 19, 4, 8))
    return s


def _build_scout(size):
    w, h = size
    s = _surface(size)
    body = [(w // 2, h - 1), (w - 2, 5), (w // 2, 13), (2, 5)]
    pygame.draw.polygon(s, (215, 55, 70), body)
    pygame.draw.polygon(s, (255, 160, 160), body, 2)
    pygame.draw.circle(s, (255, 220, 80), (w // 2, h // 2 - 2), 5)
    pygame.draw.circle(s, (120, 20, 20), (w // 2, h // 2 - 2), 2)
    return s


def _build_zigzag(size):
    w, h = size
    cx, cy = w // 2, h // 2
    s = _surface(size)
    outer = [(cx, h - 1), (w - 2, cy), (cx, 2), (2, cy)]
    pygame.draw.polygon(s, (255, 150, 40), outer)
    pygame.draw.polygon(s, (255, 225, 140), outer, 2)
    pygame.draw.polygon(s, (130, 55, 10), [(cx, h - 11), (w - 11, cy), (cx, 11), (11, cy)])
    pygame.draw.circle(s, (255, 240, 150), (cx, cy), 6)
    return s


def _build_tank(size):
    w, h = size
    cx, cy = w // 2, h // 2
    s = _surface(size)
    pygame.draw.rect(s, (80, 40, 130), (cx - 17, h - 14, 8, 14), border_radius=2)
    pygame.draw.rect(s, (80, 40, 130), (cx + 9, h - 14, 8, 14), border_radius=2)
    r = w / 2 - 3
    hexagon = [(cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a)))
               for a in range(0, 360, 60)]
    pygame.draw.polygon(s, (125, 70, 200), hexagon)
    pygame.draw.polygon(s, (215, 175, 255), hexagon, 3)
    pygame.draw.circle(s, (70, 30, 120), (cx, cy), 14)
    pygame.draw.circle(s, (255, 90, 200), (cx, cy), 7)
    return s


def _build_boss(size):
    w, h = size
    cx = w // 2
    s = _surface(size)
    for x in (cx - 48, cx - 8, cx + 40):
        pygame.draw.rect(s, (70, 70, 90), (x, h - 24, 8, 24), border_radius=2)
    body = [(cx, h - 8), (w - 4, int(h * 0.45)), (w - 30, 6), (cx + 22, 20),
            (cx - 22, 20), (30, 6), (4, int(h * 0.45))]
    pygame.draw.polygon(s, (95, 95, 125), body)
    pygame.draw.polygon(s, (190, 190, 225), body, 3)
    inner = [(cx, h - 24), (w - 30, int(h * 0.45)), (w - 44, 20), (44, 20), (30, int(h * 0.45))]
    pygame.draw.polygon(s, (60, 55, 85), inner)
    pygame.draw.circle(s, (120, 20, 30), (cx, h // 2 - 4), 26)
    pygame.draw.circle(s, (255, 70, 70), (cx, h // 2 - 4), 18)
    pygame.draw.circle(s, (255, 220, 200), (cx, h // 2 - 4), 8)
    for x in (24, w - 24):
        pygame.draw.circle(s, (255, 190, 60), (x, 26), 7)
    return s


def _build_bullet_player(size):
    w, h = size
    s = _surface(size)
    pygame.draw.ellipse(s, (255, 215, 80), (0, 0, w, h))
    pygame.draw.ellipse(s, (255, 255, 235), (w // 4, 3, w // 2, h - 8))
    return s


def _build_bullet_enemy(size):
    w, h = size
    s = _surface(size)
    pygame.draw.circle(s, (255, 70, 70), (w // 2, h // 2), w // 2)
    pygame.draw.circle(s, (255, 210, 210), (w // 2, h // 2), w // 4)
    return s


def _build_powerup(size, color, letter):
    w, h = size
    s = _surface(size)
    pygame.draw.circle(s, color, (w // 2, h // 2), w // 2 - 1)
    pygame.draw.circle(s, (255, 255, 255), (w // 2, h // 2), w // 2 - 1, 2)
    text = pygame.font.Font(None, 28).render(letter, True, (255, 255, 255))
    s.blit(text, text.get_rect(center=(w // 2, h // 2)))
    return s


BUILDERS = {
    "player": _build_player,
    "enemy_scout": _build_scout,
    "enemy_zigzag": _build_zigzag,
    "enemy_tank": _build_tank,
    "boss": _build_boss,
    "bullet_player": _build_bullet_player,
    "bullet_enemy": _build_bullet_enemy,
    "powerup_shield": lambda size: _build_powerup(size, (50, 140, 240), "E"),
    "powerup_shot": lambda size: _build_powerup(size, (240, 150, 30), "T"),
}


class Assets:
    def __init__(self):
        self.images = {name: self._load(name, size) for name, size in SIZES.items()}
        self.background = self._load_background()

    @staticmethod
    def _load(name, size):
        path = IMAGES_DIR / f"{name}.png"
        if path.exists():
            try:
                image = pygame.image.load(str(path)).convert_alpha()
                return pygame.transform.smoothscale(image, size)
            except pygame.error as erro:
                print(f"Não consegui abrir {path.name}: {erro}. Usando versão padrão.")
        return BUILDERS[name](size).convert_alpha()

    @staticmethod
    def _load_background():
        path = IMAGES_DIR / "background.png"
        if path.exists():
            try:
                image = pygame.image.load(str(path)).convert()
                height = max(1, round(image.get_height() * WIDTH / image.get_width()))
                image = pygame.transform.smoothscale(image, (WIDTH, height))
                # a imagem é espelhada na vertical para a rolagem não ter emenda visível
                tile = pygame.Surface((WIDTH, height * 2))
                tile.blit(image, (0, 0))
                tile.blit(pygame.transform.flip(image, False, True), (0, height))
                return tile
            except pygame.error as erro:
                print(f"Não consegui abrir background.png: {erro}")
        return None
