"""
Custom API Key Manager - Secure API key management via Replit Secrets
"""
from fastapi import APIRouter
from pydantic import BaseModel
import os

router = APIRouter(prefix="/api/v1", tags=["Settings"])

class CustomKeyRequest(BaseModel):
    api_key: str

def get_custom_gemini_key():
    """Get Gemini API key - Priority: USER_GEMINI_API_KEY > GEMINI_API_KEY (system default)"""
    
    # Priority 1: Check if user set their own key via Replit Secrets
    user_key = os.getenv("USER_GEMINI_API_KEY")
    if user_key:
        print("✅ Using USER_GEMINI_API_KEY (your personal key with your own quota)")
        return user_key
    
    # Priority 2: Fallback to default system key (shared quota - may hit rate limits)
    system_key = os.getenv("GEMINI_API_KEY")
    if system_key:
        print("⚠️ Using default system API key (shared quota - may experience rate limits)")
        return system_key
    
    print("❌ No API key found!")
    return None

@router.get("/api-key-status")
async def api_key_status():
    """Check which API key is currently in use"""
    user_key_set = bool(os.getenv("USER_GEMINI_API_KEY"))
    system_key_set = bool(os.getenv("GEMINI_API_KEY"))
    
    if user_key_set:
        status = "using_personal_key"
        message = "✅ Using your personal API key (your own quota)"
    elif system_key_set:
        status = "using_shared_key"
        message = "⚠️ Using shared system key (may experience rate limits)"
    else:
        status = "no_key"
        message = "❌ No API key configured"
    
    return {
        "status": status,
        "message": message,
        "has_personal_key": user_key_set,
        "has_system_key": system_key_set
    }
