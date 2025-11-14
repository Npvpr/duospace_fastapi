from typing import Dict, List
from fastapi import WebSocket, APIRouter, WebSocketDisconnect

from app.utils.connection_manager import ConnectionManager

router = APIRouter()

manager = ConnectionManager()


@router.websocket("/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    print(websocket)
    await manager.connect(user_id, websocket)
    try:
        while True:
            # Receive JSON with room_id and message
            data = await websocket.receive_json()
            room_id = data["room_id"]
            message = data["message"]

            # Send message to all users in the room
            await manager.send_message_to_room(room_id, user_id, message)

    except WebSocketDisconnect:
        manager.disconnect(user_id)
