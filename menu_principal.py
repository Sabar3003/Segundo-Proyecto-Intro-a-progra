import pygame
import sys
import os

# Configuración de la ventana del juego

ANCHO = 800
ALTO = 600

COLOR_TEXTO = (40, 25, 10)
COLOR_TEXTO_RESALTADO = (80, 50, 20)
COLOR_BOTON = (210, 190, 150)          # piedra clara
COLOR_BOTON_BORDE = (120, 90, 50)      # borde piedra
COLOR_BOTON_HOVER = (230, 210, 170)    # piedra iluminada
COLOR_SOMBRA = (0, 0, 0)
COLOR_TITULO = (230, 200, 120)

FPS = 60


#Se encarga de realizar una clase para los botones

class Boton:
    def __init__(self, texto, centro, ancho=260, alto=55):
        self.texto = texto
        self.rect = pygame.Rect(0, 0, ancho, alto)
        self.rect.center = centro

    def draw(self, surface, fuente, mouse_pos):
        esta_hover = self.rect.collidepoint(mouse_pos)

        # sombra
        sombra_rect = self.rect.copy()
        sombra_rect.x += 3
        sombra_rect.y += 3
        pygame.draw.rect(surface, COLOR_SOMBRA, sombra_rect, border_radius=12)

        # botón principal
        color_fondo = COLOR_BOTON_HOVER if esta_hover else COLOR_BOTON
        pygame.draw.rect(surface, color_fondo, self.rect, border_radius=12)

        # borde
        pygame.draw.rect(surface, COLOR_BOTON_BORDE, self.rect, width=3, border_radius=12)

        # texto
        color_texto = COLOR_TEXTO_RESALTADO if esta_hover else COLOR_TEXTO
        superficie_texto = fuente.render(self.texto, True, color_texto)
        texto_rect = superficie_texto.get_rect(center=self.rect.center)
        surface.blit(superficie_texto, texto_rect)

        return esta_hover

    def fue_click(self, mouse_pos, mouse_down):
        return mouse_down and self.rect.collidepoint(mouse_pos)


# Se encarga de cargar lo necesario para el diseño del menu

def cargar_imagen(ruta, usar_alpha=False):
    if not os.path.exists(ruta):
        print(f"ADVERTENCIA: no se encontró la imagen: {ruta}")
        return None
    img = pygame.image.load(ruta)
    return img.convert_alpha() if usar_alpha else img.convert()


def recortar_antorcha_sprites(sheet, num_frames=7):
    """
    Corta el sprite sheet horizontal de la antorcha en frames individuales.
    """
    frames = []
    ancho_total = sheet.get_width()
    alto = sheet.get_height()
    frame_ancho = ancho_total // num_frames

    for i in range(num_frames):
        rect = pygame.Rect(i * frame_ancho, 0, frame_ancho, alto)
        frame = sheet.subsurface(rect)
        frames.append(frame)

    return frames


# Se encarga de las funciones principales del menú

def menu_principal(nombre_jugador="Jugador"):
    pygame.init()
    pantalla = pygame.display.set_mode((ANCHO, ALTO))
    pygame.display.set_caption("Menú Principal - Escapa del Laberinto")

    reloj = pygame.time.Clock()

    # Fuentes
    fuente_titulo = pygame.font.Font(None, 60)
    fuente_botones = pygame.font.Font(None, 40)
    fuente_jugador = pygame.font.Font(None, 30)

    # Cargar imágenes
    fondo = cargar_imagen(os.path.join("imagenes", "fondo_piedra.png"))
    laberinto_img = cargar_imagen(os.path.join("imagenes", "imagen_laberinto.png"), usar_alpha=True)
    antorcha_sheet = cargar_imagen(os.path.join("imagenes", "antorcha.png"), usar_alpha=True)


    if fondo:
        fondo = pygame.transform.scale(fondo, (ANCHO, ALTO))

    if laberinto_img:
        # Escalamos el laberinto para que ocupe el centro
        ratio = min(400 / laberinto_img.get_width(), 400 / laberinto_img.get_height())
        nuevo_tam = (int(laberinto_img.get_width() * ratio), int(laberinto_img.get_height() * ratio))
        laberinto_img = pygame.transform.smoothscale(laberinto_img, nuevo_tam)
        laberinto_img.set_alpha(80)  # transparencia suave

    antorcha_frames = []
    if antorcha_sheet:
        antorcha_frames = recortar_antorcha_sprites(antorcha_sheet, num_frames=7)
        # Escalamos cada frame al tamaño mediano
        frames_escalados = []
        altura_deseada = 160
        for fr in antorcha_frames:
            ratio = altura_deseada / fr.get_height()
            nuevo_tam = (int(fr.get_width() * ratio), altura_deseada)
            frames_escalados.append(pygame.transform.smoothscale(fr, nuevo_tam))
        antorcha_frames = frames_escalados

    # Índice para animación de antorcha
    indice_antorcha = 0
    tiempo_anim = 0
    intervalo_anim_ms = 120  # cambiar frame cada 120ms

    # Parámetros para halo de luz de antorcha (brillo intermedio)
    halo_surface = pygame.Surface((220, 220), pygame.SRCALPHA)
    halo_radio_base = 90
    halo_alpha_base = 60
    halo_tiempo = 0

    # Aqui se definen los botones del menú principal
    botones = [
        Boton("Crear jugadores", (ANCHO // 2, 160)),
        Boton("Modo Escapa",     (ANCHO // 2, 230)),
        Boton("Modo Cazador",    (ANCHO // 2, 300)),
        Boton("Puntajes",        (ANCHO // 2, 370)),
        Boton("Configuración",   (ANCHO // 2, 440)),
        Boton("Salir",           (ANCHO // 2, 510)),
    ]

    opcion_seleccionada = None

    corriendo = True
    while corriendo:
        dt = reloj.tick(FPS)
        tiempo_anim += dt
        halo_tiempo += dt

        mouse_pos = pygame.mouse.get_pos()
        mouse_down = False

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                mouse_down = True

            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    opcion_seleccionada = "Salir"
                    corriendo = False

        # Actualizar animación de antorchas
        if antorcha_frames:
            if tiempo_anim >= intervalo_anim_ms:
                tiempo_anim = 0
                indice_antorcha = (indice_antorcha + 1) % len(antorcha_frames)

        # Se encarga de dibujar el fondo
        if fondo:
            pantalla.blit(fondo, (0, 0))
        else:
            pantalla.fill((30, 20, 10))

        # Oscurecer un poquito para que todo se lea mejor
        oscurecedor = pygame.Surface((ANCHO, ALTO))
        oscurecedor.set_alpha(60)
        oscurecedor.fill((0, 0, 0))
        pantalla.blit(oscurecedor, (0, 0))

        # Dibujar laberinto central
        if laberinto_img:
            rect_lab = laberinto_img.get_rect(center=(ANCHO // 2, ALTO // 2 - 40))
            pantalla.blit(laberinto_img, rect_lab.topleft)

        # Se encarga de dibujar las antorchas y la luz que las rodea
        if antorcha_frames:
            frame = antorcha_frames[indice_antorcha]

            # Halo "respira" suavemente
            halo_surface.fill((0, 0, 0, 0))  # limpiar
            import math
            pulso = (math.sin(halo_tiempo / 600) + 1) / 2  # 0..1
            halo_radio = int(halo_radio_base + pulso * 10)
            halo_alpha = int(halo_alpha_base + pulso * 20)
            pygame.draw.circle(
                halo_surface,
                (255, 200, 80, halo_alpha),
                (halo_surface.get_width() // 2, halo_surface.get_height() // 2),
                halo_radio
            )

            # Antorcha izquierda
            x_izq = 40
            y_izq = 20
            rect_ant_izq = frame.get_rect(topleft=(x_izq, y_izq))

            halo_rect_izq = halo_surface.get_rect(center=rect_ant_izq.center)
            pantalla.blit(halo_surface, halo_rect_izq.topleft)
            pantalla.blit(frame, rect_ant_izq.topleft)

            # Antorcha derecha
            x_der = ANCHO - frame.get_width() - 40
            y_der = 20
            rect_ant_der = frame.get_rect(topleft=(x_der, y_der))

            halo_rect_der = halo_surface.get_rect(center=rect_ant_der.center)
            pantalla.blit(halo_surface, halo_rect_der.topleft)
            pantalla.blit(frame, rect_ant_der.topleft)

        #Titulo del juego
        titulo_surface = fuente_titulo.render("ESCAPA DEL LABERINTO", True, COLOR_TITULO)
        titulo_rect = titulo_surface.get_rect(center=(ANCHO // 2, 80))
        # sombra del título
        sombra_titulo = titulo_rect.copy()
        sombra_titulo.x += 3
        sombra_titulo.y += 3
        pantalla.blit(fuente_titulo.render("ESCAPA DEL LABERINTO", True, (0, 0, 0)), sombra_titulo)
        pantalla.blit(titulo_surface, titulo_rect)

        # Nombre del jugador arriba a la derecha
        texto_jugador = fuente_jugador.render(f"Jugador: {nombre_jugador}", True, (230, 230, 220))
        rect_jugador = texto_jugador.get_rect(bottomright=(ANCHO - 20, ALTO - 20))
        pantalla.blit(texto_jugador, rect_jugador)

        # Botones del menu

        mouse_click_en_este_frame = mouse_down 
        # Se encarga de leer el click de los botones, esta linea de codigo se encarga de capturar dicho click
        for boton in botones:
            boton.draw(pantalla, fuente_botones, mouse_pos)
            if boton.fue_click(mouse_pos, mouse_click_en_este_frame):
                opcion_seleccionada = boton.texto
                corriendo = False
                break

        pygame.display.flip()

    return opcion_seleccionada


# Prueba directa del menú
from crear_jugadores import crear_jugadores
from selector_jugador import selector_jugador
from modo_escapa import modo_escapa
from modo_cazador import modo_cazador
from ventana_puntajes import mostrar_puntajes
from puntajes import GestorPuntajes
from ventana_controles import ventana_controles


if __name__ == "__main__":
    while True:
        seleccion = menu_principal("JugadorPrueba")

        if seleccion == "Crear jugadores":
            crear_jugadores()

        elif seleccion == "Modo Escapa":
            jugador = selector_jugador("Escapa")
            print("Jugador seleccionado para ESCAPA:", jugador)
            if jugador:                       
                modo_escapa(jugador)
            else:
                # Si no selecciona jugador, usar uno por defecto
                modo_escapa("Jugador")          

        elif seleccion == "Modo Cazador":
            jugador = selector_jugador("Cazador")
            if jugador:
                modo_cazador(jugador)
            else:
                # Si no selecciona jugador, usar uno por defecto
                modo_cazador("Jugador")

        elif seleccion == "Puntajes":
            print("Mostrar puntajes")
            mostrar_puntajes()

        elif seleccion == "Configuración":
            print("Abrir configuración")
            ventana_controles()

        elif seleccion == "Salir":
            pygame.quit()
            sys.exit()

