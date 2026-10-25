# 🚀 Space Defender

Shoot 'em up 2D feito em **Python 3 + Pygame**, 100% offline, para Windows.
Sobreviva a ondas de inimigos, colete power-ups e derrote o chefão a cada 5 ondas.

## Como rodar

```bash
python -m pip install -r requirements.txt
python main.py
```

## Controles

| Tecla | Ação |
|-------|------|
| WASD / Setas | Mover a nave |
| ESPAÇO (segurar) | Atirar |
| ESC ou P | Pausar |
| F11 | Tela cheia |
| Mouse / Setas + Enter | Navegar nos menus |

## Recursos

- Ondas progressivas com dificuldade crescente
- 3 tipos de inimigos: **Scout** (rápido), **Zigzag** (ondula e atira), **Tank** (resistente, tiro em leque)
- **Chefão** a cada 5 ondas, com 3 padrões de ataque que mudam conforme a vida cai
- Power-ups: **E** = escudo temporário · **T** = disparo melhorado (até 3 níveis)
- Efeitos sonoros e música, partículas, tremor de tela e fundo com parallax
- Recordes (top 5) salvos em `data/highscores.json`
- Menu inicial, pausa e configurações (volumes e contador de FPS)

## Estrutura

```
space-defender/
├── main.py              # inicia o jogo
├── settings.py          # constantes (tela, FPS, velocidades, tempos)
├── game/
│   ├── game_manager.py  # estados, ondas, colisões, pontuação, HUD
│   ├── player.py        # nave do jogador
│   ├── enemy.py         # Scout, Zigzag, Tank e Boss
│   ├── bullet.py        # projéteis
│   ├── powerup.py       # power-ups
│   ├── effects.py       # estrelas e partículas
│   ├── assets.py        # carrega imagens (ou desenha as padrão)
│   ├── audio.py         # sons e música
│   ├── ui.py            # menus
│   ├── storage.py       # JSON de recordes e configurações
│   └── utils.py         # funções auxiliares
├── assets/images/       # coloque aqui seus PNGs (opcional)
├── assets/sounds/       # coloque aqui seus sons (opcional)
└── data/                # recordes e configurações (gerados automaticamente)
```

## Usando seus próprios assets

O jogo funciona sem nenhum arquivo externo, pois sprites e sons padrão são gerados por código.
Para trocar, basta colocar os arquivos com **estes nomes exatos**:

**`assets/images/`** (PNG com fundo transparente; a imagem é redimensionada para o tamanho indicado)

| Arquivo | Tamanho (px) | Observação |
|---------|--------------|------------|
| `player.png` | 64 × 64 | nave apontando para **cima** |
| `enemy_scout.png` | 32 × 36 | apontando para **baixo** |
| `enemy_zigzag.png` | 48 × 46 | |
| `enemy_tank.png` | 60 × 64 | |
| `boss.png` | 120 × 128 | |
| `bullet_player.png` | 8 × 24 | |
| `bullet_enemy.png` | 12 × 12 | |
| `powerup_shield.png` | 34 × 34 | |
| `powerup_shot.png` | 34 × 34 | |
| `background.png` | qualquer tamanho | opcional; é ajustado à largura da tela e espelhado na vertical para rolar sem emenda |

Os PNGs incluídos estão em 2× o tamanho do jogo (ex.: `player.png` tem 128 × 128) para ficarem nítidos.
Quer outros tamanhos? Edite o dicionário `SIZES` em `game/assets.py`.

**`assets/sounds/`** (`.wav` ou `.ogg`; `music` também aceita `.mp3`)

`shoot`, `enemy_shoot`, `hit`, `explosion`, `player_hit`, `powerup`, `menu`, `wave`, `boss_warning`, `gameover`, `music`

## Gerar o executável (.exe)

```bash
python -m pip install pyinstaller
pyinstaller --noconsole --onefile --name SpaceDefender --add-data "assets;assets" main.py
```

O executável fica em `dist/SpaceDefender.exe`. A pasta `data/` é criada ao lado dele.

## Ideias para evoluir

- Nome do jogador na tabela de recordes
- Mais tipos de inimigos e novos padrões de chefe
- Controle por gamepad
- Animação por spritesheet
