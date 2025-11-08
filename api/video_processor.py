"""
Video Processing API Endpoint
Handles video upload, analysis, and app generation from video content
"""

import os
import base64
import tempfile
from pathlib import Path
from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
import google.generativeai as genai

router = APIRouter()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

@router.post("/api/v1/upload-video")
async def upload_video(
    video: UploadFile = File(...),
    instructions: str = Form(...)
):
    """
    Upload video file and analyze it using Gemini Vision AI
    Returns analysis that can be used to generate app
    """
    try:
        # Validate file size (max 100MB)
        max_size = 100 * 1024 * 1024  # 100MB
        content = await video.read()
        if len(content) > max_size:
            raise HTTPException(status_code=400, detail="Video file too large. Maximum size is 100MB.")
        
        # Validate file type
        if not video.content_type or not video.content_type.startswith('video/'):
            raise HTTPException(status_code=400, detail="Invalid file type. Please upload a video file.")
        
        # Save video temporarily
        temp_dir = Path("uploads")
        temp_dir.mkdir(exist_ok=True)
        
        video_path = temp_dir / video.filename
        with open(video_path, "wb") as f:
            f.write(content)
        
        try:
            # Upload video to Gemini
            uploaded_file = genai.upload_file(str(video_path))
            
            # Analyze video with Gemini
            model = genai.GenerativeModel("gemini-2.0-flash-exp")
            
            analysis_prompt = f"""
You are an expert app designer analyzing a video to understand what app should be built.

User Instructions: {instructions}

Please analyze this video and provide:
1. **UI/UX Description**: Describe the visual interface, layout, colors, and design elements shown
2. **Functionality**: What features and interactions does the app demonstrate?
3. **Components**: List the key UI components (buttons, inputs, displays, etc.)
4. **User Flow**: How does the user interact with the app?
5. **Technical Requirements**: What technologies or frameworks would be needed?
6. **App Type**: Is this a calculator, todo list, game, dashboard, form, etc.?

Provide a comprehensive analysis that would allow another AI to recreate this app exactly as shown in the video.
"""
            
            response = model.generate_content([analysis_prompt, uploaded_file])
            analysis = response.text
            
            # Clean up
            video_path.unlink()
            
            return JSONResponse({
                "success": True,
                "analysis": analysis,
                "filename": video.filename,
                "instructions": instructions
            })
            
        except Exception as e:
            # Clean up on error
            if video_path.exists():
                video_path.unlink()
            raise HTTPException(status_code=500, detail=f"Video analysis failed: {str(e)}")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")
