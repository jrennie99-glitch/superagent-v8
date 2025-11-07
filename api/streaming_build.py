"""
Real-Time Streaming Build System - Server-Sent Events (SSE)
Provides instant, step-by-step build progress updates
Works alongside existing build system without replacing anything
"""

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from typing import AsyncGenerator
import asyncio
import json
from datetime import datetime

router = APIRouter(prefix="/api/v1", tags=["Streaming Build"])

# Import existing build progress store
from api.realtime_build import build_progress_store

@router.get("/build-stream/{build_id}")
async def stream_build_progress(build_id: str):
    """
    Stream build progress in real-time using Server-Sent Events (SSE).
    This provides instant updates to the frontend without polling.
    """
    
    async def event_generator() -> AsyncGenerator[str, None]:
        """Generate SSE events for build progress"""
        last_step_count = 0
        
        # Keep streaming until build is complete or errored
        while True:
            # Check if build exists
            if build_id not in build_progress_store:
                yield f"data: {json.dumps({'error': 'Build not found'})}\n\n"
                break
            
            progress = build_progress_store[build_id]
            current_step_count = len(progress.get('steps', []))
            
            # Send new steps only (avoid duplicates)
            if current_step_count > last_step_count:
                for i in range(last_step_count, current_step_count):
                    step = progress['steps'][i]
                    event_data = {
                        'type': 'step',
                        'step_number': step['step_number'],
                        'title': step['title'],
                        'detail': step['detail'],
                        'status': step['status'],
                        'timestamp': datetime.now().isoformat()
                    }
                    yield f"data: {json.dumps(event_data)}\n\n"
                
                last_step_count = current_step_count
            
            # Send status updates
            status_event = {
                'type': 'status',
                'status': progress['status'],
                'preview_url': progress.get('preview_url'),
                'deployment_url': progress.get('deployment_url'),
                'total_time': progress.get('total_time', 0.0),
                'error': progress.get('error')
            }
            yield f"data: {json.dumps(status_event)}\n\n"
            
            # Check if build is complete or errored
            if progress['status'] in ['complete', 'error']:
                # Send final completion event
                final_event = {
                    'type': 'complete',
                    'status': progress['status'],
                    'preview_url': progress.get('preview_url'),
                    'deployment_url': progress.get('deployment_url'),
                    'total_time': progress.get('total_time', 0.0),
                    'error': progress.get('error')
                }
                yield f"data: {json.dumps(final_event)}\n\n"
                break
            
            # Wait before next check (very short interval for real-time feel)
            await asyncio.sleep(0.1)
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Disable nginx buffering
        }
    )


@router.post("/build-with-confirmation")
async def build_with_confirmation(request: dict):
    """
    Enhanced build endpoint that returns build info for confirmation dialog.
    User confirms, then frontend connects to SSE stream.
    """
    instruction = request.get('instruction', '')
    build_type = request.get('build_type', 'full')
    plan_mode = request.get('plan_mode', True)
    enterprise_mode = request.get('enterprise_mode', True)
    
    # Estimate build time based on complexity
    estimated_time = "2-3 minutes" if build_type == 'full' else "1-2 minutes"
    
    # Determine what will be built
    features = []
    if plan_mode:
        features.append("📋 Strategic planning & architecture design")
    
    features.extend([
        "🤖 AI-powered code generation",
        "📝 Complete file structure creation",
        "🎨 Modern, responsive UI design"
    ])
    
    if build_type == 'full':
        features.extend([
            "⚡ Full interactive functionality",
            "💾 Data persistence (localStorage)",
            "🔒 Error handling & validation"
        ])
    
    if request.get('auto_deploy'):
        features.append("🚀 Automatic deployment to production")
    
    # Return confirmation data
    return {
        "instruction": instruction,
        "build_type": build_type,
        "estimated_time": estimated_time,
        "features": features,
        "plan_mode": plan_mode,
        "enterprise_mode": enterprise_mode,
        "message": f"Ready to build: {instruction[:100]}..."
    }
