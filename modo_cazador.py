import pygame
import random
import time
from collections import deque

# ---------------------------
# CONFIG
# ---------------------------
TILE = 32
FPS = 30

CAMINO = 0
MURO = 1
TUNEL = 2
LIANA = 3

COLORS = {
    CAMINO: (200, 200, 200),
    MURO: (40, 40, 40),
    TUNEL: (150, 150, 255),
    LIANA: (100, 200, 100),
    'player': (50, 120, 200),
    'enemy': (200, 50, 50),
    'exit': (255, 215, 0),
}

DIFFICULTY_SETTINGS = {
    'Fácil': {'enemies': 1, 'enemy_speed': 0.35, 'score_loss': 20},
    'Normal': {'enemies': 2, 'enemy_speed': 0.1, 'score_loss': 30},
    'Difícil': {'enemies': 3, 'enemy_speed': 0.75, 'score_loss': 40},
}

DIFFICULTY = 'Normal'

MAX_ENERGY = 100
ENERGY_RUN_COST = 1.0
ENERGY_RECOVERY_PER_SEC = 10.0

# ---------------------------
# UTILIDADES PATHFINDING
# ---------------------------
def neighbors(m, r, c):
    rows = len(m); cols = len(m[0])
    for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
        nr, nc = r+dr, c+dc
        if 0 <= nr < rows and 0 <= nc < cols:
            yield nr, nc

def is_passable_for_player(tile):
    return tile in (CAMINO, TUNEL)

def is_passable_for_enemy(tile):
    return tile in (CAMINO, LIANA)

def bfs_path(m, start, goal, for_player=False):
    """Devuelve la ruta desde start hasta goal usando BFS"""
    queue = deque([start])
    visited = {start: None}

    passable = is_passable_for_player if for_player else is_passable_for_enemy

    while queue:
        current = queue.popleft()
        if current == goal:
            # reconstruir
            path = []
            while visited[current] is not None:
                path.append(current)
                current = visited[current]
            path.reverse()
            return path
        for nr, nc in neighbors(m, current[0], current[1]):
            if (nr, nc) not in visited and passable(m[nr][nc]):
                visited[(nr, nc)] = current
                queue.append((nr, nc))
    return []

# ---------------------------
# MAPA DE EJEMPLO
# ---------------------------
def generate_random_map(r, c):
    while True:
        m = [[MURO if random.random() < 0.30 else CAMINO for _ in range(c)] for _ in range(r)]
        start = (1, 1)
        exit_pos = (r - 2, c - 2)
        m[start[0]][start[1]] = CAMINO
        m[exit_pos[0]][exit_pos[1]] = CAMINO
        return m, start, exit_pos

ROWS, COLS = 18, 24
MAP, START_POS, EXIT_POS = generate_random_map(ROWS, COLS)

# ---------------------------
# CLASES
# ---------------------------
class Player:
    def __init__(self, cell):
        self.cell = cell
        self.energy = MAX_ENERGY
        self.kills = 0
        self.score = 0

    def update_energy(self, running, dt):
        if running and self.energy > 0:
            self.energy -= ENERGY_RUN_COST * dt * FPS
            if self.energy < 0:
                self.energy = 0
        else:
            self.energy += ENERGY_RECOVERY_PER_SEC * dt
            if self.energy > MAX_ENERGY:
                self.energy = MAX_ENERGY

class Enemy:
    def __init__(self, cell, map_ref, speed):
        self.cell = cell
        self.map = map_ref
        self.speed = speed
        self.path = []
        self.alive = True

    def flee(self, player_cell):
        """Busca alejarse del jugador usando una inversión de BFS"""
        path_to_player = bfs_path(self.map, self.cell, player_cell, for_player=False)
        if not path_to_player:
            return
        # ruta invertida = huir
        path_to_player.reverse()
        self.path = path_to_player[:6]  # huye unos pasos

    def update(self, player_cell):
        if random.random() < 0.15 or not self.path:
            self.flee(player_cell)

        if self.path and random.random() < self.speed:
            next_cell = self.path.pop(0)
            r, c = next_cell
            if is_passable_for_enemy(self.map[r][c]):
                self.cell = next_cell

# ---------------------------
# PYGAME INIT
# ---------------------------
pygame.init()
WIN = pygame.display.set_mode((COLS*TILE, ROWS*TILE + 80))
pygame.display.set_caption("Modo Cazador")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 18)

player = Player(START_POS)
enemy_cfg = DIFFICULTY_SETTINGS[DIFFICULTY]
enemies = []

def random_spawn_enemy():
    valid = []
    for r in range(ROWS):
        for c in range(COLS):
            if MAP[r][c] in (CAMINO, LIANA) and (r, c) != START_POS:
                valid.append((r, c))
    return random.choice(valid)

for _ in range(enemy_cfg['enemies']):
    enemies.append(Enemy(random_spawn_enemy(), MAP, enemy_cfg['enemy_speed']))

# ---------------------------
# DIBUJAR MAPA
# ---------------------------
def draw_map():
    for r in range(ROWS):
        for c in range(COLS):
            pygame.draw.rect(WIN, COLORS[MAP[r][c]], (c*TILE, r*TILE, TILE, TILE))
            pygame.draw.rect(WIN, (40,40,40), (c*TILE, r*TILE, TILE, TILE), 1)
    er, ec = EXIT_POS
    pygame.draw.rect(WIN, COLORS['exit'], (ec*TILE+4, er*TILE+4, TILE-8, TILE-8))

# ---------------------------
# LOOP
# ---------------------------
running = True
while running:
    dt = clock.tick(FPS) / 1000.0
    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # -----------------------
    # MOVIMIENTO DEL JUGADOR
    # -----------------------
    r, c = player.cell
    new_r, new_c = r, c
    speed = 1
    running_mode = False

    if (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]) and player.energy > 0:
        running_mode = True
        speed = 2

    if keys[pygame.K_UP] or keys[pygame.K_w]:
        new_r -= speed
    elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
        new_r += speed
    elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
        new_c -= speed
    elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        new_c += speed

    if 0 <= new_r < ROWS and 0 <= new_c < COLS:
        if is_passable_for_player(MAP[new_r][new_c]):
            player.cell = (new_r, new_c)

    player.update_energy(running_mode, dt)

    # -----------------------
    # ENEMIGOS HUYENDO
    # -----------------------
    for e in enemies:
        e.update(player.cell)

    # -----------------------
    # COLISIONES
    # -----------------------
    for e in enemies:
        if e.cell == player.cell:
            # atrapado → ganar puntos
            gain = enemy_cfg['score_loss'] * 2
            player.score += gain
            player.kills += 1
            e.cell = random_spawn_enemy()  # respawn

    # Si algún enemigo llega a la salida
    for e in enemies:
        if e.cell == EXIT_POS:
            player.score -= enemy_cfg['score_loss']
            e.cell = random_spawn_enemy()

    # -----------------------
    # RENDER
    # -----------------------
    WIN.fill((0,0,0))
    draw_map()

    # Enemigos
    for e in enemies:
        r, c = e.cell
        pygame.draw.circle(WIN, COLORS['enemy'], (c*TILE+16, r*TILE+16), 14)

    # Jugador
    pr, pc = player.cell
    pygame.draw.rect(WIN, COLORS['player'], (pc*TILE+4, pr*TILE+4, TILE-8, TILE-8))

    # HUD
    pygame.draw.rect(WIN, (30,30,30), (0, ROWS*TILE, COLS*TILE, 80))
    WIN.blit(font.render(f"Energía: {int(player.energy)}", True, (255,255,255)), (10, ROWS*TILE+10))
    WIN.blit(font.render(f"Puntaje: {player.score}", True, (255,255,255)), (10, ROWS*TILE+35))
    WIN.blit(font.render(f"Enemigos atrapados: {player.kills}", True, (255,255,255)), (200, ROWS*TILE+10))
    WIN.blit(font.render(f"Dificultad: {DIFFICULTY}", True, (255,255,255)), (200, ROWS*TILE+35))

    pygame.display.update()

pygame.quit()
