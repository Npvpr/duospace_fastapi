from fastapi import WebSocket, WebSocketDisconnect
import json
from app.utils.connection_manager import ConnectionManager
from app.services.chat_service import chat_service
from app.models.chat import ChatMessage

manager = ConnectionManager()

async def handle_websocket_connection(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Wait for message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Validate and create message
            if "text" in message_data and message_data["text"].strip():
                message = ChatMessage.create(
                    text=message_data["text"].strip(),
                    sender=message_data.get("sender", "Anonymous")
                )
                
                # Store in history
                chat_service.add_message(message)
                
                # Broadcast to all clients
                await manager.broadcast(message.json())
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        # Notify others that user left (optional)
        # leave_message = ChatMessage.create(
        #     text="A user left the chat",
        #     sender="System"
        # )
        # await manager.broadcast(leave_message.json())
    except json.JSONDecodeError:
        await websocket.send_text(json.dumps({"error": "Invalid JSON format"}))
    except Exception as e:
        await websocket.send_text(json.dumps({"error": str(e)}))