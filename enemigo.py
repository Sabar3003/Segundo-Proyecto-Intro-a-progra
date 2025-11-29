import pygame
import random
from mapa import Camino, Liana, Tunel

TAM = 32
HUD = 70  # Altura reservada para HUD

class Enemigo:
    """
    Clase base que define atributos comunes para cualquier enemigo.
    NO define movimiento: eso lo implementan las subclases.
    """
    def __init__(self, x, y, velocidad, sprite):
        self.x = x
        self.y = y
        self.velocidad = velocidad
        self.sprite = sprite
        self.rect = sprite.get_rect(center=(x, y))

    def mover(self, *args, **kwargs):
        raise NotImplementedError("El método mover debe implementarse en las subclases.")


class EnemigoPerseguidor(Enemigo):
    """
    Enemigos del modo ESCAPA. PERSEGUEN al jugador.
    """
    def mover(self, objetivo_pos, matriz, colisiones):
        ex, ey = objetivo_pos

        celda_x = int(self.x // TAM)
        celda_y = int((self.y - HUD) // TAM)

        direcciones = []

        for dx, dy in [(1,0),(-1,0),(0,1),(0,-1)]:
            nueva_cx = celda_x + dx
            nueva_cy = celda_y + dy
            
            if 0 <= nueva_cx < len(matriz[0]) and 0 <= nueva_cy < len(matriz):
                celda = matriz[nueva_cy][nueva_cx]

                # Perseguidor puede moverse por CAMINO y LIANA
                if isinstance(celda, (Camino, Liana)):
                    tx = nueva_cx * TAM + TAM//2
                    ty = nueva_cy * TAM + HUD + TAM//2
                    distancia = ((tx - ex)**2 + (ty - ey)**2)**0.5
                    direcciones.append((distancia, dx, dy))

        if direcciones:
            direcciones.sort()
            _, dx, dy = direcciones[0]
            nueva_x = self.x + dx * self.velocidad
            nueva_y = self.y + dy * self.velocidad
        else:
            # Movimiento aleatorio si queda encerrado
            nueva_x = self.x + random.choice([-1, 0, 1]) * self.velocidad
            nueva_y = self.y + random.choice([-1, 0, 1]) * self.velocidad

        old = self.rect.copy()
        self.rect.center = (nueva_x, nueva_y)

        # Colisiones
        colision = False
        for col in colisiones:
            if self.rect.colliderect(col):
                colision = True
                break

        if colision:
            self.rect = old
        else:
            self.x, self.y = nueva_x, nueva_y


class EnemigoHuya(Enemigo):
    """
    Enemigos del modo CAZADOR. HUYEN del cazador/jugador.
    """
    def mover(self, jugador_pos, matriz, colisiones):
        jx, jy = jugador_pos

        dx = self.x - jx
        dy = self.y - jy

        distancia = max((dx**2 + dy**2)**0.5, 0.1)

        dx /= distancia
        dy /= distancia

        nueva_x = self.x + dx * self.velocidad
        nueva_y = self.y + dy * self.velocidad

        old = self.rect.copy()
        self.rect.center = (nueva_x, nueva_y)

        colision = False
        for col in colisiones:
            if self.rect.colliderect(col):
                colision = True
                break

        if colision:
            self.rect = old
        else:
            self.x, self.y = nueva_x, nueva_y
