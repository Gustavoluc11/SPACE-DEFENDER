"""Coordena estados (menu, jogo, pausa...), ondas, pontuação e regras."""
import math
import random

import pygame

from settings import (BOSS_EVERY, CREDITS, CYAN, FPS, GOLD, GREY, HEIGHT, IMAGES_DIR, RED, TITLE,
                      WHITE, WIDTH)
from game import storage
from game.assets import Assets
from game.audio import Audio
from game.effects import ParticleSystem, Starfield
from game.enemy import Boss, Scout, Tank, Zigzag
from game.player import Player
from game.powerup import PowerUp
from game.ui import Menu
from game.utils import draw_bar, draw_text, hits

MENU, PLAYING, PAUSED, SETTINGS, GAME_OVER = "menu", "playing", "paused", "settings", "game_over"


class GameManager:
    def __init__(self):
        pygame.init()
        self.settings = storage.load_settings()

        try:
            icon = pygame.image.load(str(IMAGES_DIR / "player.png"))
            icon = pygame.transform.smoothscale(icon, (32, 32))
            pygame.display.set_icon(icon)
        except (pygame.error, FileNotFoundError):
            pass

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SCALED)
        pygame.display.set_caption(TITLE)
        self.canvas = pygame.Surface((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()

        self.assets = Assets()
        self.audio = Audio(self.settings)
        self.starfield = Starfield(self.assets.background)
        self.highscores = storage.load_highscores()

        self.font_title = pygame.font.Font(None, 84)
        self.font_big = pygame.font.Font(None, 60)
        self.font_menu = pygame.font.Font(None, 40)
        self.font_small = pygame.font.Font(None, 28)
        self.font_tiny = pygame.font.Font(None, 22)
        self.life_icon = pygame.transform.smoothscale(self.assets.images["player"], (26, 26))
        self.overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.overlay.fill((0, 0, 20, 175))

        self.menu_main = Menu(["Jogar", "Configurações", "Sair"], self.font_menu, top=350)
        self.menu_pause = Menu(["Continuar", "Configurações", "Menu principal"], self.font_menu, top=280)
        self.menu_over = Menu(["Jogar novamente", "Menu principal"], self.font_menu, top=485, spacing=52)
        self.menu_settings = Menu(["", "", "", "Voltar"], self.font_menu, top=250, spacing=62)

        self.state = MENU
        self.settings_return = MENU
        self.running = True
        self.shake = 0.0
        self.input_lock = 0.0
        self.new_record = False
        self.reset_world()
        self.audio.play_music()

    # ------------------------------------------------------------------
    # Estado do mundo
    # ------------------------------------------------------------------
    def reset_world(self):
        images = self.assets.images
        self.player = Player(images["player"], images["bullet_player"])
        self.enemies = pygame.sprite.Group()
        self.player_bullets = pygame.sprite.Group()
        self.enemy_bullets = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        self.particles = ParticleSystem()
        self.boss = None
        self.score = 0
        self.wave = 0
        self.spawn_queue = []
        self.spawn_timer = 0.0
        self.spawn_interval = 1.0
        self.wave_cleared = False
        self.intermission = 0.0
        self.banner_time = 0.0
        self.banner_text = ""
        self.banner_color = WHITE
        self.death_timer = 0.0
        self.enemy_sfx_cd = 0.0

    @property
    def best_score(self):
        return self.highscores[0]["score"] if self.highscores else 0

    def start_game(self):
        self.reset_world()
        self.new_record = False
        self.state = PLAYING
        self.start_wave()

    def start_wave(self):
        self.wave += 1
        self.wave_cleared = False
        self.banner_time = 2.4
        if self.wave % BOSS_EVERY == 0:
            self.banner_text, self.banner_color = "CUIDADO: CHEFÃO!", RED
            self.spawn_queue = ["boss"] + ["scout"] * 6
            self.spawn_timer = 2.6
            self.spawn_interval = 2.2
            self.audio.play("boss_warning")
        else:
            count = min(6 + self.wave * 2, 36)
            pool = ["scout"]
            if self.wave >= 2:
                pool += ["zigzag"] * 2
            if self.wave >= 3:
                pool += ["tank"]
            self.spawn_queue = [random.choice(pool) for _ in range(count)]
            self.spawn_timer = 2.0
            self.spawn_interval = max(0.45, 1.1 - self.wave * 0.05)
            self.banner_text, self.banner_color = f"ONDA {self.wave}", CYAN
            self.audio.play("wave")

    def spawn_enemy(self, kind):
        images = self.assets.images
        difficulty = min(1 + 0.05 * (self.wave - 1), 2.0)
        x = random.randint(50, WIDTH - 50)
        if kind == "boss":
            enemy = Boss(images["boss"], self.wave // BOSS_EVERY, difficulty)
            self.boss = enemy
        elif kind == "zigzag":
            enemy = Zigzag(images["enemy_zigzag"], x, difficulty)
        elif kind == "tank":
            enemy = Tank(images["enemy_tank"], x, difficulty)
        else:
            enemy = Scout(images["enemy_scout"], x, difficulty)
        self.enemies.add(enemy)

    # ------------------------------------------------------------------
    # Loop principal
    # ------------------------------------------------------------------
    def run(self):
        while self.running:
            dt = min(self.clock.tick(FPS) / 1000, 0.05)
            self.handle_events()
            self.update(dt)
            self.draw()
        storage.save_settings(self.settings)
        pygame.quit()

    # ------------------------------------------------------------------
    # Eventos
    # ------------------------------------------------------------------
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                continue
            if event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
                pygame.display.toggle_fullscreen()
                continue
            if self.state == MENU:
                self.on_menu_event(event)
            elif self.state == PLAYING:
                if event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_p):
                    self.state = PAUSED
                    self.menu_pause.selected = 0
                    self.audio.play("menu")
            elif self.state == PAUSED:
                self.on_pause_event(event)
            elif self.state == SETTINGS:
                self.on_settings_event(event)
            elif self.state == GAME_OVER:
                self.on_game_over_event(event)

    def on_menu_event(self, event):
        result = self.menu_main.handle_event(event)
        if not result:
            return
        action, index = result
        if action == "move":
            self.audio.play("menu")
        elif action == "select":
            self.audio.play("menu")
            if index == 0:
                self.start_game()
            elif index == 1:
                self.open_settings(MENU)
            else:
                self.running = False

    def on_pause_event(self, event):
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_p):
            self.state = PLAYING
            return
        result = self.menu_pause.handle_event(event)
        if not result:
            return
        action, index = result
        if action == "move":
            self.audio.play("menu")
        elif action == "select":
            self.audio.play("menu")
            if index == 0:
                self.state = PLAYING
            elif index == 1:
                self.open_settings(PAUSED)
            else:
                self.state = MENU
                self.menu_main.selected = 0

    def on_game_over_event(self, event):
        if self.input_lock > 0:
            return
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.state = MENU
            return
        result = self.menu_over.handle_event(event)
        if not result:
            return
        action, index = result
        if action == "move":
            self.audio.play("menu")
        elif action == "select":
            self.audio.play("menu")
            if index == 0:
                self.start_game()
            else:
                self.state = MENU
                self.menu_main.selected = 0

    def open_settings(self, came_from):
        self.settings_return = came_from
        self.menu_settings.selected = 0
        self.state = SETTINGS

    def close_settings(self):
        storage.save_settings(self.settings)
        self.state = self.settings_return

    def on_settings_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.close_settings()
            return
        result = self.menu_settings.handle_event(event)
        if not result:
            return
        action, index = result
        if action == "move":
            self.audio.play("menu")
            return
        if index in (0, 1):
            key = "music_volume" if index == 0 else "sfx_volume"
            value = self.settings[key]
            if action == "select":
                value = value + 0.1 if value < 0.95 else 0.0      # clique/enter: aumenta e volta ao zero
            else:
                value += 0.1 if action == "right" else -0.1
            self.settings[key] = round(min(1.0, max(0.0, value)), 1)
            self.audio.apply_volumes()
            self.audio.play("menu")
        elif index == 2:
            self.settings["show_fps"] = not self.settings["show_fps"]
            self.audio.play("menu")
        elif index == 3 and action == "select":
            self.close_settings()

    # ------------------------------------------------------------------
    # Atualização
    # ------------------------------------------------------------------
    def update(self, dt):
        self.shake = max(0.0, self.shake - 40 * dt)
        if self.state == PLAYING:
            self.update_game(dt)
        elif self.state in (MENU, GAME_OVER) or (self.state == SETTINGS and self.settings_return == MENU):
            self.starfield.update(dt, 0.6)
            self.input_lock = max(0.0, self.input_lock - dt)

    def update_game(self, dt):
        player = self.player
        keys = pygame.key.get_pressed()
        self.starfield.update(dt)
        self.particles.update(dt)
        self.banner_time = max(0.0, self.banner_time - dt)
        self.enemy_sfx_cd = max(0.0, self.enemy_sfx_cd - dt)

        if not player.dead:
            player.update(dt, keys)
            if keys[pygame.K_SPACE]:
                shots = player.shoot()
                if shots:
                    self.player_bullets.add(shots)
                    self.audio.play("shoot")
        else:
            self.death_timer -= dt
            if self.death_timer <= 0:
                self.finish_game()
                return

        self.update_spawning(dt)
        target = player.pos if not player.dead else pygame.Vector2(WIDTH / 2, HEIGHT)
        for enemy in list(self.enemies):
            new_bullets = enemy.update(dt, target, self.assets.images["bullet_enemy"])
            if new_bullets:
                self.enemy_bullets.add(new_bullets)
                if self.enemy_sfx_cd <= 0:
                    self.audio.play("enemy_shoot")
                    self.enemy_sfx_cd = 0.15
        self.player_bullets.update(dt)
        self.enemy_bullets.update(dt)
        self.powerups.update(dt)
        self.handle_collisions()

    def update_spawning(self, dt):
        if self.spawn_queue:
            self.spawn_timer -= dt
            if self.spawn_timer <= 0:
                self.spawn_enemy(self.spawn_queue.pop(0))
                self.spawn_timer = self.spawn_interval
        elif len(self.enemies) == 0 and not self.player.dead:
            if not self.wave_cleared:
                self.wave_cleared = True
                self.intermission = 1.6
                self.score += 50 * self.wave          # bônus por limpar a onda
            else:
                self.intermission -= dt
                if self.intermission <= 0:
                    self.start_wave()

    def handle_collisions(self):
        player = self.player

        # tiros do jogador x inimigos
        for bullet, targets in pygame.sprite.groupcollide(
                self.player_bullets, self.enemies, True, False, hits).items():
            enemy = targets[0]
            if not enemy.alive():
                continue
            self.particles.explosion(bullet.pos, (255, 240, 150), 5, 130, 2)
            if enemy.take_damage(bullet.damage):
                self.kill_enemy(enemy)
            else:
                self.audio.play("hit")

        if player.dead:
            return

        # tiros inimigos x jogador
        for _ in pygame.sprite.spritecollide(player, self.enemy_bullets, True, hits):
            self.damage_player()

        # corpo a corpo
        for enemy in pygame.sprite.spritecollide(player, self.enemies, False, hits):
            if not isinstance(enemy, Boss):
                self.kill_enemy(enemy)
            self.damage_player()

        # power-ups
        for powerup in pygame.sprite.spritecollide(player, self.powerups, True, hits):
            player.apply_powerup(powerup.kind)
            self.score += 25
            self.audio.play("powerup")

    def kill_enemy(self, enemy):
        self.score += enemy.score_value
        if isinstance(enemy, Boss):
            for _ in range(9):
                offset = (random.randint(-70, 70), random.randint(-45, 45))
                self.particles.explosion(enemy.pos + offset, enemy.explosion_color, 30, 320, 6)
            self.shake = 20
            self.spawn_powerup("shield", enemy.pos + (-30, 0))
            self.spawn_powerup("shot", enemy.pos + (30, 0))
            self.boss = None
        else:
            self.particles.explosion(enemy.pos, enemy.explosion_color, 24, 230, 4)
            self.shake = max(self.shake, 3)
            if random.random() < enemy.drop_chance:
                self.spawn_powerup(random.choice(("shield", "shot")), enemy.pos)
        self.audio.play("explosion")
        enemy.kill()

    def spawn_powerup(self, kind, pos):
        self.powerups.add(PowerUp(kind, self.assets.images[f"powerup_{kind}"], (pos[0], pos[1])))

    def damage_player(self):
        player = self.player
        if player.take_hit():
            self.audio.play("player_hit")
            self.particles.explosion(player.pos, (90, 200, 255), 22, 220, 3)
            self.shake = 12
            if player.dead:
                for _ in range(4):
                    offset = (random.randint(-20, 20), random.randint(-20, 20))
                    self.particles.explosion(player.pos + offset, (255, 160, 60), 30, 300, 5)
                self.audio.play("explosion")
                self.shake = 18
                self.death_timer = 1.6
        elif player.shield_time > 0:
            self.particles.explosion(player.pos, (120, 190, 255), 6, 140, 2)
            self.audio.play("hit")

    def finish_game(self):
        self.highscores, self.new_record = storage.add_highscore(self.highscores, self.score, self.wave)
        self.state = GAME_OVER
        self.menu_over.selected = 0
        self.input_lock = 0.9
        self.audio.play("gameover")

    # ------------------------------------------------------------------
    # Desenho
    # ------------------------------------------------------------------
    def draw(self):
        canvas = self.canvas
        canvas.fill((8, 8, 24))
        self.starfield.draw(canvas)

        if self.state == MENU or (self.state == SETTINGS and self.settings_return == MENU):
            if self.state == MENU:
                self.draw_main_menu(canvas)
        elif self.state == PLAYING:
            self.draw_world(canvas)
            self.draw_hud(canvas)
        elif self.state == PAUSED:
            self.draw_world(canvas)
            self.draw_hud(canvas)
            canvas.blit(self.overlay, (0, 0))
            draw_text(canvas, "PAUSADO", self.font_big, WHITE, (WIDTH // 2, 180))
            self.menu_pause.draw(canvas)
        elif self.state == GAME_OVER:
            self.draw_game_over(canvas)
        if self.state == SETTINGS:
            if self.settings_return == PAUSED:
                self.draw_world(canvas)
                self.draw_hud(canvas)
                canvas.blit(self.overlay, (0, 0))
            self.draw_settings(canvas)

        if self.settings["show_fps"]:
            draw_text(canvas, f"{self.clock.get_fps():.0f} FPS", self.font_tiny, GREY,
                      (WIDTH - 10, HEIGHT - 8), "bottomright")

        self.screen.fill((0, 0, 0))
        offset = (0, 0)
        if self.shake > 0.5:
            amount = int(self.shake)
            offset = (random.randint(-amount, amount), random.randint(-amount, amount))
        self.screen.blit(canvas, offset)
        pygame.display.flip()

    def draw_world(self, canvas):
        self.powerups.draw(canvas)
        self.enemies.draw(canvas)
        self.enemy_bullets.draw(canvas)
        self.player_bullets.draw(canvas)
        self.player.draw(canvas)
        self.particles.draw(canvas)

    def draw_hud(self, canvas):
        player = self.player
        draw_text(canvas, f"PONTOS  {self.score:07d}", self.font_small, WHITE, (16, 12), "topleft")
        draw_text(canvas, f"RECORDE {max(self.best_score, self.score):07d}", self.font_tiny,
                  GOLD, (16, 36), "topleft")
        draw_text(canvas, f"ONDA {self.wave}", self.font_small, CYAN, (WIDTH // 2, 12), "midtop")
        for i in range(player.lives):
            canvas.blit(self.life_icon, (WIDTH - 16 - (i + 1) * 30, 10))

        y = 70
        if player.shield_time > 0:
            draw_text(canvas, "ESCUDO", self.font_tiny, (120, 190, 255), (16, y), "midleft")
            draw_bar(canvas, pygame.Rect(94, y - 6, 90, 12), player.shield_time / 8.0, (80, 160, 255))
            y += 22
        if player.shot_time > 0:
            draw_text(canvas, f"TIRO x{player.shot_level}", self.font_tiny, (255, 190, 80), (16, y), "midleft")
            draw_bar(canvas, pygame.Rect(94, y - 6, 90, 12), player.shot_time / 10.0, (255, 160, 40))

        if self.boss and self.boss.alive():
            draw_text(canvas, "CHEFÃO", self.font_tiny, RED, (WIDTH // 2, 40), "midtop")
            draw_bar(canvas, pygame.Rect(WIDTH // 2 - 210, 58, 420, 12),
                     self.boss.hp / self.boss.max_hp, (230, 60, 70))

        if self.banner_time > 0 and not player.dead:
            text = self.font_big.render(self.banner_text, True, self.banner_color)
            text.set_alpha(int(255 * min(1.0, self.banner_time / 0.6)))
            canvas.blit(text, text.get_rect(center=(WIDTH // 2, int(HEIGHT * 0.36))))

    def draw_main_menu(self, canvas):
        ticks = pygame.time.get_ticks() / 1000
        draw_text(canvas, "SPACE DEFENDER", self.font_title, (40, 110, 255), (WIDTH // 2, 124), shadow=False)
        draw_text(canvas, "SPACE DEFENDER", self.font_title, (225, 240, 255), (WIDTH // 2, 120))
        draw_text(canvas, "Shoot 'em up 2D", self.font_small, GREY, (WIDTH // 2, 172))
        ship = self.assets.images["player"]
        canvas.blit(ship, ship.get_rect(center=(WIDTH // 2, 255 + int(math.sin(ticks * 2) * 6))))
        self.menu_main.draw(canvas)
        if self.best_score:
            draw_text(canvas, f"Recorde: {self.best_score:07d}", self.font_small, GOLD, (WIDTH // 2, 520))
        draw_text(canvas, "WASD / Setas: mover    ESPAÇO: atirar    ESC: pausa    F11: tela cheia",
                  self.font_tiny, GREY, (WIDTH // 2, HEIGHT - 20))
        draw_text(canvas, CREDITS, self.font_tiny, GREY, (WIDTH - 12, 12), "topright")

    def draw_settings(self, canvas):
        s = self.settings
        self.menu_settings.options = [
            f"Música: < {round(s['music_volume'] * 100)}% >",
            f"Efeitos: < {round(s['sfx_volume'] * 100)}% >",
            f"Mostrar FPS: {'SIM' if s['show_fps'] else 'NÃO'}",
            "Voltar",
        ]
        draw_text(canvas, "CONFIGURAÇÕES", self.font_big, WHITE, (WIDTH // 2, 140))
        self.menu_settings.draw(canvas)
        draw_text(canvas, "Setas esquerda/direita ajustam    ESC volta", self.font_tiny, GREY,
                  (WIDTH // 2, HEIGHT - 40))

    def draw_game_over(self, canvas):
        draw_text(canvas, "FIM DE JOGO", self.font_title, RED, (WIDTH // 2, 90))
        draw_text(canvas, f"Pontos: {self.score:07d}", self.font_menu, WHITE, (WIDTH // 2, 160))
        draw_text(canvas, f"Onda alcançada: {self.wave}", self.font_small, CYAN, (WIDTH // 2, 195))
        if self.new_record and int(pygame.time.get_ticks() / 400) % 2 == 0:
            draw_text(canvas, "NOVO RECORDE!", self.font_menu, GOLD, (WIDTH // 2, 232))
        draw_text(canvas, "MELHORES PONTUAÇÕES", self.font_small, GREY, (WIDTH // 2, 278))
        for i, entry in enumerate(self.highscores):
            line = f"{i + 1}.  {entry['score']:07d}    onda {entry['wave']}"
            draw_text(canvas, line, self.font_small, GOLD if i == 0 else WHITE,
                      (WIDTH // 2, 310 + i * 26))
        self.menu_over.draw(canvas)
