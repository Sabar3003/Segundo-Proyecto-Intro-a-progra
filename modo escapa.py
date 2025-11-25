import pygame
import random
import time
from collections import deque

# -
# CONFIGURACIÓN
# 
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
    'trap': (180, 140, 60),
    'exit': (255, 215, 0),
}


DIFFICULTY_SETTINGS = {
    'Fácil': {'enemies': 1, 'enemy_speed': 0.05, 'score_mult': 1.0},
    'Normal': {'enemies': 2, 'enemy_speed': 0.1, 'score_mult': 1.5},
    'Difícil': {'enemies': 3, 'enemy_speed': 0.5, 'score_mult': 2.0},
}

DIFFICULTY = 'Normal'  


MAX_TRAPS = 3
TRAP_COOLDOWN = 5.0  
TRAP_RESPAWN_TIME = 10.0  


MAX_ENERGY = 100
ENERGY_RUN_COST = 1.0 
ENERGY_RECOVERY_PER_SEC = 10.0


POINTS_PER_ENEMY = 15


ROWS = 18
COLS = 24


# UTILIDADES PATHFINDING  (PONER ESTO PRIMERO)

from collections import deque

def neighbors(m, r, c):
    rows = len(m); cols = len(m[0])
    for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
        nr, nc = r+dr, c+dc
        if 0 <= nr < rows and 0 <= nc < cols:
            yield nr, nc


def is_passable_for_player(tile):
    CAMINO = 0
    TUNEL = 2
    return tile in (CAMINO, TUNEL)

def is_passable_for_enemy(tile):
    CAMINO = 0
    LIANA = 3
    return tile in (CAMINO, LIANA)

def path_exists(m, start, goal):
    """Revisa si existe camino del jugador desde start hasta goal."""
    sr, sc = start
    gr, gc = goal
    visited = set()
    q = deque()
    q.append((sr, sc))
    visited.add((sr, sc))

    while q:
        r, c = q.popleft()
        if (r, c) == (gr, gc):
            return True
        for nr, nc in neighbors(m, r, c):
            if (nr, nc) in visited:
                continue
            if is_passable_for_player(m[nr][nc]):
                visited.add((nr, nc))
                q.append((nr, nc))
    return False


def bfs_shortest_path(m, start, goal, for_player=False):
    """Regresa una lista de celdas desde start hasta goal."""
    sr, sc = start
    gr, gc = goal
    queue = deque()
    queue.append((sr, sc))
    prev = {(sr, sc): None}

    if for_player:
        passable = is_passable_for_player
    else:
        passable = is_passable_for_enemy

    while queue:
        r, c = queue.popleft()

        if (r, c) == (gr, gc):
            path = []
            cur = (r, c)
            while prev[cur] is not None:
                path.append(cur)
                cur = prev[cur]
            path.reverse()
            return path

        for nr, nc in neighbors(m, r, c):
            if (nr, nc) not in prev and passable(m[nr][nc]):
                prev[(nr, nc)] = (r, c)
                queue.append((nr, nc))

    return []

def generate_random_map(rows, cols, wall_prob=0.28):

    while True:
        m = [[MURO if random.random() < wall_prob else CAMINO for _ in range(cols)] for _ in range(rows)]
       
        for _r in range(rows):
            for _c in range(cols):
                r = random.random()
                if r < 0.05:
                    m[_r][_c] = TUNEL
                elif r < 0.10:
                    m[_r][_c] = LIANA
     
        start = (1, 1)
        exit_pos = (rows - 2, cols - 2)
        m[start[0]][start[1]] = CAMINO
        m[exit_pos[0]][exit_pos[1]] = CAMINO
        if path_exists(m, start, exit_pos):
            return m, start, exit_pos

MAP, START_POS, EXIT_POS = generate_random_map(ROWS, COLS)


# UTILIDADES PATHFINDING

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

def path_exists(m, start, goal, for_player=True):
    sr, sc = start; gr, gc = goal
    visited = set(); q = deque()
    q.append((sr, sc)); visited.add((sr, sc))
    while q:
        r, c = q.popleft()
        if (r, c) == (gr, gc): return True
        for nr, nc in neighbors(m, r, c):
            if (nr, nc) in visited: continue
            tile = m[nr][nc]
            if for_player and not is_passable_for_player(tile): continue
            if not for_player and not is_passable_for_enemy(tile): continue
            visited.add((nr, nc)); q.append((nr, nc))
    return False

def bfs_shortest_path(m, start, goal, for_player=False):
    sr, sc = start; gr, gc = goal
    queue = deque()
    queue.append((sr, sc))
    prev = { (sr, sc): None }
    passable = is_passable_for_player if for_player else is_passable_for_enemy
    while queue:
        r, c = queue.popleft()
        if (r,c) == (gr,gc):
        
            path = []
            cur = (r,c)
            while prev[cur] is not None:
                path.append(cur)
                cur = prev[cur]
            path.reverse()
            return path
        for nr, nc in neighbors(m, r, c):
            if (nr, nc) not in prev and passable(m[nr][nc]):
                prev[(nr,nc)] = (r,c)
                queue.append((nr,nc))
    return []

# CLASES: Jugador, Enemigo, Trampa

class Trap:
    def __init__(self, cell_pos):
        self.cell = cell_pos
        self.created_at = time.time()
    def draw(self, surf, camera):
        r,c = self.cell
        pygame.draw.rect(surf, COLORS['trap'], (c*TILE, r*TILE, TILE, TILE))

class Enemy:
    def __init__(self, cell, map_ref, speed):
        self.cell = cell
        self.map = map_ref
        self.alive = True
        self.speed = speed 
        self.respawn_time = None
        self.last_move_tick = 0
        self.path = []  
    def update(self, player_cell, dt):
        if not self.alive:
            
            if self.respawn_time and time.time() >= self.respawn_time:
            
                self.alive = True
                self.respawn_time = None
            return
   
        if random.random() < 0.12:  
            self.path = bfs_shortest_path(self.map, self.cell, player_cell, for_player=False)
  
        if self.path and random.random() < self.speed:
            next_cell = self.path.pop(0)

            r,c = next_cell
            if is_passable_for_enemy(self.map[r][c]):
                self.cell = next_cell
            else:
                self.path = [] 
    def kill(self):
        self.alive = False
        self.respawn_time = time.time() + TRAP_RESPAWN_TIME
    def draw(self, surf):
        if not self.alive: return
        r,c = self.cell
        pygame.draw.circle(surf, COLORS['enemy'], (c*TILE + TILE//2, r*TILE + TILE//2), TILE//2 - 2)

class Player:
    def __init__(self, cell):
        self.cell = cell
        self.energy = MAX_ENERGY
        self.last_trap_time = -TRAP_COOLDOWN
        self.active_traps = []
        self.killed_enemies = 0
        self.start_time = time.time()
        self.finished = False
    def can_place_trap(self):
        if len(self.active_traps) >= MAX_TRAPS: 
            return False
        return (time.time() - self.last_trap_time) >= TRAP_COOLDOWN
    def place_trap(self, cell):
        if not self.can_place_trap(): return None
        self.last_trap_time = time.time()
        t = Trap(cell)
        self.active_traps.append(t)
        return t
    def run_cost(self, dt):
     
        return ENERGY_RUN_COST * dt * FPS
    def update_energy(self, running, dt):
        if running and self.energy > 0:
            
            self.energy -= self.run_cost(dt)
            if self.energy < 0: self.energy = 0
        else:
      
            self.energy += ENERGY_RECOVERY_PER_SEC * dt
            if self.energy > MAX_ENERGY: self.energy = MAX_ENERGY
    def draw(self, surf):
        r,c = self.cell
        pygame.draw.rect(surf, COLORS['player'], (c*TILE+4, r*TILE+4, TILE-8, TILE-8))


# INICIALIZACIÓN PYGAME

pygame.init()
rows = len(MAP); cols = len(MAP[0])
WIN_W = cols * TILE
WIN_H = rows * TILE + 80  
screen = pygame.display.set_mode((WIN_W, WIN_H))
pygame.display.set_caption("Modo Escapa - Demo")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 18)

player = Player(START_POS)
difficulty_cfg = DIFFICULTY_SETTINGS[DIFFICULTY]
enemies = []

def random_spawn_enemy():
 
    candidates = []
    for r in range(rows):
        for c in range(cols):
            if MAP[r][c] in (CAMINO, LIANA) and (r,c) != player.cell and (r,c) != EXIT_POS:
                candidates.append((r,c))
    if not candidates:
        return START_POS
    return random.choice(candidates)

for i in range(difficulty_cfg['enemies']):
    spawn = random_spawn_enemy()
    e = Enemy(spawn, MAP, difficulty_cfg['enemy_speed'])
    enemies.append(e)

# FUNCIONES DE RENDER Y LÓGICA

def draw_map():
    for r in range(rows):
        for c in range(cols):
            rect = (c*TILE, r*TILE, TILE, TILE)
            color = COLORS.get(MAP[r][c], (100,100,100))
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, (50,50,50), rect, 1)
    # draw exit
    er, ec = EXIT_POS
    pygame.draw.rect(screen, COLORS['exit'], (ec*TILE+4, er*TILE+4, TILE-8, TILE-8))

def handle_player_movement(keys, dt):
    r,c = player.cell
    running = False
    speed = 1 

    if (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]) and player.energy > 0:
        running = True
        speed = 2  

    new_r, new_c = r, c
    moved = False
    if keys[pygame.K_UP] or keys[pygame.K_w]:
        new_r = r - speed
        moved = True
    elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
        new_r = r + speed
        moved = True
    elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
        new_c = c - speed
        moved = True
    elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        new_c = c + speed
        moved = True
    # Validar movimiento paso a paso si speed>1
    if moved:
        # mover paso a paso para no saltar muros
        dr = new_r - r
        dc = new_c - c
        step_r, step_c = r, c
        steps = max(abs(dr), abs(dc))
        for s in range(steps):
            step_r += (1 if dr>0 else -1) if dr!=0 else 0
            step_c += (1 if dc>0 else -1) if dc!=0 else 0
            if 0 <= step_r < rows and 0 <= step_c < cols and is_passable_for_player(MAP[step_r][step_c]):
                # avanzar a step
                player.cell = (step_r, step_c)
            else:
                break
    # actualizar energía
    player.update_energy(running, dt)
    return

def evaluate_traps_and_enemies():
    # revisar trampas: si hay enemy en la celda de trap -> enemy.muere()
    for trap in list(player.active_traps):
        for e in enemies:
            if e.alive and e.cell == trap.cell:
                e.kill()
                player.killed_enemies += 1
                try:
                    player.active_traps.remove(trap)
                except ValueError:
                    pass
                # la trampa desaparece al eliminar al enemigo
                break
    # limpiar trampas viejas (si queremos tener duración limitada, opcional)
    # no hay duración en especificación, sólo desaparecen al matar

def enemies_respawn_check():
    # Si un enemigo ha marcado respawn_time, cuando llegue se reubica en random spawn
    for e in enemies:
        if not e.alive and e.respawn_time and time.time() >= e.respawn_time:
            e.alive = True
            e.respawn_time = None
            e.cell = random_spawn_enemy()

def check_collisions():
    # si un enemy ocupado la celda del jugador -> game over
    for e in enemies:
        if e.alive and e.cell == player.cell:
            return 'lose'
    # si jugador llegó a salida
    if player.cell == EXIT_POS:
        return 'win'
    return None

def draw_hud():
    # fondo HUD
    hud_rect = pygame.Rect(0, rows*TILE, WIN_W, 80)
    pygame.draw.rect(screen, (30,30,30), hud_rect)
    # energía
    en_text = font.render(f"Energía: {int(player.energy)} / {MAX_ENERGY}", True, (255,255,255))
    screen.blit(en_text, (10, rows*TILE + 8))
    # trampas
    traps_text = font.render(f"Trampas activas: {len(player.active_traps)} / {MAX_TRAPS}", True, (255,255,255))
    screen.blit(traps_text, (10, rows*TILE + 30))
    # cooldown
    cd = max(0, TRAP_COOLDOWN - (time.time() - player.last_trap_time))
    cd_text = font.render(f"Cooldown trampa: {cd:.1f}s", True, (255,255,255))
    screen.blit(cd_text, (10, rows*TILE + 52))
    # tiempo
    elapsed = time.time() - player.start_time
    time_text = font.render(f"Tiempo: {elapsed:.1f}s", True, (255,255,255))
    screen.blit(time_text, (250, rows*TILE + 8))
    # kills
    kills_text = font.render(f"Cazadores eliminados: {player.killed_enemies}", True, (255,255,255))
    screen.blit(kills_text, (250, rows*TILE + 30))
    # dificultad
    diff_text = font.render(f"Dificultad: {DIFFICULTY}", True, (255,255,255))
    screen.blit(diff_text, (250, rows*TILE + 52))

# ---------------------------
# BUCLE PRINCIPAL
# ---------------------------
running = True
game_state = 'playing'  # playing, win, lose
while running:
    dt = clock.tick(FPS) / 1000.0  # segundos desde última iteración
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and game_state == 'playing':
            # colocar trampa con tecla E
            if event.key == pygame.K_e:
                # coloca trampa en la casilla actual del jugador (si válido)
                pr, pc = player.cell
                # no permitir en túnel, liana o muro
                if MAP[pr][pc] == CAMINO and player.can_place_trap():
                    player.place_trap((pr, pc))
    keys = pygame.key.get_pressed()
    if game_state == 'playing':
        handle_player_movement(keys, dt)
        # actualizar enemigos
        for e in enemies:
            e.update(player.cell, dt)
        evaluate_traps_and_enemies()
        enemies_respawn_check()
        # colisiones
        col = check_collisions()
        if col == 'lose':
            game_state = 'lose'
            end_time = time.time()
        elif col == 'win':
            game_state = 'win'
            player.finished = True
            end_time = time.time()
    # render
    screen.fill((0,0,0))
    draw_map()
    # dibujar trampas
    for t in player.active_traps:
        t.draw(screen, None)
    # dibujar enemigos
    for e in enemies:
        e.draw(screen)
    # dibujar jugador
    player.draw(screen)
    draw_hud()

    if game_state == 'win':
        # calcular puntaje
        elapsed = end_time - player.start_time
        pt_time = max(0, 300 - elapsed)
        pt_diff = DIFFICULTY_SETTINGS[DIFFICULTY]['score_mult']
        total_score = int(pt_time * pt_diff + POINTS_PER_ENEMY * player.killed_enemies)
        win_text = font.render(f"¡GANASTE! Puntaje: {total_score}. Presiona ESC para salir.", True, (255,255,255))
        screen.blit(win_text, (WIN_W//2 - 220, rows*TILE + 30))
    elif game_state == 'lose':
        lose_text = font.render("HAS SIDO ALCANZADO. Presiona ESC para salir.", True, (255,255,255))
        screen.blit(lose_text, (WIN_W//2 - 160, rows*TILE + 30))

    pygame.display.flip()

    # permitir salir con ESC después de terminar
    if (game_state in ('win','lose')) and keys[pygame.K_ESCAPE]:
        running = False

pygame.quit()

# Si querés guardar puntuaciones en un archivo o integrarlo al top5,
# podés añadir lógica para leer/escribir un JSON con los puntajes y ordenar.
