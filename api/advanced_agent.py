"""
Advanced Agent API Endpoints
Exposes SuperAgent's enhanced capabilities
"""

from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os

from .tools_system import registry
from .ai_tool_integration import AIToolAgent, MultiModelRouter
from .context_manager import ContextManager, SmartContextRetrieval
from .codebase_intelligence import CodebaseAnalyzer
from .runway_integration import RunwayVideoGenerator
from .auto_app_builder import auto_app_builder

router = APIRouter()

# ==================== SECURITY GUARDS ====================

def is_admin_or_user(authorization: Optional[str] = Header(None)):
    """
    Check if request is from admin or authenticated user
    CRITICAL SECURITY: All dangerous operations must use this guard
    """
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authentication required. Please login or provide admin token."
        )
    
    token = authorization.replace("Bearer ", "")
    
    # Import user_manager here to avoid circular imports
    from .user_management import user_manager, admin_tokens
    
    # Check admin token
    if token in admin_tokens:
        return {"role": "admin", "username": "admin"}
    
    # Check user token
    user = user_manager.verify_user_token(token)
    if user:
        return {"role": "user", "username": user.get("username")}
    
    raise HTTPException(
        status_code=403,
        detail="Invalid authentication token"
    )

# Initialize global instances
ai_agent = None
model_router = None
context_manager = ContextManager()
smart_retrieval = SmartContextRetrieval(context_manager)
codebase_analyzer = CodebaseAnalyzer()

# Request/Response models
class UploadedFile(BaseModel):
    name: str
    content: str

class ChatRequest(BaseModel):
    message: str
    auto_execute_tools: bool = True
    model_type: str = "auto"  # auto, code, reasoning, writing, groq, fast
    uploaded_file: Optional[UploadedFile] = None

class ToolExecuteRequest(BaseModel):
    tool_name: str
    arguments: Dict[str, Any]

class CodeAnalysisRequest(BaseModel):
    file_path: str

class CodebaseScanRequest(BaseModel):
    extensions: List[str] = [".py"]


# ==================== AI AGENT ENDPOINTS ====================

@router.post("/agent/chat")
async def agent_chat(request: ChatRequest, auth=Depends(is_admin_or_user)):
    """
    Chat with AI agent that can use tools AND build apps automatically
    🚀 NEW: Auto-detects code and builds complete applications!
    """
    global ai_agent, model_router
    
    # Initialize if needed
    if not os.getenv('GEMINI_API_KEY'):
        raise HTTPException(status_code=400, detail="GEMINI_API_KEY not set")
    
    if not model_router:
        model_router = MultiModelRouter()
    
    try:
        # 🚀 NEW: Check if user wants to build an app
        uploaded_file_dict = None
        if request.uploaded_file:
            uploaded_file_dict = {
                "name": request.uploaded_file.name,
                "content": request.uploaded_file.content
            }
        
        should_build = auto_app_builder.should_build_app(request.message, uploaded_file_dict)
        
        # AUTO-BUILD MODE: Build complete app
        # 🔒 SECURITY: Only admins can auto-build apps (prevents remote code execution)
        if should_build:
            if auth["role"] != "admin":
                return {
                    "success": False,
                    "response": """🔒 **Auto-Build Disabled for Security**

For security reasons, autonomous app building is currently restricted to admin users only.

**Why?** Auto-building untrusted code could execute malicious commands on the server.

**What you can do:**
1. Ask me to help you build specific features step-by-step
2. I can generate code for you to review and run yourself
3. Contact an admin to enable auto-build for your account

**What would you like me to help you build?**""",
                    "model_used": "security_guard"
                }
            
            build_result = await auto_app_builder.build_app_from_chat(
                request.message,
                uploaded_file_dict
            )
            
            if build_result.get("success"):
                # Build successful!
                response_text = f"""✅ **APP BUILT SUCCESSFULLY!**

🎯 **What I Built:**
- 📁 App Name: {build_result['app_name']}
- 💻 Language: {build_result['language']}
- 📄 Files Created: {len(build_result['files_created'])}
- 🌐 URL: {build_result.get('url', 'Starting server...')}

📂 **Files:**
{chr(10).join(f"  ✓ {f}" for f in build_result['files_created'][:10])}

🎉 **Your app is live and running!**

📍 Location: `{build_result['app_directory']}`

Need changes? Just tell me what to modify!
"""
                
                # Save to context
                context_manager.save_conversation(
                    request.message,
                    response_text,
                    {"app_built": True, "build_result": build_result}
                )
                
                return {
                    "success": True,
                    "response": response_text,
                    "app_built": True,
                    "build_result": build_result,
                    "model_used": "auto_app_builder"
                }
            else:
                # Build failed, fall through to regular chat
                pass
        
        # REGULAR CHAT MODE: Use AI models
        # Handle uploaded file if present
        file_info = ""
        if request.uploaded_file:
            # Save file to project directory
            upload_dir = "uploaded_code"
            os.makedirs(upload_dir, exist_ok=True)
            file_path = os.path.join(upload_dir, request.uploaded_file.name)
            
            with open(file_path, 'w') as f:
                f.write(request.uploaded_file.content)
            
            file_info = f"\n\n[UPLOADED FILE: {request.uploaded_file.name} saved to {file_path}]\nFile content:\n```\n{request.uploaded_file.content}\n```\n"
        
        # Combine message with file info
        full_message = request.message + file_info
        
        # Route to appropriate model
        result = await model_router.route_and_execute(
            full_message,
            request.model_type
        )
        
        # Save to context
        context_manager.save_conversation(
            request.message,
            result.get("response", ""),
            {"tool_calls": result.get("tool_calls", [])}
        )
        
        return {
            "success": True,
            "response": result.get("response"),
            "tool_calls": result.get("tool_calls", []),
            "model_used": result.get("model"),
            "context_summary": context_manager.get_context_summary()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agent/tools")
async def list_available_tools(auth=Depends(is_admin_or_user)):
    """Get list of all available tools"""
    tools = registry.get_tool_definitions()
    
    return {
        "success": True,
        "total_tools": len(tools),
        "tools": tools
    }


@router.post("/agent/tool/execute")
async def execute_tool(request: ToolExecuteRequest, auth=Depends(is_admin_or_user)):
    """
    Manually execute a specific tool
    SECURITY: Requires authentication, admin-only for dangerous tools
    """
    # Get tool info
    if request.tool_name not in registry.tools:
        raise HTTPException(status_code=404, detail=f"Tool '{request.tool_name}' not found")
    
    tool_info = registry.tools[request.tool_name]
    
    # Check if dangerous operation - require admin
    if tool_info.get("dangerous", False) and auth["role"] != "admin":
        raise HTTPException(
            status_code=403,
            detail=f"Tool '{request.tool_name}' is dangerous and requires admin privileges"
        )
    
    try:
        result = await registry.execute_tool(
            request.tool_name,
            request.arguments
        )
        
        return {
            "success": True,
            "tool": request.tool_name,
            "result": result,
            "executed_by": auth["username"]
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/agent/history")
async def get_tool_history(limit: int = 10, auth=Depends(is_admin_or_user)):
    """Get tool execution history"""
    history = registry.get_execution_history(limit)
    
    return {
        "success": True,
        "history": history
    }


# ==================== CONTEXT MANAGEMENT ENDPOINTS ====================

@router.get("/context/summary")
async def get_context_summary(auth=Depends(is_admin_or_user)):
    """Get current context summary"""
    return {
        "success": True,
        "summary": context_manager.get_context_summary()
    }


@router.post("/context/search")
async def search_context(query: str, limit: int = 5, auth=Depends(is_admin_or_user)):
    """Search conversation history"""
    results = context_manager.search_conversations(query, limit)
    
    return {
        "success": True,
        "query": query,
        "results": results
    }


@router.post("/context/clear")
async def clear_context(auth=Depends(is_admin_or_user)):
    """Clear current context"""
    context_manager.clear_context()
    
    return {
        "success": True,
        "message": "Context cleared"
    }


@router.get("/context/export")
async def export_context(auth=Depends(is_admin_or_user)):
    """Export current context as JSON"""
    context_json = context_manager.export_context()
    
    return {
        "success": True,
        "context": context_json
    }


# ==================== CODEBASE INTELLIGENCE ENDPOINTS ====================

@router.post("/code/analyze")
async def analyze_code_file(request: CodeAnalysisRequest, auth=Depends(is_admin_or_user)):
    """Analyze a Python file"""
    try:
        analysis = codebase_analyzer.analyze_python_file(request.file_path)
        
        return {
            "success": True,
            "analysis": analysis
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/code/scan")
async def scan_codebase(request: CodebaseScanRequest, auth=Depends(is_admin_or_user)):
    """Scan entire codebase"""
    try:
        results = codebase_analyzer.scan_codebase(request.extensions)
        
        return {
            "success": True,
            "scan_results": results
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/code/refactor-suggestions")
async def get_refactor_suggestions(request: CodeAnalysisRequest, auth=Depends(is_admin_or_user)):
    """Get refactoring suggestions for a file"""
    try:
        suggestions = codebase_analyzer.suggest_refactoring(request.file_path)
        
        return {
            "success": True,
            "file": request.file_path,
            "suggestions": suggestions
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/code/unused-imports")
async def find_unused_imports(request: CodeAnalysisRequest, auth=Depends(is_admin_or_user)):
    """Find unused imports in a file"""
    try:
        unused = codebase_analyzer.find_unused_imports(request.file_path)
        
        return {
            "success": True,
            "file": request.file_path,
            "unused_imports": unused
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ==================== VIDEO GENERATION ENDPOINTS ====================

class VideoGenerationRequest(BaseModel):
    prompt: str
    duration: int = 5
    aspect_ratio: str = "16:9"
    model: str = "gen3a_turbo"

class VideoStatusRequest(BaseModel):
    task_id: str

@router.post("/video/generate")
async def generate_video(request: VideoGenerationRequest, auth=Depends(is_admin_or_user)):
    """Generate AI video using Runway ML Gen-3 Alpha"""
    try:
        runway = RunwayVideoGenerator()
        result = runway.generate_video_from_text(
            prompt=request.prompt,
            duration=request.duration,
            aspect_ratio=request.aspect_ratio,
            model=request.model
        )
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/video/status")
async def check_video_status(request: VideoStatusRequest, auth=Depends(is_admin_or_user)):
    """Check status of video generation task"""
    try:
        runway = RunwayVideoGenerator()
        result = runway.check_status(request.task_id)
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== SYSTEM STATUS ENDPOINTS ====================

@router.get("/system/status")
async def get_system_status():
    """Get overall system status"""
    gemini_available = bool(os.getenv('GEMINI_API_KEY'))
    groq_available = bool(os.getenv('GROQ_API_KEY'))
    runway_available = bool(os.getenv('RUNWAY_API_KEY'))
    
    return {
        "success": True,
        "status": "operational",
        "features": {
            "tool_calling": True,
            "context_management": True,
            "codebase_intelligence": True,
            "video_generation": runway_available,
            "multi_modal": False,
            "plugin_system": False
        },
        "ai_models": {
            "gemini": gemini_available,
            "groq": groq_available,
            "claude": False,
            "openai": False,
            "runway": runway_available
        },
        "tools_registered": len(registry.tools),
        "context_size": len(context_manager.current_context)
    }
