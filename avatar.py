import pygame
import os

class Avatar:
    def __init__(self, x, y, tipo="escapa"):
        """
       carga un avatar distinto segun el tipo de modo de juego que se haya seleccionado
       ya sea cazador o escapa
        """

        self.x = x
        self.y = y

        # Velocidades
        self.vel_base = 3.0
        self.vel_sprint = 5.5

        # Stamina
        self.stamina_max = 100
        self.stamina = 100
        self.gasto_sprint = 0.9
        self.recuperacion = 0.5

        # Cargar sprite
        carpeta = "imagenes"
        if tipo == "escapa":
            ruta = os.path.join("imagenes", "imagen_de_escapista.png")
        else:
            ruta = os.path.join("imagenes", "Imagen_cazador.png")

        self.sprite = pygame.image.load(ruta).convert_alpha()
        self.sprite = pygame.transform.scale(self.sprite, (48, 48))

        self.rect = self.sprite.get_rect(center=(self.x, self.y))

    # Configuración del moviemiento del avatar de los modos
    def mover(self, keys):
        velocidad = self.vel_base

        # Sprint
        if keys[pygame.K_f] and self.stamina > 0:
            velocidad = self.vel_sprint
            self.stamina -= self.gasto_sprint
        else:
            self.stamina += self.recuperacion

        # Limitar stamina
        self.stamina = max(0, min(self.stamina, self.stamina_max))

        # Movimiento W-A-S-D
        if keys[pygame.K_w]:
            self.y -= velocidad
        if keys[pygame.K_s]:
            self.y += velocidad
        if keys[pygame.K_a]:
            self.x -= velocidad
        if keys[pygame.K_d]:
            self.x += velocidad

        self.rect.center = (self.x, self.y)

    # se encarga de dibujar en este caso la stamina
    def draw(self, pantalla):
        pantalla.blit(self.sprite, self.rect)

        # Dibujar barra de stamina
        barra_ancho = 120
        barra_alto  = 12
        x = 20
        y = 20

        # Fondo negro de la barra
        pygame.draw.rect(pantalla, (0, 0, 0), (x-2, y-2, barra_ancho+4, barra_alto+4))

        #porcenrtaje que se uso de stamina utilizado para aumentar o disminuir el tamaño de la bara
        porcentaje = self.stamina / self.stamina_max

        # Barra amarilla de stamina
        pygame.draw.rect(pantalla, (255, 255, 0), (x, y, barra_ancho * porcentaje, barra_alto))

