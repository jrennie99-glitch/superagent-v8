"""
WebSocket API - Real-Time Chat
Built by SuperAgent - Production-Ready WebSocket API
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from typing import List, Dict
from datetime import datetime
import json
import uvicorn

# Connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.rooms: Dict[str, List[str]] = {}  # room_id -> list of usernames
        self.message_history: Dict[str, List[Dict]] = {}  # room_id -> messages
    
    async def connect(self, websocket: WebSocket, username: str, room: str):
        await websocket.accept()
        self.active_connections[username] = websocket
        
        if room not in self.rooms:
            self.rooms[room] = []
            self.message_history[room] = []
        
        if username not in self.rooms[room]:
            self.rooms[room].append(username)
        
        # Send message history to new user
        await websocket.send_json({
            "type": "history",
            "messages": self.message_history[room]
        })
        
        # Notify room about new user
        await self.broadcast_to_room(room, {
            "type": "user_joined",
            "username": username,
            "timestamp": datetime.utcnow().isoformat(),
            "users_online": len(self.rooms[room])
        })
    
    def disconnect(self, username: str, room: str):
        if username in self.active_connections:
            del self.active_connections[username]
        
        if room in self.rooms and username in self.rooms[room]:
            self.rooms[room].remove(username)
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        await websocket.send_json(message)
    
    async def broadcast_to_room(self, room: str, message: dict):
        if room not in self.rooms:
            return
        
        # Save message to history (except system messages)
        if message.get("type") == "message":
            self.message_history[room].append(message)
            # Keep only last 100 messages
            if len(self.message_history[room]) > 100:
                self.message_history[room] = self.message_history[room][-100:]
        
        # Send to all users in room
        for username in self.rooms[room]:
            if username in self.active_connections:
                try:
                    await self.active_connections[username].send_json(message)
                except:
                    pass

manager = ConnectionManager()

# Create FastAPI app
app = FastAPI(
    title="WebSocket API - Real-Time Chat",
    description="Production-ready WebSocket API built by SuperAgent",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# HTML client for testing
html_client = """
<!DOCTYPE html>
<html>
<head>
    <title>WebSocket Chat - SuperAgent</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
            background: #f5f5f5;
        }
        .container {
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            margin-bottom: 10px;
        }
        .subtitle {
            color: #666;
            margin-bottom: 20px;
        }
        .login-form {
            margin-bottom: 20px;
        }
        input {
            padding: 10px;
            margin: 5px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 14px;
        }
        button {
            padding: 10px 20px;
            background: #007bff;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
        }
        button:hover {
            background: #0056b3;
        }
        #messages {
            height: 400px;
            overflow-y: auto;
            border: 1px solid #ddd;
            padding: 10px;
            margin-bottom: 10px;
            border-radius: 5px;
            background: #fafafa;
        }
        .message {
            padding: 8px;
            margin: 5px 0;
            border-radius: 5px;
            background: white;
        }
        .message.own {
            background: #e3f2fd;
            margin-left: 50px;
        }
        .message.system {
            background: #fff3cd;
            text-align: center;
            font-style: italic;
        }
        .message-header {
            font-weight: bold;
            color: #007bff;
            margin-bottom: 3px;
        }
        .message-time {
            font-size: 11px;
            color: #999;
        }
        .status {
            padding: 10px;
            margin: 10px 0;
            border-radius: 5px;
            background: #d4edda;
            color: #155724;
        }
        #chat-area {
            display: none;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 WebSocket Chat</h1>
        <p class="subtitle">Built by SuperAgent - Real-Time Communication</p>
        
        <div id="login-area" class="login-form">
            <input type="text" id="username" placeholder="Your name" />
            <input type="text" id="room" placeholder="Room name" value="general" />
            <button onclick="connect()">Join Chat</button>
        </div>
        
        <div id="chat-area">
            <div class="status" id="status">Connected</div>
            <div id="messages"></div>
            <div>
                <input type="text" id="messageInput" placeholder="Type a message..." style="width: 70%;" />
                <button onclick="sendMessage()">Send</button>
                <button onclick="disconnect()" style="background: #dc3545;">Leave</button>
            </div>
        </div>
    </div>

    <script>
        let ws = null;
        let currentUsername = null;
        let currentRoom = null;

        function connect() {
            const username = document.getElementById('username').value;
            const room = document.getElementById('room').value;
            
            if (!username || !room) {
                alert('Please enter both username and room name');
                return;
            }
            
            currentUsername = username;
            currentRoom = room;
            
            ws = new WebSocket(`ws://${window.location.host}/ws/${room}/${username}`);
            
            ws.onopen = function() {
                document.getElementById('login-area').style.display = 'none';
                document.getElementById('chat-area').style.display = 'block';
                document.getElementById('status').textContent = `Connected to room: ${room} as ${username}`;
            };
            
            ws.onmessage = function(event) {
                const data = JSON.parse(event.data);
                handleMessage(data);
            };
            
            ws.onclose = function() {
                document.getElementById('status').textContent = 'Disconnected';
                document.getElementById('status').style.background = '#f8d7da';
                document.getElementById('status').style.color = '#721c24';
            };
        }
        
        function handleMessage(data) {
            const messagesDiv = document.getElementById('messages');
            const messageDiv = document.createElement('div');
            
            if (data.type === 'history') {
                data.messages.forEach(msg => displayMessage(msg));
                return;
            }
            
            if (data.type === 'user_joined' || data.type === 'user_left') {
                messageDiv.className = 'message system';
                messageDiv.innerHTML = `${data.username} ${data.type === 'user_joined' ? 'joined' : 'left'} the room (${data.users_online} online)`;
            } else if (data.type === 'message') {
                displayMessage(data);
                return;
            }
            
            messagesDiv.appendChild(messageDiv);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }
        
        function displayMessage(data) {
            const messagesDiv = document.getElementById('messages');
            const messageDiv = document.createElement('div');
            const isOwn = data.username === currentUsername;
            
            messageDiv.className = `message ${isOwn ? 'own' : ''}`;
            messageDiv.innerHTML = `
                <div class="message-header">${data.username}</div>
                <div>${data.message}</div>
                <div class="message-time">${new Date(data.timestamp).toLocaleTimeString()}</div>
            `;
            
            messagesDiv.appendChild(messageDiv);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }
        
        function sendMessage() {
            const input = document.getElementById('messageInput');
            const message = input.value;
            
            if (!message) return;
            
            ws.send(JSON.stringify({
                type: 'message',
                message: message
            }));
            
            input.value = '';
        }
        
        function disconnect() {
            if (ws) {
                ws.close();
            }
            document.getElementById('login-area').style.display = 'block';
            document.getElementById('chat-area').style.display = 'none';
            document.getElementById('messages').innerHTML = '';
        }
        
        document.getElementById('messageInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
    </script>
</body>
</html>
"""

# Routes
@app.get("/")
async def root():
    return HTMLResponse(content=html_client)

@app.get("/api")
async def api_info():
    return {
        "message": "WebSocket API - Real-Time Chat",
        "version": "1.0.0",
        "built_by": "SuperAgent",
        "websocket_endpoint": "/ws/{room}/{username}",
        "test_client": "/",
        "features": {
            "rooms": "Multiple chat rooms",
            "real_time": "Instant message delivery",
            "history": "Message history for new users",
            "presence": "User join/leave notifications"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "active_connections": len(manager.active_connections),
        "active_rooms": len(manager.rooms),
        "rooms": {
            room: len(users) for room, users in manager.rooms.items()
        }
    }

@app.get("/rooms")
async def get_rooms():
    return {
        "rooms": [
            {
                "name": room,
                "users": len(users),
                "messages": len(manager.message_history.get(room, []))
            }
            for room, users in manager.rooms.items()
        ]
    }

# WebSocket endpoint
@app.websocket("/ws/{room}/{username}")
async def websocket_endpoint(websocket: WebSocket, room: str, username: str):
    await manager.connect(websocket, username, room)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Broadcast message to room
            await manager.broadcast_to_room(room, {
                "type": "message",
                "username": username,
                "message": message_data.get("message", ""),
                "timestamp": datetime.utcnow().isoformat()
            })
    
    except WebSocketDisconnect:
        manager.disconnect(username, room)
        await manager.broadcast_to_room(room, {
            "type": "user_left",
            "username": username,
            "timestamp": datetime.utcnow().isoformat(),
            "users_online": len(manager.rooms.get(room, []))
        })

if __name__ == "__main__":
    print("🚀 Starting WebSocket API - Real-Time Chat")
    print("💬 Chat Client: http://localhost:8003/")
    print("📡 WebSocket: ws://localhost:8003/ws/{room}/{username}")
    print("🏥 Health Check: http://localhost:8003/health")
    uvicorn.run(app, host="0.0.0.0", port=8003)
