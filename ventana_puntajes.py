import pygame
import sys
from puntajes import GestorPuntajes

# Configuración de la ventana
ANCHO = 800
ALTO = 600
COLOR_FONDO = (30, 30, 50)
COLOR_TITULO = (255, 215, 0)
COLOR_TEXTO = (255, 255, 255)
COLOR_BORDE = (100, 100, 150)
COLOR_CAZADOR = (70, 130, 180)  # Azul acero
COLOR_ESCAPA = (50, 168, 82)    # Verde

def mostrar_puntajes():
    """Función simplificada para mostrar puntajes - dividida en dos mitades"""
    # Crear nueva ventana para los puntajes
    pantalla = pygame.display.set_mode((ANCHO, ALTO))
    pygame.display.set_caption("Top Puntajes - Escapa del Laberinto")
    
    # Fuentes
    fuente_titulo = pygame.font.Font(None, 48)
    fuente_subtitulo = pygame.font.Font(None, 36)
    fuente_texto = pygame.font.Font(None, 32)
    fuente_pequena = pygame.font.Font(None, 28)
    
    # Cargar gestor de puntajes
    gestor = GestorPuntajes()
    
    corriendo = True
    
    while corriendo:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    corriendo = False
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                # También permitir clic en cualquier parte para salir
                corriendo = False
        
        # Dibujar fondo
        pantalla.fill(COLOR_FONDO)
        
        # Título principal
        titulo = fuente_titulo.render("MEJORES PUNTAJES", True, COLOR_TITULO)
        pantalla.blit(titulo, (ANCHO//2 - titulo.get_width()//2, 30))
        
        # Línea divisoria central gruesa
        pygame.draw.line(pantalla, COLOR_BORDE, (ANCHO//2, 100), (ANCHO//2, ALTO-100), 3)
        
        # Obtener tops de puntajes
        top_cazador = gestor.obtener_top("cazador")
        top_escapa = gestor.obtener_top("escapa")
        
        # ===== MITAD IZQUIERDA - MODO CAZADOR =====
        titulo_cazador = fuente_subtitulo.render("MODO CAZADOR", True, COLOR_CAZADOR)
        pantalla.blit(titulo_cazador, (ANCHO//4 - titulo_cazador.get_width()//2, 100))
        
        # Marco del modo cazador
        pygame.draw.rect(pantalla, COLOR_CAZADOR, (50, 140, ANCHO//2 - 70, 400), 2, border_radius=10)
        
        if not top_cazador:
            # Si no hay puntajes en modo cazador
            texto_vacio = fuente_pequena.render("No hay puntajes aún", True, (150, 150, 150))
            pantalla.blit(texto_vacio, (ANCHO//4 - texto_vacio.get_width()//2, 300))
        else:
            # Dibujar cada puntaje del modo cazador
            for i, puntaje in enumerate(top_cazador):
                y_pos = 160 + i * 70
                
                # Fondo del puesto
                pygame.draw.rect(pantalla, (30, 60, 90), 
                               (70, y_pos, ANCHO//2 - 110, 50), border_radius=8)
                
                # Número de puesto (1., 2., 3., etc.)
                texto_puesto = fuente_texto.render(f"{i+1}.", True, COLOR_TEXTO)
                pantalla.blit(texto_puesto, (90, y_pos + 10))
                
                # Nombre del jugador
                nombre = puntaje["nombre"][:15]  # Limitar longitud del nombre
                texto_nombre = fuente_texto.render(nombre, True, COLOR_TEXTO)
                pantalla.blit(texto_nombre, (130, y_pos + 10))
                
                # Puntaje
                texto_puntaje = fuente_texto.render(str(puntaje["puntaje"]), True, COLOR_TITULO)
                pantalla.blit(texto_puntaje, (ANCHO//2 - 100, y_pos + 10))
        
        # ===== MITAD DERECHA - MODO ESCAPA =====
        titulo_escapa = fuente_subtitulo.render("MODO ESCAPA", True, COLOR_ESCAPA)
        pantalla.blit(titulo_escapa, (3*ANCHO//4 - titulo_escapa.get_width()//2, 100))
        
        # Marco del modo escapa
        pygame.draw.rect(pantalla, COLOR_ESCAPA, (ANCHO//2 + 20, 140, ANCHO//2 - 70, 400), 2, border_radius=10)
        
        if not top_escapa:
            # Si no hay puntajes en modo escapa
            texto_vacio = fuente_pequena.render("No hay puntajes aún", True, (150, 150, 150))
            pantalla.blit(texto_vacio, (3*ANCHO//4 - texto_vacio.get_width()//2, 300))
        else:
            # Dibujar cada puntaje del modo escapa
            for i, puntaje in enumerate(top_escapa):
                y_pos = 160 + i * 70
                
                # Fondo del puesto
                pygame.draw.rect(pantalla, (30, 90, 50), 
                               (ANCHO//2 + 40, y_pos, ANCHO//2 - 110, 50), border_radius=8)
                
                # Número de puesto
                texto_puesto = fuente_texto.render(f"{i+1}.", True, COLOR_TEXTO)
                pantalla.blit(texto_puesto, (ANCHO//2 + 60, y_pos + 10))
                
                # Nombre del jugador
                nombre = puntaje["nombre"][:15]  # Limitar longitud del nombre
                texto_nombre = fuente_texto.render(nombre, True, COLOR_TEXTO)
                pantalla.blit(texto_nombre, (ANCHO//2 + 100, y_pos + 10))
                
                # Puntaje
                texto_puntaje = fuente_texto.render(str(puntaje["puntaje"]), True, COLOR_TITULO)
                pantalla.blit(texto_puntaje, (ANCHO - 100, y_pos + 10))
        
        # Instrucciones para volver
        instrucciones = fuente_pequena.render("Presiona ESC o haz clic para volver al menú", True, (200, 200, 200))
        pantalla.blit(instrucciones, (ANCHO//2 - instrucciones.get_width()//2, ALTO - 50))
        
        pygame.display.flip()
    
    # Restaurar la ventana principal al salir
    pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Menú Principal - Escapa del Laberinto")
    return True