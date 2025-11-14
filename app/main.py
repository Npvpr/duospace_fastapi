from typing import Annotated
from fastapi import (
    Cookie,
    Depends,
    FastAPI,
    Query,
    WebSocket,
    WebSocketException,
    status,
)
from app.api.main import api_router
from app.core.config import settings
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

# Create FastAPI app instance
app = FastAPI(
    title="Duospace Chat API",
    description="Backend API for Duospace chatting application",
    version="1.0.0",
)

# Set all CORS enabled origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

html1 = """
<!DOCTYPE html>
<html>
<head>
    <title>Chat</title>
</head>
<body>
    <h1>WebSocket Chat</h1>
    <form onsubmit="sendMessage(event)">
        <label>User ID: <input type="text" id="userId" autocomplete="off" value="user1"/></label>
        <button onclick="connect(event)">Connect</button>
        <hr>
        <label>Room ID: <input type="text" id="roomId" autocomplete="off" value="room1"/></label>
        <label>Message: <input type="text" id="messageText" autocomplete="off"/></label>
        <button>Send</button>
    </form>
    <ul id='messages'></ul>

    <script>
    var ws = null;

    function connect(event) {
        var userId = document.getElementById("userId").value;
        ws = new WebSocket("ws://localhost:8000/ws/" + userId);

        ws.onmessage = function(event) {
            var messages = document.getElementById('messages');
            var message = document.createElement('li');
            message.textContent = event.data;
            messages.appendChild(message);
        };

        ws.onopen = function() {
            console.log("Connected as " + userId);
        };

        ws.onclose = function() {
            console.log("Disconnected");
        };

        event.preventDefault();
    }

    function sendMessage(event) {
        if (!ws || ws.readyState !== WebSocket.OPEN) {
            alert("WebSocket not connected!");
            return;
        }

        var roomId = document.getElementById("roomId").value;
        var messageText = document.getElementById("messageText").value;

        ws.send(JSON.stringify({
            "room_id": roomId,
            "message": messageText
        }));

        document.getElementById("messageText").value = '';
        event.preventDefault();
    }
    </script>
</body>
</html>

"""


@app.get("/1")
async def get():
    return HTMLResponse(html1)


app.include_router(api_router)
