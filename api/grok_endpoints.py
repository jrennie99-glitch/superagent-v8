"""
SuperAgent v2.0 - Grok Co-Pilot API Endpoints
Real-time AI assistance endpoints
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict
import logging
from api.grok_copilot import grok_copilot

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v2/grok", tags=["grok_copilot"])

class GrokQuestionRequest(BaseModel):
    """Request to ask Grok a question"""
    build_id: str
    question: str
    context: Optional[Dict] = None

class GrokApplyRequest(BaseModel):
    """Request to apply Grok recommendation"""
    build_id: str
    decision_id: int
    auto_apply: bool = True

@router.post("/ask")
async def ask_grok_question(request: GrokQuestionRequest):
    """
    Ask Grok Co-Pilot a question
    
    Examples:
    - "Optimize this SQL for 1M users"
    - "Make this UI convert 40% better"
    - "Secure this file upload endpoint"
    - "Best tech stack for real-time duet video sync?"
    
    Returns:
    - AI-powered recommendation
    - Code examples
    - Estimated improvements
    """
    try:
        result = await grok_copilot.ask_grok(
            build_id=request.build_id,
            question=request.question,
            context=request.context
        )
        
        if not result.get("success", False):
            raise HTTPException(status_code=500, detail=result.get("error", "Grok request failed"))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in ask_grok_question: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/apply")
async def apply_grok_recommendation(request: GrokApplyRequest):
    """
    Apply Grok's recommendation
    
    Features:
    - Auto-apply code changes
    - Diff preview
    - Rollback capability
    """
    try:
        result = await grok_copilot.apply_grok_response(
            build_id=request.build_id,
            decision_id=request.decision_id,
            auto_apply=request.auto_apply
        )
        
        if not result.get("success", False):
            raise HTTPException(status_code=500, detail=result.get("error", "Apply failed"))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in apply_grok_recommendation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/rollback/{build_id}")
async def rollback_grok_decision(build_id: str):
    """
    Rollback last applied Grok decision
    
    Reverts code changes and restores previous state
    """
    try:
        result = await grok_copilot.rollback_decision(build_id)
        
        if not result.get("success", False):
            raise HTTPException(status_code=400, detail=result.get("error", "Rollback failed"))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in rollback_grok_decision: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history/{build_id}")
async def get_grok_history(build_id: str):
    """Get all Grok decisions for a build session"""
    try:
        history = grok_copilot.get_decision_history(build_id)
        
        return {
            "success": True,
            "build_id": build_id,
            "total_decisions": len(history),
            "decisions": history
        }
        
    except Exception as e:
        logger.error(f"Error in get_grok_history: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/examples")
async def get_grok_examples():
    """Get example Grok questions and use cases"""
    return {
        "success": True,
        "examples": [
            {
                "category": "SQL Optimization",
                "question": "Optimize this SQL for 1M users",
                "use_case": "Database performance tuning"
            },
            {
                "category": "UI/UX",
                "question": "Make this UI convert 40% better",
                "use_case": "Conversion rate optimization"
            },
            {
                "category": "Security",
                "question": "Secure this file upload endpoint",
                "use_case": "Security hardening"
            },
            {
                "category": "Tech Stack",
                "question": "Best tech stack for real-time duet video sync?",
                "use_case": "Architecture decisions"
            },
            {
                "category": "Performance",
                "question": "Make this page load 3x faster",
                "use_case": "Performance optimization"
            },
            {
                "category": "Scaling",
                "question": "How to handle 100K concurrent users?",
                "use_case": "Scalability planning"
            }
        ]
    }

# Export router
grok_copilot_router = router
