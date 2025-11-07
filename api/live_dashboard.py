"""
SuperAgent v2.0 - Live Build Dashboard
Split-screen interface with real-time logs + live preview
Like Replit x Cursor x Bolt on steroids
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, List, Set
import asyncio
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v2/dashboard", tags=["live_dashboard"])

class LiveDashboardManager:
    """
    Manages live build dashboard connections and real-time updates
    
    Features:
    - Split-screen interface (logs + preview)
    - Real-time WebSocket updates
    - Hot-reload <1s
    - Build mode selector
    - Grok Co-Pilot integration
    """
    
    def __init__(self):
        # Active WebSocket connections
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        
        # Build sessions
        self.build_sessions: Dict[str, Dict] = {}
        
        logger.info("LiveDashboardManager initialized")
    
    async def connect(self, websocket: WebSocket, build_id: str):
        """Connect client to live dashboard"""
        await websocket.accept()
        
        if build_id not in self.active_connections:
            self.active_connections[build_id] = set()
        
        self.active_connections[build_id].add(websocket)
        logger.info(f"Client connected to build {build_id}")
        
        # Send initial state
        if build_id in self.build_sessions:
            await websocket.send_json({
                "type": "init",
                "build_id": build_id,
                "session": self.build_sessions[build_id]
            })
    
    def disconnect(self, websocket: WebSocket, build_id: str):
        """Disconnect client from live dashboard"""
        if build_id in self.active_connections:
            self.active_connections[build_id].discard(websocket)
            
            if not self.active_connections[build_id]:
                del self.active_connections[build_id]
        
        logger.info(f"Client disconnected from build {build_id}")
    
    async def broadcast_log(self, build_id: str, log_entry: Dict):
        """Broadcast log entry to all connected clients"""
        if build_id not in self.active_connections:
            return
        
        message = {
            "type": "log",
            "build_id": build_id,
            "timestamp": datetime.now().isoformat(),
            "entry": log_entry
        }
        
        # Send to all connected clients
        disconnected = set()
        for websocket in self.active_connections[build_id]:
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Error sending to websocket: {e}")
                disconnected.add(websocket)
        
        # Clean up disconnected clients
        for websocket in disconnected:
            self.disconnect(websocket, build_id)
    
    async def broadcast_preview_update(self, build_id: str, preview_url: str):
        """Broadcast preview URL update"""
        if build_id not in self.active_connections:
            return
        
        message = {
            "type": "preview_update",
            "build_id": build_id,
            "preview_url": preview_url,
            "timestamp": datetime.now().isoformat()
        }
        
        for websocket in self.active_connections[build_id]:
            try:
                await websocket.send_json(message)
            except:
                pass
    
    async def broadcast_grok_message(self, build_id: str, grok_message: Dict):
        """Broadcast Grok Co-Pilot message"""
        if build_id not in self.active_connections:
            return
        
        message = {
            "type": "grok",
            "build_id": build_id,
            "grok_message": grok_message,
            "timestamp": datetime.now().isoformat()
        }
        
        for websocket in self.active_connections[build_id]:
            try:
                await websocket.send_json(message)
            except:
                pass
    
    async def start_build_session(
        self,
        build_id: str,
        build_mode: str = "full_autonomous",
        app_type: str = "tiktok_clone"
    ):
        """Start a new build session"""
        self.build_sessions[build_id] = {
            "build_id": build_id,
            "build_mode": build_mode,
            "app_type": app_type,
            "status": "building",
            "progress": 0,
            "started_at": datetime.now().isoformat(),
            "logs": [],
            "preview_url": None,
            "grok_messages": []
        }
        
        logger.info(f"Started build session: {build_id}")
        
        # Send initial log
        await self.broadcast_log(build_id, {
            "level": "info",
            "message": f"🚀 Starting {build_mode} build for {app_type}...",
            "step": "init"
        })
    
    async def update_build_progress(self, build_id: str, progress: int, message: str):
        """Update build progress"""
        if build_id in self.build_sessions:
            self.build_sessions[build_id]["progress"] = progress
        
        await self.broadcast_log(build_id, {
            "level": "info",
            "message": message,
            "progress": progress
        })
    
    async def complete_build_session(self, build_id: str, app_url: str):
        """Complete build session"""
        if build_id in self.build_sessions:
            self.build_sessions[build_id]["status"] = "completed"
            self.build_sessions[build_id]["progress"] = 100
            self.build_sessions[build_id]["app_url"] = app_url
            self.build_sessions[build_id]["completed_at"] = datetime.now().isoformat()
        
        await self.broadcast_log(build_id, {
            "level": "success",
            "message": f"✅ Build complete! App deployed at {app_url}",
            "step": "complete"
        })
        
        await self.broadcast_preview_update(build_id, app_url)

# Global instance
dashboard_manager = LiveDashboardManager()

@router.websocket("/ws/{build_id}")
async def websocket_endpoint(websocket: WebSocket, build_id: str):
    """
    WebSocket endpoint for live dashboard
    
    Provides real-time updates:
    - Build logs
    - Preview updates
    - Grok messages
    - Progress updates
    """
    await dashboard_manager.connect(websocket, build_id)
    
    try:
        while True:
            # Keep connection alive and receive client messages
            data = await websocket.receive_text()
            
            # Handle client commands
            try:
                command = json.loads(data)
                
                if command.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})
                
                elif command.get("type") == "get_status":
                    if build_id in dashboard_manager.build_sessions:
                        await websocket.send_json({
                            "type": "status",
                            "session": dashboard_manager.build_sessions[build_id]
                        })
                
            except json.JSONDecodeError:
                pass
            
    except WebSocketDisconnect:
        dashboard_manager.disconnect(websocket, build_id)
    except Exception as e:
        logger.error(f"WebSocket error: {e}", exc_info=True)
        dashboard_manager.disconnect(websocket, build_id)

@router.post("/start/{build_id}")
async def start_dashboard_session(
    build_id: str,
    build_mode: str = "full_autonomous",
    app_type: str = "tiktok_clone"
):
    """
    Start a new live dashboard session
    
    Build modes:
    - full_autonomous: Complete build, zero input (2.5 min)
    - prototype_first: Interactive mockup (45 sec)
    - enterprise: Production-ready (5 min)
    """
    await dashboard_manager.start_build_session(build_id, build_mode, app_type)
    
    return {
        "success": True,
        "build_id": build_id,
        "build_mode": build_mode,
        "websocket_url": f"/api/v2/dashboard/ws/{build_id}",
        "message": "Dashboard session started. Connect via WebSocket for live updates."
    }

@router.get("/session/{build_id}")
async def get_dashboard_session(build_id: str):
    """Get current dashboard session state"""
    if build_id not in dashboard_manager.build_sessions:
        return {
            "success": False,
            "error": "Build session not found"
        }
    
    return {
        "success": True,
        "session": dashboard_manager.build_sessions[build_id]
    }

@router.get("/active")
async def get_active_sessions():
    """Get all active dashboard sessions"""
    return {
        "success": True,
        "active_sessions": len(dashboard_manager.build_sessions),
        "sessions": list(dashboard_manager.build_sessions.keys())
    }

# Export router and manager
live_dashboard_router = router
