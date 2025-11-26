import json
import os

ARCHIVO = "jugadores.json" # Nombre del archivo donde se van a guardar el nombre de los jugadores 

def cargar_registro(): # Se encarga de cargar los datos de los jugadores desde el archivo.json
    
    if not os.path.exists(ARCHIVO): # Verifica si el archivo existe para evitar errores
        return {"jugadores": [], "puntajes": {}}
    #En caso de que el archivo no exista o aun no haya sido creado retorna una estructura vacía
    with open(ARCHIVO, "r") as f:
        return json.load(f)

def guardar_registro(data):
    #Guarda los datos de jugadores en el archivo JSON.
    with open(ARCHIVO, "w") as f:
        json.dump(data, f, indent=4) ## Convierte el diccionario a JSON

def registrar_jugador(nombre): # Registra un nuevo jugador en el sistema.

    data = cargar_registro() # Carga los datos actuales del archivo

    if nombre not in data["jugadores"]: # Verifica si el jugador ya está registrado
        data["jugadores"].append(nombre) # Agrega el jugador a la lista de jugadores
        data["puntajes"][nombre] = {"Escapa": 0, "Cazador": 0} # Inicializa los puntajes para ambos roles del juego

    guardar_registro(data) # Guarda los cambios en el archivo
