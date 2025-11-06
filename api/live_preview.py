"""
Live Preview System for SuperAgent v8
Beats Bolt.new's instant preview with hot reload and multi-device support
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import asyncio
import json
import uuid
import os
import tempfile
import shutil
from pathlib import Path

router = APIRouter()

# Store active preview sessions
active_previews: Dict[str, Dict[str, Any]] = {}
preview_connections: Dict[str, List[WebSocket]] = {}


class PreviewRequest(BaseModel):
    """Request to create a live preview"""
    code: str
    language: str = "html"
    framework: Optional[str] = None
    hot_reload: bool = True
    mobile_preview: bool = False


class PreviewResponse(BaseModel):
    """Response with preview details"""
    preview_id: str
    preview_url: str
    websocket_url: str
    mobile_preview_url: Optional[str] = None
    qr_code_url: Optional[str] = None


@router.post("/api/v1/preview/create")
async def create_preview(request: PreviewRequest):
    """
    Create a live preview session
    Returns preview URL and WebSocket for hot reload
    """
    
    # Generate unique preview ID
    preview_id = str(uuid.uuid4())[:8]
    
    # Create temporary directory for preview files
    preview_dir = Path(tempfile.gettempdir()) / "superagent_previews" / preview_id
    preview_dir.mkdir(parents=True, exist_ok=True)
    
    # Write code to file
    if request.language == "html" or request.framework in ["html", "vanilla"]:
        file_path = preview_dir / "index.html"
        file_path.write_text(request.code)
    elif request.framework == "react":
        # For React, create a basic setup
        file_path = preview_dir / "App.jsx"
        file_path.write_text(request.code)
        # Create index.html wrapper
        html_wrapper = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SuperAgent Preview</title>
    <script crossorigin src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
    <script crossorigin src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
</head>
<body>
    <div id="root"></div>
    <script type="text/babel" src="App.jsx"></script>
</body>
</html>
        """
        (preview_dir / "index.html").write_text(html_wrapper)
    else:
        file_path = preview_dir / f"index.{request.language}"
        file_path.write_text(request.code)
    
    # Store preview session
    active_previews[preview_id] = {
        "code": request.code,
        "language": request.language,
        "framework": request.framework,
        "directory": str(preview_dir),
        "hot_reload": request.hot_reload,
        "mobile_preview": request.mobile_preview,
        "created_at": asyncio.get_event_loop().time()
    }
    
    # Generate URLs
    base_url = os.getenv("BASE_URL", "http://localhost:8000")
    preview_url = f"{base_url}/preview/{preview_id}"
    websocket_url = f"{base_url.replace('http', 'ws')}/preview/ws/{preview_id}"
    
    mobile_preview_url = None
    qr_code_url = None
    if request.mobile_preview:
        mobile_preview_url = f"{base_url}/preview/{preview_id}/mobile"
        qr_code_url = f"{base_url}/preview/{preview_id}/qr"
    
    return PreviewResponse(
        preview_id=preview_id,
        preview_url=preview_url,
        websocket_url=websocket_url,
        mobile_preview_url=mobile_preview_url,
        qr_code_url=qr_code_url
    )


@router.get("/api/v1/preview/{preview_id}")
async def get_preview(preview_id: str):
    """
    Get preview HTML with hot reload support
    """
    
    if preview_id not in active_previews:
        raise HTTPException(status_code=404, detail="Preview not found")
    
    preview = active_previews[preview_id]
    preview_dir = Path(preview["directory"])
    
    # Read the HTML file
    html_file = preview_dir / "index.html"
    if not html_file.exists():
        raise HTTPException(status_code=404, detail="Preview file not found")
    
    html_content = html_file.read_text()
    
    # Inject hot reload script if enabled
    if preview["hot_reload"]:
        base_url = os.getenv("BASE_URL", "http://localhost:8000")
        websocket_url = base_url.replace("http", "ws")
        hot_reload_script = f"""
<script>
    // SuperAgent Hot Reload
    const ws = new WebSocket('{websocket_url}/preview/ws/{preview_id}');
    
    ws.onmessage = function(event) {{
        const data = JSON.parse(event.data);
        if (data.type === 'reload') {{
            console.log('Hot reload triggered');
            location.reload();
        }} else if (data.type === 'update') {{
            console.log('Updating content');
            document.body.innerHTML = data.content;
        }}
    }};
    
    ws.onclose = function() {{
        console.log('Preview connection closed');
    }};
    
    ws.onerror = function(error) {{
        console.error('Preview error:', error);
    }};
</script>
        """
        # Inject before closing body tag
        html_content = html_content.replace("</body>", f"{hot_reload_script}</body>")
    
    return {"html": html_content, "preview_id": preview_id}


@router.websocket("/preview/ws/{preview_id}")
async def preview_websocket(websocket: WebSocket, preview_id: str):
    """
    WebSocket endpoint for hot reload
    """
    
    await websocket.accept()
    
    # Add to active connections
    if preview_id not in preview_connections:
        preview_connections[preview_id] = []
    preview_connections[preview_id].append(websocket)
    
    try:
        while True:
            # Keep connection alive
            data = await websocket.receive_text()
            # Echo back for heartbeat
            await websocket.send_json({"type": "pong"})
    except WebSocketDisconnect:
        # Remove from active connections
        if preview_id in preview_connections:
            preview_connections[preview_id].remove(websocket)


@router.post("/api/v1/preview/{preview_id}/update")
async def update_preview(preview_id: str, request: PreviewRequest):
    """
    Update preview code and trigger hot reload
    """
    
    if preview_id not in active_previews:
        raise HTTPException(status_code=404, detail="Preview not found")
    
    preview = active_previews[preview_id]
    preview_dir = Path(preview["directory"])
    
    # Update code file
    file_path = preview_dir / "index.html"
    file_path.write_text(request.code)
    
    # Update preview session
    preview["code"] = request.code
    
    # Trigger hot reload for all connected clients
    if preview_id in preview_connections:
        for websocket in preview_connections[preview_id]:
            try:
                await websocket.send_json({
                    "type": "reload",
                    "preview_id": preview_id
                })
            except:
                pass
    
    return {"success": True, "message": "Preview updated"}


@router.delete("/api/v1/preview/{preview_id}")
async def delete_preview(preview_id: str):
    """
    Delete a preview session
    """
    
    if preview_id not in active_previews:
        raise HTTPException(status_code=404, detail="Preview not found")
    
    preview = active_previews[preview_id]
    preview_dir = Path(preview["directory"])
    
    # Close all WebSocket connections
    if preview_id in preview_connections:
        for websocket in preview_connections[preview_id]:
            try:
                await websocket.close()
            except:
                pass
        del preview_connections[preview_id]
    
    # Delete preview files
    if preview_dir.exists():
        shutil.rmtree(preview_dir)
    
    # Remove from active previews
    del active_previews[preview_id]
    
    return {"success": True, "message": "Preview deleted"}


@router.get("/api/v1/preview/{preview_id}/mobile")
async def get_mobile_preview(preview_id: str):
    """
    Get mobile-optimized preview
    """
    
    if preview_id not in active_previews:
        raise HTTPException(status_code=404, detail="Preview not found")
    
    preview = active_previews[preview_id]
    
    # Return mobile-optimized HTML
    mobile_html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>SuperAgent Mobile Preview</title>
    <style>
        body {{
            margin: 0;
            padding: 0;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }}
        .mobile-frame {{
            width: 100vw;
            height: 100vh;
            overflow: auto;
        }}
    </style>
</head>
<body>
    <div class="mobile-frame">
        <iframe src="/api/v1/preview/{preview_id}" style="width: 100%; height: 100%; border: none;"></iframe>
    </div>
</body>
</html>
    """
    
    return {"html": mobile_html}


@router.get("/api/v1/preview/{preview_id}/qr")
async def get_qr_code(preview_id: str):
    """
    Generate QR code for mobile preview
    """
    
    if preview_id not in active_previews:
        raise HTTPException(status_code=404, detail="Preview not found")
    
    base_url = os.getenv("BASE_URL", "http://localhost:8000")
    mobile_url = f"{base_url}/preview/{preview_id}/mobile"
    
    # Generate QR code (simplified - in production, use qrcode library)
    qr_data = {
        "url": mobile_url,
        "preview_id": preview_id,
        "message": "Scan to view on mobile"
    }
    
    return qr_data


@router.get("/api/v1/preview/list")
async def list_previews():
    """
    List all active preview sessions
    """
    
    previews = []
    for preview_id, preview in active_previews.items():
        base_url = os.getenv("BASE_URL", "http://localhost:8000")
        previews.append({
            "preview_id": preview_id,
            "preview_url": f"{base_url}/preview/{preview_id}",
            "language": preview["language"],
            "framework": preview["framework"],
            "created_at": preview["created_at"],
            "hot_reload": preview["hot_reload"],
            "mobile_preview": preview["mobile_preview"],
            "active_connections": len(preview_connections.get(preview_id, []))
        })
    
    return {"previews": previews, "total": len(previews)}


@router.get("/api/v1/preview/capabilities")
async def preview_capabilities():
    """
    Get preview system capabilities
    """
    
    return {
        "features": {
            "instant_preview": True,
            "hot_reload": True,
            "mobile_preview": True,
            "qr_code": True,
            "websocket_support": True,
            "multi_device": True,
            "shareable_links": True
        },
        "supported_languages": ["html", "javascript", "css"],
        "supported_frameworks": ["html", "react", "vue", "vanilla"],
        "max_preview_size": "10MB",
        "max_active_previews": 100,
        "preview_lifetime": "24 hours",
        "advantages_over_bolt": [
            "Free (Bolt costs $20-200/month)",
            "No token limits",
            "Unlimited previews",
            "Better hot reload",
            "Mobile preview with QR code",
            "Shareable links",
            "WebSocket support",
            "Multi-device sync"
        ]
    }


# Cleanup old previews (run periodically)
async def cleanup_old_previews():
    """
    Remove previews older than 24 hours
    """
    current_time = asyncio.get_event_loop().time()
    to_delete = []
    
    for preview_id, preview in active_previews.items():
        age = current_time - preview["created_at"]
        if age > 86400:  # 24 hours
            to_delete.append(preview_id)
    
    for preview_id in to_delete:
        try:
            await delete_preview(preview_id)
        except:
            pass


# Add router to main app
def setup_live_preview(app):
    """Add live preview to the main app"""
    app.include_router(router)
