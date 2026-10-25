"""Leitura e gravação de dados locais em JSON (recordes e configurações)."""
import json
from datetime import date

from settings import (DEFAULT_SETTINGS, HIGHSCORES_FILE, MAX_HIGHSCORES,
                      SETTINGS_FILE)


def _read(path, default):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return default


def _write(path, data):
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except OSError as erro:
        print(f"Não foi possível salvar {path.name}: {erro}")


def load_settings():
    data = _read(SETTINGS_FILE, {})
    settings = dict(DEFAULT_SETTINGS)
    if isinstance(data, dict):
        settings.update({k: v for k, v in data.items() if k in settings})
    for key in ("music_volume", "sfx_volume"):
        try:
            settings[key] = min(1.0, max(0.0, float(settings[key])))
        except (TypeError, ValueError):
            settings[key] = DEFAULT_SETTINGS[key]
    settings["show_fps"] = bool(settings["show_fps"])
    return settings


def save_settings(settings):
    _write(SETTINGS_FILE, settings)


def load_highscores():
    data = _read(HIGHSCORES_FILE, [])
    scores = []
    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict) and isinstance(item.get("score"), int):
                scores.append({"score": item["score"],
                               "wave": int(item.get("wave", 1)),
                               "date": str(item.get("date", ""))})
    scores.sort(key=lambda s: s["score"], reverse=True)
    return scores[:MAX_HIGHSCORES]


def add_highscore(scores, score, wave):
    """Adiciona a pontuação na tabela. Retorna (nova_tabela, bateu_recorde)."""
    best_before = scores[0]["score"] if scores else 0
    is_record = score > best_before
    if score > 0:
        scores = scores + [{"score": int(score), "wave": int(wave),
                            "date": date.today().isoformat()}]
        scores.sort(key=lambda s: s["score"], reverse=True)
        scores = scores[:MAX_HIGHSCORES]
        _write(HIGHSCORES_FILE, scores)
    return scores, is_record
