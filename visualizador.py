import pygame
from mapa import GeneradorMapa

ANCHO = 800
ALTO = 800

pygame.init()
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Laberinto-Proyecto 2 TEC")

COLOR_SALIDA = (255, 255, 0)   # Amarillo
COLOR_INICIO = (0, 255, 255)   # Cyan (opcional, para que se vea mejor)

def dibujar_mapa(matriz, salidas):
    filas = len(matriz)
    columnas = len(matriz[0])

    tam_fila = ALTO // filas
    tam_col = ANCHO // columnas

    for f in range(filas):
        for c in range(columnas):
            x = c * tam_col
            y = f * tam_fila

            # Dibujar el color de la casilla normal
            pygame.draw.rect(pantalla, matriz[f][c].color, (x, y, tam_col, tam_fila))

            # Pintar inicio (0,0)
            if (f, c) == (0, 0):
                pygame.draw.rect(pantalla, COLOR_INICIO, (x, y, tam_col, tam_fila))

            # Pintar salidas
            if (f, c) in salidas:
                pygame.draw.rect(pantalla, COLOR_SALIDA, (x, y, tam_col, tam_fila))


def main():
    generador = GeneradorMapa(25, 25)
    mapa = generador.generar_mapa()
    salidas = generador.salidas

    corriendo = True

    while corriendo:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                corriendo = False

            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_r:
                    mapa = generador.generar_mapa()
                    salidas = generador.salidas  # ACTUALIZAR SALIDAS

        pantalla.fill((0, 0, 0))
        dibujar_mapa(mapa, salidas)
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
