from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List

router = APIRouter()

# Estructura para gestionar las salas
class PokerRoom:
    def __init__(self, room_id: str):
        self.room_id = room_id
        self.players: List[WebSocket] = []

    async def connect_player(self, websocket: WebSocket):
        await websocket.accept()
        self.players.append(websocket)

    def disconnect_player(self, websocket: WebSocket):
        self.players.remove(websocket)

    async def broadcast(self, message: str):
        for player in self.players:
            await player.send_text(message)

# Diccionario para almacenar las salas activas
active_rooms = {}

# Crear o unir a una sala
async def join_room(room_id: str, websocket: WebSocket):
    if room_id not in active_rooms:
        active_rooms[room_id] = PokerRoom(room_id)
    room = active_rooms[room_id]
    await room.connect_player(websocket)
    return room

# Endpoint para unirse a una sala de póker
@router.websocket("/ws/poker/{room_id}")
async def poker_room_endpoint(websocket: WebSocket, room_id: str):
    room = await join_room(room_id, websocket)
    
    try:
        while True:
            # Recibir mensajes del jugador
            data = await websocket.receive_text()
            print(data)
            await room.broadcast(f"Jugador en {room_id}: {data}")
    except WebSocketDisconnect:
        room.disconnect_player(websocket)
        # Si no quedan jugadores, eliminar la sala
        if len(room.players) == 0:
            del active_rooms[room_id]


@router.get("/info")
def get_info():
    return ({"Mensaje":"Esto es un juego de poker"})