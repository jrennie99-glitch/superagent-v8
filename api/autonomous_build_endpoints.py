"""
SuperAgent v2.0 - Autonomous Build API Endpoints
Triggers autonomous app generation from uploaded media
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict
import logging
from api.autonomous_app_generator import autonomous_app_generator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v2/build", tags=["autonomous_build"])

class BuildFromVideoRequest(BaseModel):
    """Request to build app from video"""
    file_id: str
    app_type: str = "tiktok_clone"  # tiktok_clone, youtube_clone
    video_metadata: Optional[Dict] = None

class BuildFromImageRequest(BaseModel):
    """Request to build app from image"""
    file_id: str
    app_type: str = "instagram_clone"  # instagram_clone, meme_generator
    image_metadata: Optional[Dict] = None

class BuildFromAudioRequest(BaseModel):
    """Request to build app from audio"""
    file_id: str
    app_type: str = "music_video_app"  # music_video_app, podcast_app
    audio_metadata: Optional[Dict] = None

@router.post("/from-video")
async def build_app_from_video(request: BuildFromVideoRequest):
    """
    Build full-stack app from uploaded video
    
    Supported app types:
    - tiktok_clone: Short video platform (3 min build)
    - youtube_clone: Video streaming platform (4 min build)
    
    Returns:
    - Live app URL
    - GitHub repository
    - Build log
    - Tech stack details
    """
    try:
        logger.info(f"Building {request.app_type} from video {request.file_id}")
        
        # Get video file path from file_id
        from pathlib import Path
        upload_dir = Path("/tmp/superagent_uploads")
        video_files = list(upload_dir.glob(f"*{request.file_id}*"))
        
        if not video_files:
            raise HTTPException(status_code=404, detail="Video file not found")
        
        video_path = str(video_files[0])
        
        # Generate app
        result = await autonomous_app_generator.generate_from_video(
            video_path=video_path,
            video_metadata=request.video_metadata or {},
            app_type=request.app_type
        )
        
        if not result.get("success", False):
            raise HTTPException(status_code=500, detail=result.get("error", "Build failed"))
        
        return {
            "success": True,
            "message": f"✅ {result['app_name']} built and deployed in {result['build_time']:.1f}s!",
            "app_url": result["app_url"],
            "github_url": result["github_url"],
            "tech_stack": result["tech_stack"],
            "features": result["features"],
            "build_time": result["build_time"],
            "build_log": result["build_log"],
            "deployment": {
                "platform": "Render",
                "status": "deployed",
                "url": result["app_url"]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error building app from video: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/from-image")
async def build_app_from_image(request: BuildFromImageRequest):
    """
    Build full-stack app from uploaded image
    
    Supported app types:
    - instagram_clone: Photo sharing platform (3 min build)
    - meme_generator: Viral meme creation app (2 min build)
    
    Returns:
    - Live app URL
    - GitHub repository
    - Build log
    """
    try:
        logger.info(f"Building {request.app_type} from image {request.file_id}")
        
        from pathlib import Path
        upload_dir = Path("/tmp/superagent_uploads")
        image_files = list(upload_dir.glob(f"*{request.file_id}*"))
        
        if not image_files:
            raise HTTPException(status_code=404, detail="Image file not found")
        
        image_path = str(image_files[0])
        
        result = await autonomous_app_generator.generate_from_image(
            image_path=image_path,
            image_metadata=request.image_metadata or {},
            app_type=request.app_type
        )
        
        if not result.get("success", False):
            raise HTTPException(status_code=500, detail=result.get("error", "Build failed"))
        
        return {
            "success": True,
            "message": f"✅ {result['app_name']} built in {result['build_time']:.1f}s!",
            "app_url": result["app_url"],
            "github_url": result["github_url"],
            "tech_stack": result["tech_stack"],
            "features": result["features"],
            "build_time": result["build_time"],
            "build_log": result["build_log"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error building app from image: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/from-audio")
async def build_app_from_audio(request: BuildFromAudioRequest):
    """
    Build full-stack app from uploaded audio
    
    Supported app types:
    - music_video_app: AI music video generator with Sora 2 (5 min build)
    - podcast_app: Podcast hosting platform (3 min build)
    
    Returns:
    - Live app URL
    - Build log
    """
    try:
        logger.info(f"Building {request.app_type} from audio {request.file_id}")
        
        from pathlib import Path
        upload_dir = Path("/tmp/superagent_uploads")
        audio_files = list(upload_dir.glob(f"*{request.file_id}*"))
        
        if not audio_files:
            raise HTTPException(status_code=404, detail="Audio file not found")
        
        audio_path = str(audio_files[0])
        
        result = await autonomous_app_generator.generate_from_audio(
            audio_path=audio_path,
            audio_metadata=request.audio_metadata or {},
            app_type=request.app_type
        )
        
        if not result.get("success", False):
            raise HTTPException(status_code=500, detail=result.get("error", "Build failed"))
        
        return {
            "success": True,
            "message": f"✅ {result['app_name']} built in {result['build_time']:.1f}s!",
            "app_url": result["app_url"],
            "tech_stack": result["tech_stack"],
            "features": result["features"],
            "build_time": result["build_time"],
            "build_log": result["build_log"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error building app from audio: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/templates")
async def get_build_templates():
    """Get list of all available app templates"""
    return {
        "success": True,
        "templates": autonomous_app_generator.build_templates
    }

@router.get("/status/{build_id}")
async def get_build_status(build_id: str):
    """Get status of ongoing build"""
    # TODO: Implement build status tracking
    return {
        "success": True,
        "build_id": build_id,
        "status": "building",
        "progress": 75,
        "estimated_time_remaining": 45
    }

# Export router
autonomous_build_router = router
