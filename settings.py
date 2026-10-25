"""Constantes globais do Space Defender.

Mexeu aqui, mexeu no jogo todo: velocidade, vidas, tempo de power-ups etc.
"""
import sys
from pathlib import Path

TITLE = "Space Defender"
WIDTH, HEIGHT = 800, 600
FPS = 60

# Caminhos (funcionam tanto no Python normal quanto no .exe do PyInstaller)
if getattr(sys, "frozen", False):
    BASE_DIR = Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
    DATA_DIR = Path(sys.executable).parent / "data"
else:
    BASE_DIR = Path(__file__).resolve().parent
    DATA_DIR = BASE_DIR / "data"

IMAGES_DIR = BASE_DIR / "assets" / "images"
SOUNDS_DIR = BASE_DIR / "assets" / "sounds"
HIGHSCORES_FILE = DATA_DIR / "highscores.json"
SETTINGS_FILE = DATA_DIR / "settings.json"

# Cores
WHITE = (255, 255, 255)
GOLD = (255, 215, 90)
RED = (255, 90, 90)
CYAN = (120, 220, 255)
GREY = (150, 160, 185)

# Jogador
PLAYER_SPEED = 360          # pixels por segundo
PLAYER_LIVES = 3
PLAYER_SHOOT_DELAY = 0.22   # segundos entre tiros
PLAYER_BULLET_SPEED = 640
INVULNERABLE_TIME = 1.6     # segundos de invencibilidade após tomar dano

# Power-ups
SHIELD_TIME = 8.0
SHOT_BOOST_TIME = 10.0
POWERUP_DROP_CHANCE = 0.12  # chance base (cada inimigo ajusta a sua)

# Ondas
BOSS_EVERY = 5              # um chefão a cada N ondas

# Dados
MAX_HIGHSCORES = 5
DEFAULT_SETTINGS = {
    "music_volume": 0.5,
    "sfx_volume": 0.7,
    "show_fps": False,
}

CREDITS = "Criado por: Gustavo Gomes"
