import pygame
import sys
import random
from avatar import Avatar
from mapa import GeneradorMapa, Muro, Tunel, Liana, Camino
from collections import deque
from puntajes import GestorPuntajes

# --------------------------------------
# CONFIGURACIÓN GENERAL
# --------------------------------------
TAM = 32
FILAS = 20
COLUMNAS = 25

ANCHO = COLUMNAS * TAM
ALTO = FILAS * TAM + 70

COLOR_HUD = (0, 0, 0)
COLOR_SALIDA = (255, 230, 0)

pygame.init()
pygame.display.set_caption("Modo Escapa")

# --------------------------------------
# CLASE TRAMPA
# --------------------------------------
class Trampa:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.rect = pygame.Rect(x - 15, y - 15, 30, 30)
        self.tiempo_activacion = pygame.time.get_ticks()
        self.duracion = 5000  # 5 segundos visibles en el mapa
        self.activa = True
        
        # Sprite de trampa (círculo rojo)
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
# CLASE CAZADOR IA
# --------------------------------------
from enemigo import EnemigoPerseguidor
import pygame

class CazadorIA(EnemigoPerseguidor):
    def __init__(self, x, y):
        try:
            sprite = pygame.image.load("imagenes/Imagen_cazador.png").convert_alpha()
            sprite = pygame.transform.scale(sprite, (24, 24))
        except:
            sprite = pygame.Surface((24, 24))
            sprite.fill((0, 0, 255))

        super().__init__(x, y, velocidad=1.5, sprite=sprite)

# --------------------------------------
# FUNCIÓN PARA VERIFICAR QUE EL MAPA SEA JUGABLE
# --------------------------------------
def verificar_ruta_jugador(matriz, salidas):
    inicio = (0, 0)
    FIL = len(matriz)
    COL = len(matriz[0])

    q = deque([inicio])
    visitado = set([inicio])

    while q:
        f, c = q.popleft()

        if (f, c) in salidas:
            return True

        for df, dc in [(1,0), (-1,0), (0,1), (0,-1)]:
            nf, nc = f + df, c + dc
            if 0 <= nf < FIL and 0 <= nc < COL:
                if (nf, nc) not in visitado and matriz[nf][nc].transitable_jugador:
                    visitado.add((nf, nc))
                    q.append((nf, nc))

    return False

# --------------------------------------
# FUNCIONES AUXILIARES
# --------------------------------------
def construir_colisiones(generador, matriz, modo="escapista"):
    """
    Devuelve lista de rects NO transitables según el modo
    """
    colisiones = []
    rect_salidas = []

    for f in range(FILAS):
        for c in range(COLUMNAS):
            celda = matriz[f][c]
            rect = pygame.Rect(c * TAM, f * TAM + 70, TAM, TAM)
            

            if modo == "escapista":
                # Escapista choca con Muros y Lianas
                if not celda.transitable_jugador:
                    colisiones.append(rect)
            else:  # cazador
                # Cazador choca con Muros y Túneles
                if not celda.transitable_enemigo:
                    colisiones.append(rect)

            # Salidas amarillas
            if (f, c) in generador.salidas:
                rect_salidas.append(rect)

    return colisiones, rect_salidas

def encontrar_posicion_valida_cazador(matriz):
    """Encuentra una posición válida para cazador (Camino o Lianas)"""
    posiciones_validas = []
    
    for f in range(FILAS):
        for c in range(COLUMNAS):
            celda = matriz[f][c]
            # Cazador puede caminar en Camino y Lianas
            if isinstance(celda, (Camino, Liana)):
                posiciones_validas.append((c * TAM + TAM//2, f * TAM + 70 + TAM//2))
    
    return random.choice(posiciones_validas) if posiciones_validas else (TAM//2, 70 + TAM//2)

# ----------------------------------------------------------
# FUNCIÓN PRINCIPAL DEL MODO ESCAPA
# ----------------------------------------------------------
def modo_escapa(nombre_jugador):

    # --------------------------------------
    # GENERACIÓN VALIDADA DEL MAPA
    # --------------------------------------
    while True:
        generador = GeneradorMapa(FILAS, COLUMNAS)
        matriz = generador.generar_mapa()

        if verificar_ruta_jugador(matriz, generador.salidas):
            break
        else:
            print("❌ Mapa inválido — regenerando...\n")

    # Construcción de colisiones
    colisiones_escapista, rect_salidas = construir_colisiones(generador, matriz, "escapista")
    colisiones_cazador, _ = construir_colisiones(generador, matriz, "cazador")

    # --------------------------------------
    # CONFIGURACIÓN DE PYGAME
    # --------------------------------------
    pantalla = pygame.display.set_mode((ANCHO, ALTO))
    reloj = pygame.time.Clock()
    fuente = pygame.font.Font(None, 36)
    fuente_pequena = pygame.font.Font(None, 24)

    # Avatar del escapista
    jugador = Avatar(32 // 2, 32 // 2 + 70, tipo="escapa")
    jugador.sprite = pygame.transform.scale(jugador.sprite, (24, 24))
    jugador.rect = jugador.sprite.get_rect(center=(16, 16 + 70))

    # Cazadores iniciales
    cazadores = []
    for _ in range(3):  # 3 cazadores iniciales
        cazador_x, cazador_y = encontrar_posicion_valida_cazador(matriz)
        cazadores.append(CazadorIA(cazador_x, cazador_y))

    # Variables de juego - NUEVA LÓGICA DE TRAMPAS
    trampas_activas = []  # Trampas colocadas en el mapa
    trampas_disponibles = 3  # Trampas que el jugador tiene disponibles
    tiempo_ultima_trampa = 0
    cooldown_recarga = 10000  # 10 segundos para recuperar trampa
    
    puntaje = 0
    tiempo_inicio = pygame.time.get_ticks()
    corriendo = True
    juego_terminado = False
    resultado = ""

    # --------------------------------------
    # LOOP PRINCIPAL
    # --------------------------------------
    while corriendo:
        dt = reloj.tick(60)
        tiempo_actual = pygame.time.get_ticks()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if not juego_terminado and evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_g and trampas_disponibles > 0:
                    # Colocar nueva trampa
                    nueva_trampa = Trampa(jugador.x, jugador.y)
                    trampas_activas.append(nueva_trampa)
                    trampas_disponibles -= 1
                    tiempo_ultima_trampa = tiempo_actual
                    print(f"¡Trampa colocada! Trampas disponibles: {trampas_disponibles}")
        from puntajes import GestorPuntajes
        if juego_terminado:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE]:
                gestor = GestorPuntajes()
                gestor.agregar_puntaje("escapa", nombre_jugador, puntaje)
                return puntaje
            continue

        # RECARGAR TRAMPAS - NUEVA LÓGICA
        if trampas_disponibles < 3 and (tiempo_actual - tiempo_ultima_trampa > cooldown_recarga):
            trampas_disponibles += 1
            tiempo_ultima_trampa = tiempo_actual
            print(f"¡Trampa recargada! Trampas disponibles: {trampas_disponibles}")

        keys = pygame.key.get_pressed()

        # Guardar posición anterior para colisiones
        old_x, old_y = jugador.rect.x, jugador.rect.y

        # Movimiento del escapista
        jugador.mover(keys, colisiones_escapista)

        # Limitar movimiento a bordes del mapa
        if jugador.rect.left < 0:
            jugador.rect.left = 0
        if jugador.rect.right > ANCHO:
            jugador.rect.right = ANCHO
        if jugador.rect.top < 70:
            jugador.rect.top = 70
        if jugador.rect.bottom > ALTO:
            jugador.rect.bottom = ALTO

        jugador.x, jugador.y = jugador.rect.center

        # Colisiones del escapista con muros
        colision_detectada = False
        for muro in colisiones_escapista:
            if jugador.rect.colliderect(muro):
                colision_detectada = True
                break
        
        if colision_detectada:
            jugador.rect.x, jugador.rect.y = old_x, old_y
            jugador.x, jugador.y = jugador.rect.center

        # Actualizar trampas activas
        trampas_activas = [trampa for trampa in trampas_activas if trampa.actualizar()]

        # Movimiento de cazadores
        escapista_pos = (jugador.x, jugador.y)
        for cazador in cazadores[:]:
            cazador.mover(escapista_pos, matriz, colisiones_cazador)

            # Verificar si cazador pisa una trampa
            for trampa in trampas_activas[:]:
                if trampa.activa and cazador.rect.colliderect(trampa.rect):
                    print("¡Cazador eliminado! +10 puntos")
                    cazadores.remove(cazador)
                    trampas_activas.remove(trampa)
                    puntaje += 10
                    
                    # Generar nuevo cazador
                    cazador_x, cazador_y = encontrar_posicion_valida_cazador(matriz)
                    cazadores.append(CazadorIA(cazador_x, cazador_y))
                    break

            # Verificar si cazador atrapa al escapista
            from puntajes import GestorPuntajes
                        # Verificar si cazador atrapa al escapista
            if jugador.rect.colliderect(cazador.rect):
                print("¡Has sido atrapado! -50 puntos")
                puntaje = max(0, puntaje - 50)
                juego_terminado = True
                resultado = "DERROTA - Te atraparon"
                
                # GUARDAR PUNTAJE
                from puntajes import GestorPuntajes
                gestor = GestorPuntajes()
                gestor.agregar_puntaje("escapa", nombre_jugador, puntaje)
                print(f"PUNTAJE GUARDADO - Modo: escapa, Jugador: {nombre_jugador}, Puntos: {puntaje}")
                break

        # Detectar salida exitosa
        from puntajes import GestorPuntajes
                # Detectar salida exitosa
                # Detectar salida exitosa
        for salida in rect_salidas:
            if jugador.rect.colliderect(salida):
                print("¡HAS ESCAPADO ÉXITOSAMENTE! +100 puntos")
                puntaje += 100
                juego_terminado = True
                resultado = "VICTORIA - Lograste escapar"
                
                # GUARDAR PUNTAJE - ESTO ES LO QUE FALTA
                print("Guardando puntaje...")
                gestor = GestorPuntajes()
                gestor.agregar_puntaje("escapa", nombre_jugador, puntaje)
                print("Puntaje guardado exitosamente")
                break
                
                # GUARDAR PUNTAJE 
                from puntajes import GestorPuntajes
                gestor = GestorPuntajes()
                gestor.agregar_puntaje("escapa", nombre_jugador, puntaje)
                print(f"PUNTAJE GUARDADO - Modo: escapa, Jugador: {nombre_jugador}, Puntos: {puntaje}")
                break

        # --------------------------------------
        # DIBUJAR
        # --------------------------------------
        pantalla.fill((0, 0, 0))

        # HUD
        pygame.draw.rect(pantalla, COLOR_HUD, (0, 0, ANCHO, 70))

        # Texto HUD
        txt_nombre = fuente.render(f"Jugador: {nombre_jugador}", True, (255, 255, 255))
        txt_puntaje = fuente.render(f"Puntos: {puntaje}", True, (255, 255, 255))
        txt_trampas = fuente_pequena.render(f"Trampas: {trampas_disponibles}/3", True, (255, 255, 255))
        
        pantalla.blit(txt_nombre, (20, 15))
        pantalla.blit(txt_puntaje, (ANCHO - txt_puntaje.get_width() - 20, 15))
        pantalla.blit(txt_trampas, (20, 45))

        # Barra de stamina
        barra_ancho = 120
        barra_alto = 12
        x_centro = (ANCHO - barra_ancho) // 2
        y_centro = 50

        pygame.draw.rect(pantalla, (50, 50, 50), (x_centro-2, y_centro-2, barra_ancho+4, barra_alto+4))
        
        porcentaje = jugador.stamina / jugador.stamina_max
        if porcentaje > 0:
            pygame.draw.rect(pantalla, (255, 255, 0), (x_centro, y_centro, barra_ancho * porcentaje, barra_alto))
        
        txt_stamina = fuente_pequena.render("Stamina", True, (200, 200, 200))
        pantalla.blit(txt_stamina, (x_centro + (barra_ancho - txt_stamina.get_width()) // 2, y_centro - 20))

        # MAPA
        for f in range(FILAS):
            for c in range(COLUMNAS):
                celda = matriz[f][c]
                r = pygame.Rect(c * TAM, f * TAM + 70, TAM, TAM)
                pygame.draw.rect(pantalla, celda.color, r)
                # Dibujar bordes para mejor visibilidad
                pygame.draw.rect(pantalla, (50, 50, 50), r, 1)

        # Salidas amarillas
        for s in rect_salidas:
            pygame.draw.rect(pantalla, COLOR_SALIDA, s)

        # Dibujar trampas activas
        for trampa in trampas_activas:
            trampa.dibujar(pantalla)

        # Dibujar sprites
        pantalla.blit(jugador.sprite, jugador.rect)
        for cazador in cazadores:
            pantalla.blit(cazador.sprite, cazador.rect)

        # Pantalla de resultado
        if juego_terminado:
            overlay = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            pantalla.blit(overlay, (0, 0))
            
            txt_resultado = fuente.render(resultado, True, (255, 255, 255))
            txt_puntaje_final = fuente.render(f"Puntaje final: {puntaje}", True, (255, 255, 255))
            txt_continuar = fuente_pequena.render("Presiona ESPACIO para continuar", True, (200, 200, 200))
            
            pantalla.blit(txt_resultado, (ANCHO//2 - txt_resultado.get_width()//2, ALTO//2 - 40))
            pantalla.blit(txt_puntaje_final, (ANCHO//2 - txt_puntaje_final.get_width()//2, ALTO//2))
            pantalla.blit(txt_continuar, (ANCHO//2 - txt_continuar.get_width()//2, ALTO//2 + 40))

        pygame.display.flip()

    pygame.quit()
    return puntaje