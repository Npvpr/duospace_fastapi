from typing import Dict, List
from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.rooms: Dict[str, List[str]] = {
            "room1": ["user1", "user2"],
            "room2": ["user2", "user3"],
        }

    async def connect(self, user_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
        else:
            raise ValueError("User not connected")

    async def send_message_to_room(self, room_id: str, sender_id: str, message: str):
        if room_id in self.rooms:
            for user_id in self.rooms[room_id]:
                if user_id in self.active_connections:
                    websocket = self.active_connections[user_id]
                    await websocket.send_text(message)
        else:
            raise ValueError("Room does not exist")
