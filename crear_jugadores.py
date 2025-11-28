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
    
def limpiar_jugadores(): # se encarga de limpiar la lista de jugadores en caso de presionar el boton
    data = {"jugadores": [], "puntajes": {}}
    guardar_registro(data)


def guardar_registro(data):
    with open(ARCHIVO, "w") as f:
        json.dump(data, f, indent=4)


def crear_jugadores():
    pygame.init()
    pantalla = pygame.display.set_mode((ANCHO, ALTO))
    pygame.display.set_caption("Crear jugadores")

    # Fuentes
    fuente_titulo = pygame.font.Font(None, 60)
    fuente_normal = pygame.font.Font(None, 40)
    fuente_lista = pygame.font.Font(None, 32)

    # Cargar fondo de piedra
    fondo = pygame.image.load(os.path.join("imagenes", "fondo_piedra.png")).convert()
    fondo = pygame.transform.scale(fondo, (ANCHO, ALTO))

    # Input variables
    texto_nombre = ""
    input_activo = False

    reloj = pygame.time.Clock()

    while True:
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = False

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if evento.type == pygame.MOUSEBUTTONDOWN:
                mouse_click = True

                # Activar input
                if 250 <= mouse_pos[0] <= 550 and 150 <= mouse_pos[1] <= 200:
                    input_activo = True
                else:
                    input_activo = False

                # Botón agregar jugador
                if 300 <= mouse_pos[0] <= 500 and 240 <= mouse_pos[1] <= 290:
                    if texto_nombre.strip() != "":
                        data = cargar_registro()
                        nombre = texto_nombre.strip()

                        if nombre not in data["jugadores"]:
                            data["jugadores"].append(nombre)
                            data["puntajes"][nombre] = {"Escapa": 0, "Cazador": 0}
                            guardar_registro(data)

                        texto_nombre = ""  # limpiar input

                # Botón volver
                if 300 <= mouse_pos[0] <= 500 and 500 <= mouse_pos[1] <= 560:
                    return  # volver al menú

            # Escribir en el input
            if evento.type == pygame.KEYDOWN and input_activo:
                if evento.key == pygame.K_BACKSPACE:
                    texto_nombre = texto_nombre[:-1]
                elif evento.key == pygame.K_RETURN:
                    pass
                else:
                    if len(texto_nombre) < 12:
                        texto_nombre += evento.unicode

        # dibuja la pantalla
        pantalla.blit(fondo, (0, 0))

        # Título
        titulo = fuente_titulo.render("CREAR JUGADORES", True, (230, 230, 200))
        rect_titulo = titulo.get_rect(center=(ANCHO//2, 70))
        pantalla.blit(titulo, rect_titulo)

        # Input
        color_input = (60, 60, 60) if input_activo else (40, 40, 40)
        pygame.draw.rect(pantalla, color_input, (250, 150, 300, 50), border_radius=10)

        txt_surface = fuente_normal.render(texto_nombre, True, (255, 255, 255))
        pantalla.blit(txt_surface, (260, 155))

        # Botón de agregar jugadores
        pygame.draw.rect(pantalla, (180, 150, 90), (300, 240, 200, 50), border_radius=10)

        # Se encarga de centrar el texto del boton de agregar jugadores
        texto_agregar = fuente_normal.render("Agregar", True, (0, 0, 0))
        rect_agregar = texto_agregar.get_rect(center=(300 + 100, 240 + 25))  # centro del botón
        pantalla.blit(texto_agregar, rect_agregar)


        # Lista de jugadores
        data = cargar_registro()
        y = 320
        for jugador in data["jugadores"]:
            texto = fuente_lista.render(jugador, True, (255, 255, 255))
            pantalla.blit(texto, (260, y))
            y += 35

        # Configuracion del boton para volver al menu principal
        btn_volver_rect = pygame.Rect(220, 500, 160, 55)
        pygame.draw.rect(pantalla, (120, 90, 50), btn_volver_rect, border_radius=10)

        txt_volver = fuente_normal.render("Volver", True, (0, 0, 0))
        pantalla.blit(txt_volver, txt_volver.get_rect(center=btn_volver_rect.center))

        # Configuracion del boton para limpiar la lista de jugadores
        btn_limpiar_rect = pygame.Rect(420, 500, 220, 55)
        pygame.draw.rect(pantalla, (200, 50, 50), btn_limpiar_rect, border_radius=10)

        txt_limpiar = fuente_normal.render("Limpiar lista", True, (0, 0, 0))
        pantalla.blit(txt_limpiar, txt_limpiar.get_rect(center=btn_limpiar_rect.center))

        # Botón VOLVER
        if btn_volver_rect.collidepoint(mouse_pos) and mouse_click:
            return  # vuelve al menú principal

        # Botón LIMPIAR LISTA
        if btn_limpiar_rect.collidepoint(mouse_pos) and mouse_click:
            limpiar_jugadores()  # elimina todos los jugadores

        pygame.display.flip()
        reloj.tick(60)
