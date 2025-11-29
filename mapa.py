import random
from collections import deque

# Creacion de clases del terreno del mapa

class Casilla: # Clase base para todos los tipos de casillas del mapa
    def __init__(self):
        self.transitable_jugador = True
        self.transitable_enemigo = True
        self.color = (255, 255, 255)

class Camino(Casilla):# Casilla por la que se pueden mover todos los juadores
    def __init__(self):
        super().__init__()
        self.color = (200, 200, 200)

class Muro(Casilla):# Casilla por la que se no se puede mover ningun jugador
    def __init__(self):
        super().__init__()
        self.transitable_jugador = False
        self.transitable_enemigo = False
        self.color = (30, 30, 30)

class Liana(Casilla): # Casilla por la que solo los enemigos/cazadores se puede mover
    def __init__(self):
        super().__init__()
        self.transitable_jugador = False
        self.transitable_enemigo = True
        self.color = (0, 160, 0)

class Tunel(Casilla): # Casilla por la que solo se puede mover un jugador normal
    def __init__(self):
        super().__init__()
        self.transitable_jugador = True
        self.transitable_enemigo = False
        self.color = (0, 0, 170)



# Clase encargada de generar el mapa
class GeneradorMapa:

    def __init__(self, filas, columnas): # Inicializa el generador de mapas
        self.filas = filas
        self.columnas = columnas
        self.salidas = []

    def generar_mapa(self):
        """
        Genera un mapa aleatorio, con varias salida, minimo una se puede utilizar y 
        que el mapa sea siempre diferente cada vez que se reinicie el juego.
        """
        intentos = 0
        min_distancia = int((self.filas + self.columnas) * 0.4)  # distancia mínima recomendada

        while True:
            intentos += 1

            matriz = [[self._casilla_aleatoria() for _ in range(self.columnas)]
                      for _ in range(self.filas)]

            # Spawn del jugador 
            inicio = (0, 0)
            matriz[0][0] = Camino()

            # genera las salidas en los bordes para mayor dificultad
            self.salidas = []
            cantidad_salidas = random.randint(1, 5)

            bordes = []

            # borde superior
            bordes += [(0, c) for c in range(self.columnas)]
            # borde inferior
            bordes += [(self.filas - 1, c) for c in range(self.columnas)]
            # borde izquierdo
            bordes += [(f, 0) for f in range(self.filas)]
            # borde derecho
            bordes += [(f, self.columnas - 1) for f in range(self.filas)]

            random.shuffle(bordes)

            for pos in bordes:
                if len(self.salidas) >= cantidad_salidas:
                    break

                f, c = pos

                # Distancia relacionada al spawn
                dist = abs(f - 0) + abs(c - 0)

                if dist >= min_distancia:
                    matriz[f][c] = Camino()
                    self.salidas.append((f, c))

            # Se regenera el mapa en caso de no tener sufientes salidas
            if len(self.salidas) == 0:
                continue

            # valida si almenos una salida es alcanzable por el jugador que escapa
            if self._hay_camino_a_alguna_salida(matriz, inicio, self.salidas):
                print(f"Mapa generado en {intentos} intentos ({len(self.salidas)} salidas).")
                return matriz

    def _casilla_aleatoria(self):
        """Se encarga de hacer el mapa más difícil."""
        # configura las probabiliddes
        opciones = [
            (Camino, 0.55),   # bajamos caminos
            (Muro,   0.20),   # aumentamos muros
            (Liana,  0.15),
            (Tunel,  0.10)
        ]

        r = random.random()
        acum = 0
        for clase, prob in opciones:
            acum += prob
            if r <= acum:
                return clase()
        return Camino()

    def _hay_camino_a_alguna_salida(self, matriz, inicio, salidas):
        """
        Utiliza el BFS para verificar si existe el camino desde el spawn hasta alguna salida
        """
        f0, c0 = inicio
        visitado = set()
        q = deque([(f0, c0)])
        visitado.add((f0, c0))

        while q:
            f, c = q.popleft()

            # Verifica si llegamos a alguna salida
            if (f, c) in salidas:
                return True  # se alcanzó una salida válida

            for df, dc in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                nf, nc = f + df, c + dc

                # Verifica límites del mapa
                if 0 <= nf < self.filas and 0 <= nc < self.columnas:
                    if (nf, nc) not in visitado:
                        # CORRECCIÓN: Usar transitable_jugador en lugar de verificar solo Muros
                        if matriz[nf][nc].transitable_jugador:  # ¡ESTA ES LA CORRECCIÓN CLAVE!
                            visitado.add((nf, nc))
                            q.append((nf, nc))

        return False # No se encontró camino a ninguna salida