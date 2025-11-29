import pygame
from avatar import Avatar

pygame.init()
pantalla = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

# Cambiar tipo a "cazador" para probar el otro avatar
player = Avatar(400, 300, tipo="escapa")

running = True
while running:
    for evt in pygame.event.get():
        if evt.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    player.mover(keys)

    pantalla.fill((30, 30, 30))
    player.draw(pantalla)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
