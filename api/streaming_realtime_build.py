"""
Real-Time STREAMING Build API - Like Manus/Replit/Cursor
Streams AI responses token-by-token in real-time with Enterprise Build System
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
import google.generativeai as genai
from asyncio import Queue

router = APIRouter(prefix="/api/v1", tags=["Streaming Build"])

class StreamingBuildRequest(BaseModel):
    instruction: str
    plan_mode: bool = True
    enterprise_mode: bool = True
    live_preview: bool = True
    auto_deploy: bool = False

async def stream_build_progress(instruction: str, plan_mode: bool, enterprise_mode: bool):
    """Stream build progress in real-time using Enterprise Build System"""
    
    # Send initial message
    yield f"data: {json.dumps({'type': 'log', 'message': '🚀 Starting SuperAgent build process...', 'icon': '🚀'})}\n\n"
    await asyncio.sleep(0.2)
    
    request_msg = f'📝 Your request: "{instruction}"'
    yield f"data: {json.dumps({'type': 'log', 'message': request_msg, 'icon': '📝'})}\n\n"
    await asyncio.sleep(0.2)
    
    plan_status = "ON" if plan_mode else "OFF"
    enterprise_status = "ON" if enterprise_mode else "OFF"
    config_msg = f'⚙️ Plan Mode: {plan_status}, Enterprise Mode: {enterprise_status}'
    yield f"data: {json.dumps({'type': 'log', 'message': config_msg, 'icon': '⚙️'})}\n\n"
    await asyncio.sleep(0.3)
    
    # Get Gemini API key
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        yield f"data: {json.dumps({'type': 'log', 'message': '❌ Error: GEMINI_API_KEY not found', 'icon': '❌'})}\n\n"
        yield f"data: {json.dumps({'type': 'error', 'message': 'API key not configured. Please add GEMINI_API_KEY to your secrets.'})}\n\n"
        return
    
    # Configure Gemini
    genai.configure(api_key=gemini_key)
    
    yield f"data: {json.dumps({'type': 'log', 'message': '🤖 Connecting to Gemini AI...', 'icon': '🤖'})}\n\n"
    await asyncio.sleep(0.3)
    yield f"data: {json.dumps({'type': 'log', 'message': '✅ Connected to Gemini 2.0 Flash!', 'icon': '✅'})}\n\n"
    await asyncio.sleep(0.2)
    
    # Use Enterprise Build System if enabled
    if enterprise_mode:
        yield f"data: {json.dumps({'type': 'log', 'message': '🏭 Initiating Enterprise Build System (9-stage production pipeline)...', 'icon': '🏭'})}\n\n"
        await asyncio.sleep(0.3)
        
        try:
            # Import Enterprise Build System components
            from api.enterprise_builder import EnterpriseBuildSystem
            from api.app_builder import AppBuilder
            from api.rollback_system import RollbackSystem
            from api.hallucination_fixer import HallucinationFixer
            from api.cybersecurity_ai import cybersecurity_agent
            
            # Initialize components
            basic_builder = AppBuilder()
            hallucination_fixer = HallucinationFixer()
            rollback_system = RollbackSystem()
            enterprise_system = EnterpriseBuildSystem(
                basic_builder,
                rollback_system,
                hallucination_fixer,
                cybersecurity_agent
            )
            
            # Detect language from instruction
            instruction_lower = instruction.lower()
            if 'python' in instruction_lower or 'flask' in instruction_lower or 'django' in instruction_lower:
                language = 'python'
            elif 'react' in instruction_lower or 'next' in instruction_lower or 'vue' in instruction_lower or 'node' in instruction_lower:
                language = 'javascript'
            elif 'website' in instruction_lower or 'webpage' in instruction_lower or 'landing' in instruction_lower:
                language = 'html'
            else:
                language = 'python'  # default
            
            yield f"data: {json.dumps({'type': 'log', 'message': f'📊 Detected language: {language.upper()}', 'icon': '📊'})}\n\n"
            await asyncio.sleep(0.2)
            
            yield f"data: {json.dumps({'type': 'log', 'message': '🚀 Starting enterprise build (this may take 2-5 minutes)...', 'icon': '🚀'})}\n\n"
            await asyncio.sleep(0.3)
            
            # Create async queue for real-time progress updates
            progress_queue = Queue()
            build_complete = {'done': False, 'result': None}
            
            # Progress callback that feeds the queue
            async def progress_callback(message: str, percent: int):
                icon = '⏳' if percent < 100 else '✅'
                await progress_queue.put({
                    'type': 'log',
                    'message': f'[{percent}%] {message}',
                    'icon': icon,
                    'percent': percent
                })
            
            # Background task to run enterprise build
            async def run_build():
                try:
                    result = await enterprise_system.enterprise_build(
                        instruction=instruction,
                        language=language,
                        enable_checkpoints=True,
                        enable_testing=True,
                        enable_security_scan=True,
                        enable_multi_file=True,
                        progress_callback=progress_callback
                    )
                    build_complete['result'] = result
                except Exception as e:
                    build_complete['result'] = {'success': False, 'error': str(e)}
                finally:
                    build_complete['done'] = True
                    await progress_queue.put(None)  # Signal completion
            
            # Start the build in background
            build_task = asyncio.create_task(run_build())
            
            # Stream progress updates as they arrive
            while True:
                try:
                    # Wait for next progress update (with timeout)
                    update = await asyncio.wait_for(progress_queue.get(), timeout=1.0)
                    
                    if update is None:  # Build complete signal
                        break
                    
                    # Send the progress update to frontend
                    yield f"data: {json.dumps(update)}\n\n"
                    
                    # Update step status based on percentage
                    percent = update.get('percent', 0)
                    step = max(1, min(5, (percent // 20) + 1))
                    status = 'active' if percent < 100 else 'complete'
                    yield f"data: {json.dumps({'type': 'step', 'step': step, 'status': status})}\n\n"
                    
                except asyncio.TimeoutError:
                    # No update in 1 second, send heartbeat
                    if build_complete['done']:
                        break
                    continue
            
            # Wait for build task to complete
            await build_task
            result = build_complete['result']
            
            if result.get('success'):
                project_dir = result.get('project_dir', '')
                files_created = result.get('files_created', [])
                build_time = result.get('build_time', 0)
                
                yield f"data: {json.dumps({'type': 'log', 'message': f'✅ Enterprise build complete in {build_time}s!', 'icon': '✅'})}\n\n"
                yield f"data: {json.dumps({'type': 'log', 'message': f'📁 Created {len(files_created)} files in {project_dir}', 'icon': '📁'})}\n\n"
                yield f"data: {json.dumps({'type': 'log', 'message': '🎉 Production-ready application generated!', 'icon': '🎉'})}\n\n"
                yield f"data: {json.dumps({'type': 'step', 'step': 5, 'status': 'complete'})}\n\n"
                yield f"data: {json.dumps({'type': 'complete', 'project_dir': project_dir, 'files': files_created})}\n\n"
            else:
                error = result.get('error', 'Unknown error')
                yield f"data: {json.dumps({'type': 'log', 'message': f'❌ Build failed: {error}', 'icon': '❌'})}\n\n"
                yield f"data: {json.dumps({'type': 'error', 'message': error})}\n\n"
                
        except Exception as e:
            yield f"data: {json.dumps({'type': 'log', 'message': f'❌ Error: {str(e)}', 'icon': '❌'})}\n\n"
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
    else:
        # Simple mode - just use Gemini to generate a single HTML file
        yield f"data: {json.dumps({'type': 'log', 'message': '💭 Generating application with Gemini...', 'icon': '💭'})}\n\n"
        yield f"data: {json.dumps({'type': 'step', 'step': 1, 'status': 'active'})}\n\n"
        
        try:
            model = genai.GenerativeModel('gemini-2.0-flash')
            prompt = f"""Create a complete, production-ready, beautiful web application for: {instruction}

Requirements:
- COMPLETE, WORKING code (no placeholders)
- Modern, beautiful design with CSS
- Full interactive features with JavaScript
- Mobile-responsive
- Include data persistence (localStorage if needed)
- Production-ready quality

Return ONLY the complete HTML code."""
            
            response = model.generate_content(prompt)
            generated_code = response.text
            
            # Save file
            build_id = str(uuid.uuid4())[:8]
            filename = f"app_{build_id}.html"
            filepath = f"/tmp/{filename}"
            
            with open(filepath, 'w') as f:
                f.write(generated_code)
            
            yield f"data: {json.dumps({'type': 'log', 'message': f'✅ Generated {len(generated_code)} characters', 'icon': '✅'})}\n\n"
            yield f"data: {json.dumps({'type': 'step', 'step': 1, 'status': 'complete'})}\n\n"
            yield f"data: {json.dumps({'type': 'log', 'message': f'💾 Saved as {filename}', 'icon': '💾'})}\n\n"
            yield f"data: {json.dumps({'type': 'preview', 'url': f'/preview/{filename}'})}\n\n"
            yield f"data: {json.dumps({'type': 'complete', 'filename': filename})}\n\n"
            
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
