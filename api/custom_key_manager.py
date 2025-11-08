"""
Custom API Key Manager - Allows users to use their own Gemini API key
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
import json

router = APIRouter(prefix="/api/v1", tags=["Settings"])

CUSTOM_KEY_FILE = "/tmp/custom_gemini_key.json"

class CustomKeyRequest(BaseModel):
    api_key: str

def get_custom_gemini_key():
    """Get custom Gemini API key if set, otherwise use default"""
    try:
        if os.path.exists(CUSTOM_KEY_FILE):
            with open(CUSTOM_KEY_FILE, 'r') as f:
                data = json.load(f)
                custom_key = data.get('gemini_api_key')
                if custom_key:
                    return custom_key
    except Exception as e:
        print(f"Error reading custom key: {e}")
    
    # Fallback to default environment key
    return os.getenv("GEMINI_API_KEY")

@router.post("/set-custom-key")
async def set_custom_key(request: CustomKeyRequest):
    """Set a custom Gemini API key"""
    try:
        # Save to file
        with open(CUSTOM_KEY_FILE, 'w') as f:
            json.dump({'gemini_api_key': request.api_key}, f)
        
        return {
            "success": True,
            "message": "Custom API key saved! Your builds will now use your own quota."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/has-custom-key")
async def has_custom_key():
    """Check if a custom API key is set"""
    has_key = os.path.exists(CUSTOM_KEY_FILE)
    return {"has_custom_key": has_key}

@router.delete("/remove-custom-key")
async def remove_custom_key():
    """Remove custom API key and revert to default"""
    try:
        if os.path.exists(CUSTOM_KEY_FILE):
            os.remove(CUSTOM_KEY_FILE)
        return {"success": True, "message": "Reverted to default API key"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
