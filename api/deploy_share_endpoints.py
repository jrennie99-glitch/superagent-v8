"""
SuperAgent v2.0 - Deploy & Share API Endpoints
One-click deployment and social sharing
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict
import logging
from api.deploy_share import deploy_share_system

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v2/deploy", tags=["deploy_share"])

class DeployRequest(BaseModel):
    """Request to deploy app"""
    app_id: str
    app_name: str
    app_type: str
    platforms: List[str] = ["render"]  # render, vercel, netlify, railway, flyio

class ShareRequest(BaseModel):
    """Request to generate share links"""
    app_url: str
    app_name: str
    platforms: List[str] = ["twitter", "facebook", "linkedin"]

@router.post("/multi-platform")
async def deploy_to_multiple_platforms(request: DeployRequest):
    """
    Deploy app to multiple platforms simultaneously
    
    Supported platforms:
    - render: Render.com
    - vercel: Vercel
    - netlify: Netlify
    - railway: Railway.app
    - flyio: Fly.io
    
    Returns:
    - Deployment URLs for each platform
    - GitHub repository
    - QR code
    - Download links
    """
    try:
        logger.info(f"Deploying {request.app_id} to {len(request.platforms)} platforms...")
        
        app_config = {
            "name": request.app_name,
            "type": request.app_type
        }
        
        results = {
            "app_id": request.app_id,
            "app_name": request.app_name,
            "deployments": [],
            "github": None,
            "qr_code": None,
            "downloads": None,
            "viral_score": None
        }
        
        # Deploy to each platform
        for platform in request.platforms:
            if platform == "render":
                result = await deploy_share_system.deploy_to_render(request.app_id, app_config)
            elif platform == "vercel":
                result = await deploy_share_system.deploy_to_vercel(request.app_id, app_config)
            elif platform == "netlify":
                result = await deploy_share_system.deploy_to_netlify(request.app_id, app_config)
            else:
                result = {
                    "success": False,
                    "platform": platform,
                    "error": "Platform not yet supported"
                }
            
            results["deployments"].append(result)
        
        # Create GitHub repo
        github_result = await deploy_share_system.create_github_repo(request.app_id, app_config)
        results["github"] = github_result
        
        # Generate QR code for primary deployment
        if results["deployments"] and results["deployments"][0].get("success"):
            primary_url = results["deployments"][0]["url"]
            qr_code = deploy_share_system.generate_qr_code(primary_url)
            results["qr_code"] = qr_code
        
        # Create download package
        download_result = await deploy_share_system.create_download_package(request.app_id, app_config)
        results["downloads"] = download_result
        
        # Predict viral score
        viral_score = await deploy_share_system.predict_viral_score(app_config)
        results["viral_score"] = viral_score
        
        return {
            "success": True,
            "message": f"✅ Deployed to {len([d for d in results['deployments'] if d.get('success')])} platforms!",
            **results
        }
        
    except Exception as e:
        logger.error(f"Error in multi-platform deployment: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/share")
async def generate_share_links(request: ShareRequest):
    """
    Generate social media share links
    
    Platforms:
    - twitter, facebook, linkedin, reddit
    - whatsapp, telegram
    - tiktok, instagram (embed codes)
    
    Returns:
    - Share links for each platform
    - Embed codes
    - Viral score prediction
    """
    try:
        # Generate share links
        share_links = deploy_share_system.generate_social_share_links(
            request.app_url,
            request.app_name
        )
        
        # Generate embed codes
        embed_codes = deploy_share_system.generate_embed_code(
            request.app_url,
            request.app_name
        )
        
        # Predict viral score
        viral_score = await deploy_share_system.predict_viral_score({
            "name": request.app_name,
            "type": "app"
        })
        
        return {
            "success": True,
            "app_url": request.app_url,
            "app_name": request.app_name,
            "share_links": share_links,
            "embed_codes": embed_codes,
            "viral_score": viral_score,
            "message": f"Share your app! Viral score: {viral_score['score']}/100 {viral_score['emoji']}"
        }
        
    except Exception as e:
        logger.error(f"Error generating share links: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/qr/{app_url:path}")
async def generate_qr_code(app_url: str):
    """Generate QR code for app URL"""
    try:
        qr_code = deploy_share_system.generate_qr_code(app_url)
        
        return {
            "success": True,
            "app_url": app_url,
            "qr_code": qr_code
        }
        
    except Exception as e:
        logger.error(f"Error generating QR code: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/viral-score")
async def predict_viral_score(app_config: Dict):
    """Predict viral potential of app"""
    try:
        viral_score = await deploy_share_system.predict_viral_score(app_config)
        
        return {
            "success": True,
            "viral_score": viral_score
        }
        
    except Exception as e:
        logger.error(f"Error predicting viral score: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/platforms")
async def get_supported_platforms():
    """Get list of supported deployment platforms"""
    return {
        "success": True,
        "platforms": [
            {
                "id": "render",
                "name": "Render",
                "type": "full-stack",
                "deploy_time": "2-3 min",
                "free_tier": True
            },
            {
                "id": "vercel",
                "name": "Vercel",
                "type": "frontend",
                "deploy_time": "1-2 min",
                "free_tier": True
            },
            {
                "id": "netlify",
                "name": "Netlify",
                "type": "frontend",
                "deploy_time": "1-2 min",
                "free_tier": True
            },
            {
                "id": "railway",
                "name": "Railway",
                "type": "full-stack",
                "deploy_time": "2-3 min",
                "free_tier": True
            },
            {
                "id": "flyio",
                "name": "Fly.io",
                "type": "full-stack",
                "deploy_time": "2-3 min",
                "free_tier": True
            }
        ]
    }

# Export router
deploy_share_router = router
