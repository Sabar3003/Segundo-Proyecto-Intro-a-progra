import pygame
from pygame.locals import *
import os

def cargar_imagen(ruta, usar_alpha=False):
    if not os.path.exists(ruta):
        print(f"ADVERTENCIA: no se encontró la imagen: {ruta}")
        return None
    img = pygame.image.load(ruta)
    return img.convert_alpha() if usar_alpha else img.convert()

def ventana_controles():
    ANCHO = 600
    ALTO = 400

    pygame.init()
    ventana = pygame.display.set_mode((ANCHO, ALTO))
    pygame.display.set_caption("Controles del Juego")

    # Cargar fondo bonito (piedras con enredaderas)
    fondo = cargar_imagen(os.path.join("imagenes", "fondo_piedra.png"))
    if fondo:
        fondo = pygame.transform.scale(fondo, (ANCHO, ALTO))

    # Fuentes
    fuente_titulo = pygame.font.Font(None, 50)
    fuente_texto = pygame.font.Font(None, 32)

    # Título
    titulo = fuente_titulo.render("CONTROLES DEL JUEGO", True, (255, 255, 255))

    # Lista de controles visibles
    textos = [
        "Movimiento: W A S D",
        "Sprint: F",
        "Colocar trampa utilizable en el Modo Escapa: G",
        "Cerrar ventana: ESC"
    ]

    color_texto = (240, 240, 220)

    corriendo = True
    while corriendo:
        for evento in pygame.event.get():
            if evento.type == QUIT:
                pygame.quit()
                return
            if evento.type == KEYDOWN and evento.key == K_ESCAPE:
                corriendo = False

        # Dibujar fondo
        if fondo:
            ventana.blit(fondo, (0, 0))
        else:
            ventana.fill((30, 30, 30))

        # Oscurecer ligeramente para que el texto se lea mejor
        capa = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
        capa.fill((0, 0, 0, 100))
        ventana.blit(capa, (0, 0))

        # Título en la parte superior
        ventana.blit(titulo, (ANCHO // 2 - titulo.get_width() // 2, 40))

        # Texto de controles
        y = 150
        for t in textos:
            r = fuente_texto.render(t, True, color_texto)
            ventana.blit(r, (ANCHO // 2 - r.get_width() // 2, y))
            y += 50

        pygame.display.flip()

    pygame.quit()
