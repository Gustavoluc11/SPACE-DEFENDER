"""Sons e música.

Os efeitos são sintetizados por código (nada de arquivos externos).
Para usar os teus próprios sons, coloca arquivos .wav/.ogg em assets/sounds/
com os nomes: shoot, enemy_shoot, hit, explosion, player_hit, powerup, menu,
wave, boss_warning, gameover e music.
"""
import math
import random
from array import array

import pygame

from settings import SOUNDS_DIR

RATE = 22050
EXTENSIONS = (".wav", ".ogg", ".mp3")


class Audio:
    def __init__(self, settings):
        self.settings = settings
        self.enabled = False
        self.sounds = {}
        self.music_sound = None
        self.music_file = None
        try:
            pygame.mixer.quit()
            pygame.mixer.init(RATE, -16, 1, 512, allowedchanges=0)
        except (pygame.error, TypeError) as erro:
            print(f"Áudio indisponível, o jogo seguirá sem som: {erro}")
            return
        self.rate, _fmt, self.channels = pygame.mixer.get_init()
        pygame.mixer.set_reserved(1)             # canal 0 fica só para a música
        self.music_channel = pygame.mixer.Channel(0)
        self._build_sfx()
        self._build_music()
        self.enabled = True
        self.apply_volumes()

    # ---------- síntese ----------
    def _tone(self, f0, f1, dur, wave="square", vol=0.3, power=1.0, lowpass=0.0):
        n = max(1, int(self.rate * dur))
        out, phase, y = [], 0.0, 0.0
        for i in range(n):
            t = i / n
            phase += (f0 + (f1 - f0) * t) / self.rate
            ph = phase % 1.0
            if wave == "square":
                v = 1.0 if ph < 0.5 else -1.0
            elif wave == "saw":
                v = 2 * ph - 1
            elif wave == "tri":
                v = 4 * abs(ph - 0.5) - 1
            elif wave == "noise":
                v = random.uniform(-1, 1)
                if lowpass:
                    y += lowpass * (v - y)
                    v = y * 3
            else:
                v = math.sin(2 * math.pi * ph)
            env = (1 - t) ** power
            if i < 40:
                env *= i / 40                     # evita "clique" no começo
            out.append(v * env * vol)
        return out

    @staticmethod
    def _mix(*tracks):
        size = max(len(t) for t in tracks)
        out = [0.0] * size
        for track in tracks:
            for i, v in enumerate(track):
                out[i] += v
        return out

    def _silence(self, dur):
        return [0.0] * int(self.rate * dur)

    def _make_sound(self, samples):
        buf = array("h")
        for v in samples:
            s = int(max(-1.0, min(1.0, v)) * 32767)
            buf.append(s)
            if self.channels == 2:
                buf.append(s)
        return pygame.mixer.Sound(buffer=buf.tobytes())

    @staticmethod
    def _find_file(name):
        for ext in EXTENSIONS:
            path = SOUNDS_DIR / f"{name}{ext}"
            if path.exists():
                return path
        return None

    # ---------- construção ----------
    def _build_sfx(self):
        t = self._tone
        recipes = {
            "shoot": lambda: t(900, 260, 0.11, "square", 0.22, 1.5),
            "enemy_shoot": lambda: t(420, 160, 0.14, "saw", 0.16, 1.2),
            "hit": lambda: t(0, 0, 0.08, "noise", 0.5, 1.5, 0.6),
            "explosion": lambda: t(0, 0, 0.55, "noise", 0.9, 1.6, 0.12),
            "player_hit": lambda: self._mix(t(260, 50, 0.4, "saw", 0.4),
                                            t(0, 0, 0.3, "noise", 0.6, 1.5, 0.2)),
            "powerup": lambda: sum((t(f, f, 0.07, "square", 0.2, 0.5)
                                    for f in (523, 659, 784, 1047)), []),
            "menu": lambda: t(660, 720, 0.05, "square", 0.18),
            "wave": lambda: t(392, 392, 0.09, "square", 0.2, 0.5) + t(523, 523, 0.09, "square", 0.2, 0.5)
                            + t(659, 659, 0.16, "square", 0.2, 1.0),
            "boss_warning": lambda: sum((t(180, 130, 0.25, "saw", 0.3, 0.3) + self._silence(0.08)
                                         for _ in range(3)), []),
            "gameover": lambda: t(392, 392, 0.2, "tri", 0.4, 0.3) + t(330, 330, 0.2, "tri", 0.4, 0.3)
                                + t(262, 262, 0.2, "tri", 0.4, 0.3) + t(196, 196, 0.7, "tri", 0.4, 1.0),
        }
        for name, make in recipes.items():
            path = self._find_file(name)
            try:
                self.sounds[name] = pygame.mixer.Sound(str(path)) if path else self._make_sound(make())
            except pygame.error as erro:
                print(f"Som '{name}' ignorado: {erro}")

    def _build_music(self):
        self.music_file = self._find_file("music")
        if self.music_file:
            return
        chords = [(220.0, 261.63, 329.63),      # Lá menor
                  (174.61, 220.0, 261.63),      # Fá
                  (261.63, 329.63, 392.0),      # Dó
                  (196.0, 246.94, 293.66)]      # Sol
        eighth = 0.24
        n8 = int(self.rate * eighth)
        bar = n8 * 8
        total = [0.0] * (bar * len(chords))
        for ci, chord in enumerate(chords):
            base = ci * bar
            notes = [chord[0], chord[1], chord[2], chord[0] * 2,
                     chord[2], chord[1], chord[2], chord[1]]
            for ni, freq in enumerate(notes):
                seg = self._tone(freq, freq, eighth * 0.95, "square", 0.07, 1.6)
                off = base + ni * n8
                for i, v in enumerate(seg):
                    total[off + i] += v
            bass = self._tone(chord[0] / 2, chord[0] / 2, eighth * 7.8, "tri", 0.2, 0.4)
            for i, v in enumerate(bass):
                total[base + i] += v
        self.music_sound = self._make_sound(total)

    # ---------- uso ----------
    def apply_volumes(self):
        if not self.enabled:
            return
        for sound in self.sounds.values():
            sound.set_volume(self.settings["sfx_volume"])
        if self.music_sound:
            self.music_sound.set_volume(self.settings["music_volume"])
        pygame.mixer.music.set_volume(self.settings["music_volume"])

    def play(self, name):
        if self.enabled and name in self.sounds:
            self.sounds[name].play()

    def play_music(self):
        if not self.enabled:
            return
        if self.music_file:
            try:
                pygame.mixer.music.load(str(self.music_file))
                pygame.mixer.music.play(-1)
            except pygame.error as erro:
                print(f"Não consegui tocar a música: {erro}")
        elif self.music_sound:
            self.music_channel.play(self.music_sound, loops=-1)
