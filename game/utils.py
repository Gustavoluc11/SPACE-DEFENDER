"""Funções auxiliares usadas em vários arquivos."""
import pygame

_flash_cache = {}


def hits(a, b):
    """Colisão usando a 'hitbox' (menor que a imagem) quando existir."""
    return getattr(a, "hitbox", a.rect).colliderect(getattr(b, "hitbox", b.rect))


def flash_version(image):
    """Versão clareada da imagem, usada quando o inimigo leva dano."""
    key = id(image)
    if key not in _flash_cache:
        flash = image.copy()
        flash.fill((140, 140, 140, 0), special_flags=pygame.BLEND_RGB_ADD)
        _flash_cache[key] = flash
    return _flash_cache[key]


def clamp(value, low, high):
    return max(low, min(high, value))


def draw_text(surface, text, font, color, pos, anchor="center", shadow=True):
    image = font.render(text, True, color)
    rect = image.get_rect(**{anchor: pos})
    if shadow:
        surface.blit(font.render(text, True, (0, 0, 0)), rect.move(2, 2))
    surface.blit(image, rect)
    return rect


def draw_bar(surface, rect, ratio, color):
    ratio = clamp(ratio, 0.0, 1.0)
    pygame.draw.rect(surface, (25, 25, 45), rect, border_radius=4)
    if ratio > 0:
        fill = pygame.Rect(rect.x, rect.y, max(2, int(rect.w * ratio)), rect.h)
        pygame.draw.rect(surface, color, fill, border_radius=4)
    pygame.draw.rect(surface, (200, 205, 225), rect, 1, border_radius=4)
