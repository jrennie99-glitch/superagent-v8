"""
Multiplayer Real-Time Collaboration System
WebSocket-based collaborative coding like Replit
"""
import asyncio
import json
import uuid
from typing import Dict, List, Set
from datetime import datetime, timedelta
from fastapi import WebSocket, WebSocketDisconnect
import secrets

class CollaborationRoom:
    """Manages a single collaboration session"""
    
    def __init__(self, room_id: str, owner_id: str):
        self.room_id = room_id
        self.owner_id = owner_id
        self.created_at = datetime.now()
        self.connections: Dict[str, WebSocket] = {}  # user_id -> websocket
        self.users: Dict[str, dict] = {}  # user_id -> user info
        self.shared_state: Dict = {
            "code": "",
            "files": {},
            "active_file": None
        }
        self.cursors: Dict[str, dict] = {}  # user_id -> cursor position
        self.join_link = secrets.token_urlsafe(16)
    
    async def add_user(self, user_id: str, username: str, websocket: WebSocket):
        """Add user to room"""
        self.connections[user_id] = websocket
        self.users[user_id] = {
            "id": user_id,
            "username": username,
            "joined_at": datetime.now().isoformat(),
            "is_owner": user_id == self.owner_id,
            "observing": None
        }
        
        # Notify all users about new user
        await self.broadcast({
            "type": "user_joined",
            "user": self.users[user_id],
            "total_users": len(self.users)
        }, exclude_user=user_id)
        
        # Send current state to new user
        await self.send_to_user(user_id, {
            "type": "init",
            "room_id": self.room_id,
            "users": list(self.users.values()),
            "shared_state": self.shared_state,
            "cursors": self.cursors
        })
    
    async def remove_user(self, user_id: str):
        """Remove user from room"""
        if user_id in self.connections:
            del self.connections[user_id]
        if user_id in self.users:
            del self.users[user_id]
        if user_id in self.cursors:
            del self.cursors[user_id]
        
        # Notify remaining users
        await self.broadcast({
            "type": "user_left",
            "user_id": user_id,
            "total_users": len(self.users)
        })
    
    async def update_code(self, user_id: str, code: str, file_path: str = None):
        """Update shared code state"""
        if file_path:
            self.shared_state["files"][file_path] = code
            self.shared_state["active_file"] = file_path
        else:
            self.shared_state["code"] = code
        
        # Broadcast to all except sender
        await self.broadcast({
            "type": "code_update",
            "user_id": user_id,
            "username": self.users[user_id]["username"],
            "code": code,
            "file_path": file_path,
            "timestamp": datetime.now().isoformat()
        }, exclude_user=user_id)
    
    async def update_cursor(self, user_id: str, line: int, column: int):
        """Update user's cursor position"""
        self.cursors[user_id] = {
            "user_id": user_id,
            "username": self.users[user_id]["username"],
            "line": line,
            "column": column
        }
        
        # Broadcast cursor position
        await self.broadcast({
            "type": "cursor_update",
            "cursor": self.cursors[user_id]
        }, exclude_user=user_id)
    
    async def set_observation_mode(self, observer_id: str, target_id: str):
        """Enable observation mode (watch another user)"""
        if observer_id in self.users:
            self.users[observer_id]["observing"] = target_id
            
            await self.broadcast({
                "type": "observation_changed",
                "observer_id": observer_id,
                "target_id": target_id
            })
    
    async def send_to_user(self, user_id: str, message: dict):
        """Send message to specific user"""
        if user_id in self.connections:
            try:
                await self.connections[user_id].send_json(message)
            except:
                await self.remove_user(user_id)
    
    async def broadcast(self, message: dict, exclude_user: str = None):
        """Broadcast message to all users in room"""
        for user_id in list(self.connections.keys()):
            if user_id != exclude_user:
                await self.send_to_user(user_id, message)
    
    def is_empty(self) -> bool:
        """Check if room has no users"""
        return len(self.connections) == 0


class MultiplayerManager:
    """Manages all collaboration rooms"""
    
    def __init__(self):
        self.rooms: Dict[str, CollaborationRoom] = {}
        self.user_to_room: Dict[str, str] = {}  # user_id -> room_id
        self.join_links: Dict[str, str] = {}  # join_link -> room_id
    
    def create_room(self, owner_id: str, owner_username: str) -> CollaborationRoom:
        """Create new collaboration room"""
        room_id = str(uuid.uuid4())
        room = CollaborationRoom(room_id, owner_id)
        self.rooms[room_id] = room
        self.join_links[room.join_link] = room_id
        return room
    
    def get_room(self, room_id: str) -> CollaborationRoom:
        """Get room by ID"""
        return self.rooms.get(room_id)
    
    def get_room_by_join_link(self, join_link: str) -> CollaborationRoom:
        """Get room by join link"""
        room_id = self.join_links.get(join_link)
        if room_id:
            return self.rooms.get(room_id)
        return None
    
    def get_user_room(self, user_id: str) -> CollaborationRoom:
        """Get room user is currently in"""
        room_id = self.user_to_room.get(user_id)
        if room_id:
            return self.rooms.get(room_id)
        return None
    
    async def join_room(self, room_id: str, user_id: str, username: str, websocket: WebSocket):
        """Join existing room"""
        room = self.get_room(room_id)
        if not room:
            return False
        
        # Limit to 4 users (like Replit)
        if len(room.users) >= 4:
            return False
        
        await room.add_user(user_id, username, websocket)
        self.user_to_room[user_id] = room_id
        return True
    
    async def leave_room(self, user_id: str):
        """Leave current room"""
        room = self.get_user_room(user_id)
        if room:
            await room.remove_user(user_id)
            
            # Clean up empty rooms
            if room.is_empty():
                del self.rooms[room.room_id]
                if room.join_link in self.join_links:
                    del self.join_links[room.join_link]
            
            if user_id in self.user_to_room:
                del self.user_to_room[user_id]
    
    def get_active_rooms(self) -> List[dict]:
        """Get list of active rooms (NO join links exposed for security)"""
        return [
            {
                "room_id": room.room_id,
                "user_count": len(room.users),
                "created_at": room.created_at.isoformat()
                # Join link intentionally omitted for security
            }
            for room in self.rooms.values()
        ]
    
    async def cleanup_stale_rooms(self):
        """Remove rooms older than 24 hours with no activity"""
        cutoff = datetime.now() - timedelta(hours=24)
        stale_rooms = [
            room_id for room_id, room in self.rooms.items()
            if room.created_at < cutoff and room.is_empty()
        ]
        
        for room_id in stale_rooms:
            room = self.rooms[room_id]
            if room.join_link in self.join_links:
                del self.join_links[room.join_link]
            del self.rooms[room_id]


# Global multiplayer manager instance
multiplayer_manager = MultiplayerManager()
