import pygame
import sys
import random
from avatar import Avatar
from mapa import GeneradorMapa, Muro, Tunel, Liana, Camino
from collections import deque
from puntajes import GestorPuntajes

# --------------------------------------
# CONFIG GENERAL
# --------------------------------------
TAM = 32
FILAS = 20
COLUMNAS = 25

ANCHO = COLUMNAS * TAM
ALTO = FILAS * TAM + 70  # HUD arriba

COLOR_HUD = (0, 0, 0)
COLOR_SALIDA = (255, 230, 0)  # amarillo brillante

pygame.init()
pygame.display.set_caption("Modo Cazador")

# --------------------------------------
# VALIDACIÓN DE RUTA PARA ESCAPISTA
# --------------------------------------
def verificar_ruta_escapista(matriz, salidas):
    """ Verifica si el escapista puede llegar a una salida. """
    inicio = (0, 0)
    FIL = len(matriz)
    COL = len(matriz[0])

    q = deque([inicio])
    visitado = set([inicio])

    while q:
        f, c = q.popleft()

        if (f, c) in salidas:
            return True

        for df, dc in [(1,0),(-1,0),(0,1),(0,-1)]:
            nf, nc = f + df, c + dc
            if 0 <= nf < FIL and 0 <= nc < COL:
                if (nf, nc) not in visitado and matriz[nf][nc].transitable_jugador:
                    visitado.add((nf, nc))
                    q.append((nf, nc))

    return False

# --------------------------------------
# ENCONTRAR POSICIÓN VÁLIDA PARA SPAWN
# --------------------------------------
def encontrar_posicion_valida(matriz, tipo="cazador"):
    """Encuentra una posición válida para spawn evitando muros"""
    posiciones_validas = []
    
    for f in range(FILAS):
        for c in range(COLUMNAS):
            celda = matriz[f][c]
            
            if tipo == "cazador":
                # Cazador puede caminar en Camino y Lianas
                if isinstance(celda, (Camino, Liana)):
                    posiciones_validas.append((c * TAM + TAM//2, f * TAM + 70 + TAM//2))
            else:  # escapista
                # Escapista puede caminar en Camino y Túneles
                if isinstance(celda, (Camino, Tunel)):
                    posiciones_validas.append((c * TAM + TAM//2, f * TAM + 70 + TAM//2))
    
    return random.choice(posiciones_validas) if posiciones_validas else (TAM//2, 70 + TAM//2)

# --------------------------------------
# CLASE TRAMPA
# --------------------------------------
class Trampa:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.rect = pygame.Rect(x - 15, y - 15, 30, 30)
        self.tiempo_activacion = pygame.time.get_ticks()
        self.duracion = 5000  # 5 segundos
        self.activa = True
        
        # Crear sprite de trampa (círculo rojo)
        self.sprite = pygame.Surface((30, 30), pygame.SRCALPHA)
        pygame.draw.circle(self.sprite, (255, 0, 0, 180), (15, 15), 12)
        pygame.draw.circle(self.sprite, (255, 100, 100, 220), (15, 15), 8)
    
    def actualizar(self):
        """Actualiza el estado de la trampa y la desactiva después de 5 segundos"""
        tiempo_actual = pygame.time.get_ticks()
        if tiempo_actual - self.tiempo_activacion > self.duracion:
            self.activa = False
        return self.activa
    
    def dibujar(self, pantalla):
        """Dibuja la trampa en la pantalla"""
        if self.activa:
            pantalla.blit(self.sprite, self.rect)

# --------------------------------------
# CLASE ESCAPISTA IA (COMPATIBLE CON TU VERSIÓN)
# --------------------------------------
class EscapistaIA:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        
        # Sprite
        try:
            self.sprite = pygame.image.load("imagenes/imagen_de_escapista.png").convert_alpha()
            self.sprite = pygame.transform.scale(self.sprite, (24, 24))
        except:
            self.sprite = pygame.Surface((24, 24))
            self.sprite.fill((255, 0, 0))

        self.rect = self.sprite.get_rect(center=(x, y))
        self.velocidad = 2

        self.objetivo = None  # (fila, columna)
        
        # Trampas
        self.trampas = []
        self.tiempo_ultima_trampa = 0
        self.cooldown_trampa = 8000

    # --------------------------
    # TRAMPAS
    # --------------------------
    def colocar_trampa(self):
        tiempo = pygame.time.get_ticks()
        if (tiempo - self.tiempo_ultima_trampa > self.cooldown_trampa
            and len(self.trampas) < 3):

            self.trampas.append(Trampa(self.x, self.y))
            self.tiempo_ultima_trampa = tiempo

    def actualizar_trampas(self):
        nuevas = []
        for trampa in self.trampas:
            if trampa.actualizar():
                nuevas.append(trampa)
        self.trampas = nuevas

    # --------------------------
    # MOVIMIENTO
    # --------------------------
    def mover(self, cazador_pos, salidas, colisiones):
        cx, cy = cazador_pos

        # Distancia al cazador
        dist_cazador = ((self.x - cx)**2 + (self.y - cy)**2) ** 0.5

        # =====================================================
        # 1. HUIR DEL CAZADOR
        # =====================================================
        if dist_cazador < 150:
            dx = self.x - cx
            dy = self.y - cy

            mag = max((dx*dx + dy*dy)**0.5, 0.1)
            dx /= mag
            dy /= mag

            nueva_x = self.x + dx * self.velocidad
            nueva_y = self.y + dy * self.velocidad

            # posibilidad de colocar trampa
            if random.random() < 0.02:
                self.colocar_trampa()

        # =====================================================
        # 2. BUSCAR SALIDA MÁS CERCANA
        # =====================================================
        else:
            # salidas aquí es una lista de (fila, columna)
            if salidas:
                if not self.objetivo or random.random() < 0.02:
                    distancias = []
                    for f, c in salidas:
                        sx = c * TAM + TAM//2
                        sy = f * TAM + 70 + TAM//2
                        d = ((self.x - sx)**2 + (self.y - sy)**2)**0.5
                        distancias.append((d, (f, c)))

                    distancias.sort()
                    self.objetivo = distancias[0][1]

            if self.objetivo:
                f, c = self.objetivo
                target_x = c * TAM + TAM//2
                target_y = f * TAM + 70 + TAM//2

                dx = target_x - self.x
                dy = target_y - self.y

                mag = max((dx*dx + dy*dy)**0.5, 0.1)
                dx /= mag
                dy /= mag

                nueva_x = self.x + dx * self.velocidad
                nueva_y = self.y + dy * self.velocidad

            else:
                nueva_x = self.x + random.choice([-1, 0, 1]) * self.velocidad
                nueva_y = self.y + random.choice([-1, 0, 1]) * self.velocidad


        # =====================================================
        # 3. VERIFICAR COLISIONES + BORDES
        # =====================================================
        old = self.rect.copy()
        self.rect.center = (nueva_x, nueva_y)

        colision = False
        for r in colisiones:
            if self.rect.colliderect(r):
                colision = True
                break

        if self.rect.left < 0 or self.rect.right > ANCHO or \
            self.rect.top < 70 or self.rect.bottom > 70 + FILAS * TAM:
            colision = True

        if colision:
            self.rect = old
            self.x, self.y = self.rect.center
        else:
            self.x, self.y = nueva_x, nueva_y




# --------------------------------------
# CONSTRUCCIÓN DE COLISIONES
# --------------------------------------
def construir_colisiones(generador, matriz, modo="cazador"):
    colisiones = []
    rect_salidas = []

    for f in range(FILAS):
        for c in range(COLUMNAS):
            celda = matriz[f][c]

            rect = pygame.Rect(c * TAM, f * TAM + 70, TAM, TAM)

            if modo == "cazador":  
                # Cazador choca con Muros y Túneles
                if not celda.transitable_enemigo:
                    colisiones.append(rect)
            else:  # escapista
                # Escapista choca con Muros y Lianas
                if not celda.transitable_jugador:
                    colisiones.append(rect)

            if (f, c) in generador.salidas:
                rect_salidas.append(rect)

    return colisiones, rect_salidas

# ----------------------------------------------------------
# FUNCIÓN PRINCIPAL DEL MODO CAZADOR
# ----------------------------------------------------------
def modo_cazador(nombre_jugador):

    # Generación válida del mapa
    while True:
        generador = GeneradorMapa(FILAS, COLUMNAS)
        matriz = generador.generar_mapa()

        if verificar_ruta_escapista(matriz, generador.salidas):
            break
        else:
            print("Mapa inválido — regenerando...")

    colisiones_cazador, rect_salidas = construir_colisiones(generador, matriz, modo="cazador")
    colisiones_escapista, _ = construir_colisiones(generador, matriz, modo="escapa")

    pantalla = pygame.display.set_mode((ANCHO, ALTO))
    reloj = pygame.time.Clock()
    fuente = pygame.font.Font(None, 36)
    fuente_pequena = pygame.font.Font(None, 24)

    # Cazador aparece en posición válida
    cazador_x, cazador_y = encontrar_posicion_valida(matriz, "cazador")
    cazador = Avatar(cazador_x, cazador_y, tipo="cazador")
    cazador.sprite = pygame.transform.scale(cazador.sprite, (24, 24))
    cazador.rect = cazador.sprite.get_rect(center=(cazador_x, cazador_y))

    # Múltiples escapistas
    escapistas = []
    for _ in range(3):  # 3 escapistas iniciales
        escapista_x, escapista_y = encontrar_posicion_valida(matriz, "escapista")
        escapistas.append(EscapistaIA(escapista_x, escapista_y))

    # Variables de juego
    puntaje = 0
    escapistas_eliminados = 0
    escapistas_escapados = 0
    tiempo_inicio = pygame.time.get_ticks()
    corriendo = True

    # --------------------------------------
    # LOOP PRINCIPAL
    # --------------------------------------
    while corriendo:
        reloj.tick(60)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()

        # Movimiento del cazador con colisiones y límites de mapa
        old_x, old_y = cazador.x, cazador.y
        cazador.mover(keys)
        
        # Limitar a bordes del mapa
        """
        cazador.rect.clamp_ip(pygame.Rect(0, 70, ANCHO, ALTO - 70))
        cazador.x, cazador.y = cazador.rect.center
        """
        limite_mapa = pygame.Rect(0, 70, ANCHO, FILAS * TAM)
        cazador.rect.clamp_ip(limite_mapa)
        cazador.x, cazador.y = cazador.rect.center

        # Verificar colisiones del cazador
        colision_cazador = False
        for colision_rect in colisiones_cazador:
            if cazador.rect.colliderect(colision_rect):
                colision_cazador = True
                break
        
        if colision_cazador:
            cazador.rect.center = (old_x, old_y)
            cazador.x, cazador.y = old_x, old_y

        # Movimiento de los escapistas
        cazador_pos = (cazador.x, cazador.y)
        for escapista in escapistas[:]:  # Copia para modificar durante iteración
            escapista.mover(cazador_pos, generador.salidas, colisiones_escapista)
            escapista.actualizar_trampas()

            # Verificar si el cazador pisa una trampa
            for trampa in escapista.trampas[:]:
                if trampa.activa and cazador.rect.colliderect(trampa.rect):
                    print("¡El cazador cayó en una trampa! -30 puntos y congelado por 2 segundos")
                    puntaje = max(0, puntaje - 30)
                    escapista.trampas.remove(trampa)
                    # Aquí podrías agregar un efecto de congelación temporal

            # Captura → eliminar escapista
            if cazador.rect.colliderect(escapista.rect):
                print("¡El cazador atrapó a un escapista! +50 puntos")
                escapistas.remove(escapista)
                puntaje += 50
                escapistas_eliminados += 1
                
                # Generar nuevo escapista
                if len(escapistas) < 5:  # Máximo 5 escapistas
                    escapista_x, escapista_y = encontrar_posicion_valida(matriz, "escapista")
                    escapistas.append(EscapistaIA(escapista_x, escapista_y))

            # Escapista llega a una salida → perder puntos
            for rect_s in rect_salidas:
                if escapista.rect.colliderect(rect_s):
                    print("¡Un escapista escapó! -40 puntos")
                    escapistas.remove(escapista)
                    puntaje = max(0, puntaje - 40)  # No menor a 0
                    escapistas_escapados += 1
                    
                    # Generar nuevo escapista
                    if len(escapistas) < 5:
                        escapista_x, escapista_y = encontrar_posicion_valida(matriz, "escapista")
                        escapistas.append(EscapistaIA(escapista_x, escapista_y))
                    break

        # Condición de fin de juego
        from puntajes import GestorPuntajes
        if escapistas_eliminados >= 10:
            print(f"¡Victoria! Puntaje final: {puntaje}")
            # GUARDAR PUNTAJE
            gestor = GestorPuntajes()
            gestor.agregar_puntaje("cazador", nombre_jugador, puntaje)
            print(f"PUNTAJE GUARDADO - Modo: cazador, Jugador: {nombre_jugador}, Puntos: {puntaje}")
            return puntaje
        elif escapistas_escapados >= 10:
            print(f"¡Derrota! Demasiados escapistas huyeron. Puntaje final: {puntaje}")
            # GUARDAR PUNTAJE
            gestor = GestorPuntajes()
            gestor.agregar_puntaje("cazador", nombre_jugador, puntaje)
            print(f"PUNTAJE GUARDADO - Modo: cazador, Jugador: {nombre_jugador}, Puntos: {puntaje}")
            return puntaje

        # --------------------------------------
        # DIBUJAR
        # --------------------------------------
        pantalla.fill((0, 0, 0))

        # HUD negro
        pygame.draw.rect(pantalla, COLOR_HUD, (0, 0, ANCHO, 70))

        # Información del HUD - MEJOR DISTRIBUCIÓN
        txt_nombre = fuente.render(f"{nombre_jugador}", True, (255, 255, 255))
        txt_puntaje = fuente.render(f"Puntos: {puntaje}", True, (255, 255, 255))
        txt_eliminados = fuente_pequena.render(f"Atrapados: {escapistas_eliminados}", True, (255, 255, 255))
        txt_escapados = fuente_pequena.render(f"Escapados: {escapistas_escapados}", True, (255, 255, 255))
        
        # Izquierda: Nombre y estadísticas
        pantalla.blit(txt_nombre, (20, 15))
        pantalla.blit(txt_eliminados, (20, 45))
        
        # Derecha: Puntos y escapados
        pantalla.blit(txt_puntaje, (ANCHO - txt_puntaje.get_width() - 20, 15))
        pantalla.blit(txt_escapados, (ANCHO - txt_escapados.get_width() - 20, 45))

        # Barra de stamina CENTRADA en el HUD (debajo del nombre)
        barra_ancho = 120
        barra_alto = 12
        x_centro = (ANCHO - barra_ancho) // 2
        y_centro = 50  # Posición más baja para no tapar texto

        # Fondo de la barra
        pygame.draw.rect(pantalla, (50, 50, 50), (x_centro-2, y_centro-2, barra_ancho+4, barra_alto+4))
        
        # Porcentaje de stamina
        porcentaje = cazador.stamina / cazador.stamina_max
        
        # Barra de stamina (amarilla)
        if porcentaje > 0:
            pygame.draw.rect(pantalla, (255, 255, 0), (x_centro, y_centro, barra_ancho * porcentaje, barra_alto))
        
        # Texto "Stamina" sobre la barra
        txt_stamina = fuente_pequena.render("Stamina", True, (200, 200, 200))
        pantalla.blit(txt_stamina, (x_centro + (barra_ancho - txt_stamina.get_width()) // 2, y_centro - 20))

        # Mapa
        for f in range(FILAS):
            for c in range(COLUMNAS):
                celda = matriz[f][c]
                r = pygame.Rect(c * TAM, f * TAM + 70, TAM, TAM)
                pygame.draw.rect(pantalla, celda.color, r)
                # Dibujar bordes para mejor visibilidad
                pygame.draw.rect(pantalla, (50, 50, 50), r, 1)

        # Salidas (amarillas)
        for s in rect_salidas:
            pygame.draw.rect(pantalla, COLOR_SALIDA, s)

        # Dibujar trampas
        for escapista in escapistas:
            for trampa in escapista.trampas:
                trampa.dibujar(pantalla)

        # Dibujar sprites
        pantalla.blit(cazador.sprite, cazador.rect)
        for escapista in escapistas:
            pantalla.blit(escapista.sprite, escapista.rect)

        pygame.display.flip()

    pygame.quit()
    return puntaje