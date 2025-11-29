import json
import os

class GestorPuntajes:
    def __init__(self, archivo="puntajes.json"):
        self.archivo = archivo
        self.puntajes = {"cazador": [], "escapa": []}
        self.cargar_puntajes()
    
    def cargar_puntajes(self):
        """Carga los puntajes desde el archivo JSON"""
        try:
            if os.path.exists(self.archivo):
                with open(self.archivo, 'r', encoding='utf-8') as f:
                    self.puntajes = json.load(f)
                print(f"Puntajes cargados desde {self.archivo}")
            else:
                # Si el archivo no existe, crearlo
                self.guardar_puntajes()
                print(f"Archivo {self.archivo} creado")
        except Exception as e:
            print(f"Error cargando puntajes: {e}")
            # Crear archivo nuevo si hay error
            self.guardar_puntajes()
    
    def guardar_puntajes(self):
        """Guarda los puntajes en el archivo JSON"""
        try:
            with open(self.archivo, 'w', encoding='utf-8') as f:
                json.dump(self.puntajes, f, indent=2, ensure_ascii=False)
            print(f"Puntajes guardados en {self.archivo}")
        except Exception as e:
            print(f"Error guardando puntajes: {e}")
    
    def agregar_puntaje(self, modo, nombre, puntaje):
        """Agrega un nuevo puntaje y mantiene solo el top 5"""
        # Validar que el nombre no sea None
        if nombre is None:
            nombre = "Jugador"
            
        if modo not in self.puntajes:
            print(f"Modo inválido: {modo}")
            return
        
        print(f"Agregando puntaje - Modo: {modo}, Jugador: {nombre}, Puntos: {puntaje}")
        
        # Agregar nuevo puntaje
        self.puntajes[modo].append({"nombre": nombre, "puntaje": puntaje})
        
        # Ordenar por puntaje (mayor a menor) y mantener solo top 5
        self.puntajes[modo].sort(key=lambda x: x["puntaje"], reverse=True)
        self.puntajes[modo] = self.puntajes[modo][:5]
        
        print(f"Top actualizado para {modo}: {self.puntajes[modo]}")
        
        # Guardar cambios
        self.guardar_puntajes()
    
    def obtener_top(self, modo):
        """Obtiene el top 5 de un modo específico"""
        return self.puntajes.get(modo, [])