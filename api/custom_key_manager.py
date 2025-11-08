"""
Custom API Key Manager - Secure API key management via Replit Secrets
Supports multiple AI providers: Gemini, GROQ, OpenAI, etc.
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
    
    print("❌ No Gemini API key found!")
    return None

def get_custom_groq_key():
    """Get GROQ API key - Priority: USER_GROQ_API_KEY > GROQ_API_KEY (system default)"""
    
    # Priority 1: Check if user set their own key via Replit Secrets
    user_key = os.getenv("USER_GROQ_API_KEY")
    if user_key:
        print("✅ Using USER_GROQ_API_KEY (your personal GROQ key with blazing fast inference)")
        return user_key
    
    # Priority 2: Fallback to default system key (if exists)
    system_key = os.getenv("GROQ_API_KEY")
    if system_key:
        print("⚠️ Using default GROQ API key (shared quota)")
        return system_key
    
    print("❌ No GROQ API key found!")
    return None

def get_ai_provider():
    """Determine which AI provider to use based on available keys
    
    Priority:
    1. GROQ (if USER_GROQ_API_KEY is set) - Fastest inference
    2. Gemini (if USER_GEMINI_API_KEY is set) - Large free tier
    3. Gemini (system default)
    """
    
    # Check for user's custom GROQ key (highest priority for performance)
    if os.getenv("USER_GROQ_API_KEY"):
        return "groq"
    
    # Check for user's custom Gemini key
    if os.getenv("USER_GEMINI_API_KEY"):
        return "gemini"
    
    # Fallback to system Gemini key
    if os.getenv("GEMINI_API_KEY"):
        return "gemini"
    
    # Fallback to system GROQ key
    if os.getenv("GROQ_API_KEY"):
        return "groq"
    
    return "gemini"  # Default

@router.get("/api-key-status")
async def api_key_status():
    """Check which API keys are currently available"""
    
    # Gemini keys
    user_gemini_key_set = bool(os.getenv("USER_GEMINI_API_KEY"))
    system_gemini_key_set = bool(os.getenv("GEMINI_API_KEY"))
    
    # GROQ keys
    user_groq_key_set = bool(os.getenv("USER_GROQ_API_KEY"))
    system_groq_key_set = bool(os.getenv("GROQ_API_KEY"))
    
    # Determine active provider
    active_provider = get_ai_provider()
    
    if active_provider == "groq" and user_groq_key_set:
        status = "using_personal_groq"
        message = "✅ Using your personal GROQ API key (blazing fast inference + free tier)"
    elif active_provider == "gemini" and user_gemini_key_set:
        status = "using_personal_gemini"
        message = "✅ Using your personal Gemini API key (1,500 free requests/day)"
    elif active_provider == "gemini" and system_gemini_key_set:
        status = "using_shared_gemini"
        message = "⚠️ Using shared Gemini system key (may experience rate limits)"
    elif active_provider == "groq" and system_groq_key_set:
        status = "using_shared_groq"
        message = "⚠️ Using shared GROQ system key"
    else:
        status = "no_key"
        message = "❌ No API keys configured"
    
    return {
        "status": status,
        "message": message,
        "active_provider": active_provider,
        "gemini": {
            "has_personal_key": user_gemini_key_set,
            "has_system_key": system_gemini_key_set,
            "is_active": active_provider == "gemini"
        },
        "groq": {
            "has_personal_key": user_groq_key_set,
            "has_system_key": system_groq_key_set,
            "is_active": active_provider == "groq"
        }
    }
