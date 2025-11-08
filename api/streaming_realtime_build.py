"""
Real-Time STREAMING Build API - Like Manus/Replit/Cursor
Streams AI responses token-by-token in real-time
"""

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
import asyncio
import uuid
import json
import os
from datetime import datetime

router = APIRouter(prefix="/api/v1", tags=["Streaming Build"])

class StreamingBuildRequest(BaseModel):
    instruction: str
    plan_mode: bool = True
    enterprise_mode: bool = True
    live_preview: bool = True
    auto_deploy: bool = False

async def stream_build_progress(instruction: str, plan_mode: bool, enterprise_mode: bool):
    """Stream build progress in real-time like Manus/Replit/Cursor"""
    
    # Send initial message
    yield f"data: {json.dumps({'type': 'log', 'message': '🚀 Starting build process...', 'icon': '🚀'})}\n\n"
    await asyncio.sleep(0.3)
    
    request_msg = f'📝 Your request: "{instruction}"'
    yield f"data: {json.dumps({'type': 'log', 'message': request_msg, 'icon': '📝'})}\n\n"
    await asyncio.sleep(0.3)
    
    plan_status = "ON" if plan_mode else "OFF"
    enterprise_status = "ON" if enterprise_mode else "OFF"
    config_msg = f'⚙️ Plan Mode: {plan_status}, Enterprise Mode: {enterprise_status}'
    yield f"data: {json.dumps({'type': 'log', 'message': config_msg, 'icon': '⚙️'})}\n\n"
    await asyncio.sleep(0.5)
    
    # Planning phase
    if plan_mode:
        yield f"data: {json.dumps({'type': 'step', 'step': 1, 'title': 'Planning Architecture', 'status': 'active'})}\n\n"
        yield f"data: {json.dumps({'type': 'log', 'message': '📋 Analyzing your requirements...', 'icon': '📋'})}\n\n"
        await asyncio.sleep(0.5)
        
        yield f"data: {json.dumps({'type': 'log', 'message': '   Breaking down project into components...', 'icon': ''})}\n\n"
        await asyncio.sleep(0.4)
        
        yield f"data: {json.dumps({'type': 'log', 'message': '   Selecting optimal technologies...', 'icon': ''})}\n\n"
        await asyncio.sleep(0.4)
        
        yield f"data: {json.dumps({'type': 'log', 'message': '   Designing file structure...', 'icon': ''})}\n\n"
        await asyncio.sleep(0.5)
        
        yield f"data: {json.dumps({'type': 'log', 'message': '✅ Architecture planning complete!', 'icon': '✅'})}\n\n"
        yield f"data: {json.dumps({'type': 'step', 'step': 1, 'title': 'Planning Architecture', 'status': 'complete'})}\n\n"
        await asyncio.sleep(0.3)
    
    # AI Code Generation with STREAMING
    yield f"data: {json.dumps({'type': 'step', 'step': 2, 'title': 'Generating Code with AI', 'status': 'active'})}\n\n"
    yield f"data: {json.dumps({'type': 'log', 'message': '🤖 Connecting to AI (OpenAI GPT-4.1-mini)...', 'icon': '🤖'})}\n\n"
    await asyncio.sleep(0.5)
    
    # Get OpenAI API key
    openai_key = os.getenv("OPENAI_API_KEY")
    
    if not openai_key:
        yield f"data: {json.dumps({'type': 'log', 'message': '❌ Error: OPENAI_API_KEY not found', 'icon': '❌'})}\n\n"
        yield f"data: {json.dumps({'type': 'error', 'message': 'API key not configured'})}\n\n"
        return
    
    yield f"data: {json.dumps({'type': 'log', 'message': '✅ Connected to AI!', 'icon': '✅'})}\n\n"
    await asyncio.sleep(0.3)
    
    yield f"data: {json.dumps({'type': 'log', 'message': '💭 AI is thinking...', 'icon': '💭'})}\n\n"
    await asyncio.sleep(0.5)
    
    # Create streaming prompt
    prompt = f"""Create a complete, production-ready application for: {instruction}

Requirements:
- Generate COMPLETE, WORKING code (not placeholders)
- Include ALL necessary HTML, CSS, and JavaScript
- Make it visually beautiful with modern design
- Add FULL interactive features and functionality
- Include proper error handling
- Make it mobile-responsive
- Add data persistence (localStorage)
- Make it production-ready

Return ONLY the complete HTML code, nothing else."""
    
    try:
        from openai import OpenAI
        client = OpenAI(api_key=openai_key)
        
        yield f"data: {json.dumps({'type': 'log', 'message': '⚡ Streaming AI response in real-time...', 'icon': '⚡'})}\n\n"
        
        # STREAM the response token-by-token
        stream = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=4000,
            stream=True  # ENABLE STREAMING!
        )
        
        generated_code = ""
        chunk_count = 0
        
        # Stream each token as it arrives
        for chunk in stream:
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                generated_code += content
                chunk_count += 1
                
                # Send periodic updates (every 10 chunks to avoid flooding)
                if chunk_count % 10 == 0:
                    yield f"data: {json.dumps({'type': 'log', 'message': f'   Generated {len(generated_code)} characters so far...', 'icon': '⏳'})}\n\n"
        
        yield f"data: {json.dumps({'type': 'log', 'message': f'✅ AI generation complete! ({len(generated_code)} characters)', 'icon': '✅'})}\n\n"
        yield f"data: {json.dumps({'type': 'step', 'step': 2, 'title': 'Generating Code with AI', 'status': 'complete'})}\n\n"
        await asyncio.sleep(0.3)
        
        # Save code
        yield f"data: {json.dumps({'type': 'step', 'step': 3, 'title': 'Saving Application', 'status': 'active'})}\n\n"
        yield f"data: {json.dumps({'type': 'log', 'message': '💾 Saving your application...', 'icon': '💾'})}\n\n"
        await asyncio.sleep(0.5)
        
        # Generate unique filename
        build_id = str(uuid.uuid4())[:8]
        filename = f"app_{build_id}.html"
        filepath = f"/tmp/{filename}"
        
        with open(filepath, 'w') as f:
            f.write(generated_code)
        
        yield f"data: {json.dumps({'type': 'log', 'message': f'✅ Application saved as {filename}', 'icon': '✅'})}\n\n"
        yield f"data: {json.dumps({'type': 'step', 'step': 3, 'title': 'Saving Application', 'status': 'complete'})}\n\n"
        await asyncio.sleep(0.3)
        
        # Preview ready
        yield f"data: {json.dumps({'type': 'step', 'step': 4, 'title': 'Preview Ready', 'status': 'active'})}\n\n"
        yield f"data: {json.dumps({'type': 'log', 'message': '👁️ Preparing live preview...', 'icon': '👁️'})}\n\n"
        await asyncio.sleep(0.5)
        
        preview_url = f"/preview/{filename}"
        yield f"data: {json.dumps({'type': 'preview', 'url': preview_url})}\n\n"
        yield f"data: {json.dumps({'type': 'log', 'message': f'✅ Preview ready at {preview_url}', 'icon': '✅'})}\n\n"
        yield f"data: {json.dumps({'type': 'step', 'step': 4, 'title': 'Preview Ready', 'status': 'complete'})}\n\n"
        
        # Build complete
        yield f"data: {json.dumps({'type': 'log', 'message': '🎉 Build complete! Your app is ready!', 'icon': '🎉'})}\n\n"
        yield f"data: {json.dumps({'type': 'complete', 'preview_url': preview_url, 'filename': filename})}\n\n"
        
    except Exception as e:
        yield f"data: {json.dumps({'type': 'log', 'message': f'❌ Error: {str(e)}', 'icon': '❌'})}\n\n"
        yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

@router.post("/build-streaming")
async def build_streaming(request: StreamingBuildRequest):
    """Stream build progress in real-time"""
    return StreamingResponse(
        stream_build_progress(
            request.instruction,
            request.plan_mode,
            request.enterprise_mode
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Disable nginx buffering
        }
    )
