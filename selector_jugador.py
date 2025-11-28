import pygame
import sys
import os
import json

ANCHO = 800
ALTO = 600
ARCHIVO = "jugadores.json"

def cargar_registro():
    if not os.path.exists(ARCHIVO):
        return {"jugadores": [], "puntajes": {}}

    with open(ARCHIVO, "r") as f:
        return json.load(f)

def selector_jugador(modo):
    """
    Funciona para cualquiera de los dos modos, ya sea "Escapa" o "Cazador"
    retorna el nombre del jugador seleccionado o None si se cancela y no se selecciona ningun jugador
    """

    pygame.init()
    pantalla = pygame.display.set_mode((ANCHO, ALTO))
    pygame.display.set_caption(f"Seleccionar Jugador - Modo {modo}")

    fuente_titulo = pygame.font.Font(None, 60)
    fuente_lista = pygame.font.Font(None, 40)
    fuente_boton = pygame.font.Font(None, 40)

    fondo = pygame.image.load(os.path.join("imagenes", "fondo_piedra.png")).convert()
    fondo = pygame.transform.scale(fondo, (ANCHO, ALTO))

    data = cargar_registro()
    jugadores = data["jugadores"]

    seleccionado = 0  # índice jugador seleccionado

    reloj = pygame.time.Clock()

    while True:
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = False

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_UP:
                    seleccionado = max(0, seleccionado - 1)

                if evento.key == pygame.K_DOWN:
                    seleccionado = min(len(jugadores) - 1, seleccionado + 1)

                if evento.key == pygame.K_RETURN:
                    if jugadores:
                        return jugadores[seleccionado]

            if evento.type == pygame.MOUSEBUTTONDOWN:
                mouse_click = True

        pantalla.blit(fondo, (0, 0))

        titulo = fuente_titulo.render("SELECCIONAR JUGADOR", True, (230, 220, 200))
        pantalla.blit(titulo, titulo.get_rect(center=(ANCHO//2, 80)))

        # Lista de jugadores
        y = 180
        for i, jugador in enumerate(jugadores):
            color = (255, 255, 255) if i == seleccionado else (200, 200, 200)
            txt = fuente_lista.render(jugador, True, color)
            pantalla.blit(txt, (280, y))
            y += 50

        # Botón seleccionar
        rect_sel = pygame.Rect(250, 480, 150, 55)
        pygame.draw.rect(pantalla, (180, 160, 80), rect_sel, border_radius=10)
        pantalla.blit(fuente_boton.render("Seleccionar", True, (0, 0, 0)),
                      fuente_boton.render("Seleccionar", True, (0,0,0)).get_rect(center=rect_sel.center))

        # Botón volver
        rect_volver = pygame.Rect(420, 480, 150, 55)
        pygame.draw.rect(pantalla, (120, 90, 50), rect_volver, border_radius=10)
        pantalla.blit(fuente_boton.render("Volver", True, (0, 0, 0)),
                      fuente_boton.render("Volver", True, (0,0,0)).get_rect(center=rect_volver.center))

        # Click seleccionar
        if rect_sel.collidepoint(mouse_pos) and mouse_click:
            if jugadores:
                return jugadores[seleccionado]

        # Click volver
        if rect_volver.collidepoint(mouse_pos) and mouse_click:
            return None

        pygame.display.flip()
        reloj.tick(60)