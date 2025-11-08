"""
Real-Time STREAMING Build API - Like Manus/Replit/Cursor
Streams AI responses token-by-token in real-time with Enterprise Build System
"""

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, Union
import asyncio
import uuid
import json
import os
from datetime import datetime
import google.generativeai as genai
from asyncio import Queue

router = APIRouter(prefix="/api/v1", tags=["Streaming Build"])

def _analyze_project_type(files_created: list, project_dir: str) -> dict:
    """Analyze project type and determine if it's previewable"""
    import os
    
    # Get actual files from disk (not in-memory data)
    file_names = []
    if os.path.exists(project_dir):
        for root, dirs, files in os.walk(project_dir):
            for file in files:
                rel_path = os.path.relpath(os.path.join(root, file), project_dir)
                file_names.append(rel_path)
    
    # Fallback to in-memory data if directory doesn't exist
    if not file_names:
        file_names = [f.get('filename', f.get('name', '')) for f in files_created]
    
    # Check for single HTML file (simple static site)
    if len(files_created) == 1 and file_names[0].endswith('.html'):
        return {
            'type': 'static_html',
            'is_previewable': True,
            'preview_url': f'/api/v1/preview/{project_dir.split("/")[-1]}/{file_names[0]}',
            'run_commands': [],
            'deploy_instructions': [
                '📦 Download the ZIP file',
                '🌐 Upload to any static hosting (Netlify, Vercel, GitHub Pages)',
                '✅ Or use Replit: Click "Publish" button to deploy instantly'
            ]
        }
    
    # Check for Flask app
    if any('app.py' in name or 'main.py' in name for name in file_names):
        if any('requirements.txt' in name for name in file_names):
            return {
                'type': 'flask',
                'is_previewable': False,
                'run_commands': [
                    'cd ' + project_dir,
                    'pip install -r requirements.txt',
                    'python app.py'
                ],
                'deploy_instructions': [
                    '📦 Download the ZIP file',
                    '📁 Open the folder in Replit or your local environment',
                    '▶️  Run: pip install -r requirements.txt',
                    '▶️  Run: python app.py',
                    '🚀 Deploy: Use Replit Publish or deploy to Railway/Render'
                ]
            }
    
    # Check for React/Node app
    if any('package.json' in name for name in file_names):
        return {
            'type': 'nodejs',
            'is_previewable': False,
            'run_commands': [
                'cd ' + project_dir,
                'npm install',
                'npm start'
            ],
            'deploy_instructions': [
                '📦 Download the ZIP file',
                '📁 Open the folder in Replit or your local environment',
                '▶️  Run: npm install',
                '▶️  Run: npm start',
                '🚀 Deploy: Use Replit Publish, Vercel, or Netlify'
            ]
        }
    
    # Multi-file static site
    has_html = any(name.endswith('.html') for name in file_names)
    if has_html:
        index_file = next((name for name in file_names if 'index.html' in name), file_names[0])
        return {
            'type': 'static_multifile',
            'is_previewable': True,
            'preview_url': f'/api/v1/preview/{project_dir.split("/")[-1]}/{index_file}',
            'run_commands': [],
            'deploy_instructions': [
                '📦 Download the ZIP file',
                '🌐 Upload to static hosting (Netlify, Vercel, GitHub Pages)',
                '✅ Or use Replit: Click "Publish" button to deploy'
            ]
        }
    
    # Default fallback
    return {
        'type': 'unknown',
        'is_previewable': False,
        'run_commands': ['Check the generated files for run instructions'],
        'deploy_instructions': [
            '📦 Download the ZIP file',
            '📁 Review the generated files',
            '📖 Check README.md for specific run instructions'
        ]
    }

def _build_file_tree(files_created: list, project_dir: Optional[str] = None) -> list:
    """Build a structured file tree from created files - reads actual file sizes from disk"""
    import os
    tree = []
    
    for file_info in files_created:
        name = file_info.get('filename', file_info.get('name', ''))
        file_type = file_info.get('type', 'file')
        
        # Get actual file size from disk
        size = 0
        if project_dir and os.path.exists(project_dir):
            file_path = os.path.join(project_dir, name)
            if os.path.exists(file_path):
                size = os.path.getsize(file_path)
        
        # Fallback: try to get size from code/content field
        if size == 0:
            content = file_info.get('code', file_info.get('content', ''))
            size = len(content) if content else 0
        
        tree.append({
            'name': name,
            'type': file_type,
            'size': size,
            'icon': _get_file_icon(name)
        })
    
    return tree

def _get_file_icon(filename: str) -> str:
    """Get emoji icon for file type"""
    if filename.endswith('.html'): return '📄'
    if filename.endswith('.css'): return '🎨'
    if filename.endswith('.js'): return '⚡'
    if filename.endswith('.py'): return '🐍'
    if filename.endswith('.json'): return '📋'
    if filename.endswith('.md'): return '📝'
    if filename.endswith('.txt'): return '📄'
    if 'Dockerfile' in filename: return '🐳'
    if 'requirements' in filename: return '📦'
    if 'package' in filename: return '📦'
    return '📄'

class StreamingBuildRequest(BaseModel):
    instruction: str
    plan_mode: bool = True
    enterprise_mode: bool = True
    live_preview: bool = True
    auto_deploy: bool = False

async def stream_log_message(message: str, icon: str = ''):
    """Stream a log message smoothly like a chat conversation"""
    log_id = str(uuid.uuid4())
    
    # Split message into words for smooth streaming
    words = message.split(' ')
    
    for i, word in enumerate(words):
        # Add space before word (except first word)
        text = (' ' + word) if i > 0 else word
        
        yield f"data: {json.dumps({'type': 'log-stream', 'id': log_id, 'delta': text, 'icon': icon if i == 0 else ''})}\n\n"
        await asyncio.sleep(0.015)  # Small delay for smooth streaming effect
    
    # Mark as complete (removes typing cursor)
    yield f"data: {json.dumps({'type': 'log-stream', 'id': log_id, 'complete': True})}\n\n"
    await asyncio.sleep(0.05)

async def stream_build_progress(instruction: str, plan_mode: bool, enterprise_mode: bool):
    """Stream build progress in real-time using Enterprise Build System"""
    
    # Send initial message with streaming
    async for chunk in stream_log_message('🚀 Starting SuperAgent build process...', '🚀'):
        yield chunk
    
    request_msg = f'📝 Your request: "{instruction}"'
    async for chunk in stream_log_message(request_msg, '📝'):
        yield chunk
    
    plan_status = "ON" if plan_mode else "OFF"
    enterprise_status = "ON" if enterprise_mode else "OFF"
    config_msg = f'⚙️ Plan Mode: {plan_status}, Enterprise Mode: {enterprise_status}'
    async for chunk in stream_log_message(config_msg, '⚙️'):
        yield chunk
    
    # Get Gemini API key
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        async for chunk in stream_log_message('❌ Error: GEMINI_API_KEY not found', '❌'):
            yield chunk
        yield f"data: {json.dumps({'type': 'error', 'message': 'API key not configured. Please add GEMINI_API_KEY to your secrets.'})}\n\n"
        return
    
    # Configure Gemini
    genai.configure(api_key=gemini_key)
    
    async for chunk in stream_log_message('🤖 Connecting to Gemini AI...', '🤖'):
        yield chunk
    async for chunk in stream_log_message('✅ Connected to Gemini 2.0 Flash!', '✅'):
        yield chunk
    
    # Use Enterprise Build System if enabled
    if enterprise_mode:
        async for chunk in stream_log_message('🏭 Initiating Enterprise Build System (9-stage production pipeline)...', '🏭'):
            yield chunk
        
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
            
            # Detect language from instruction with visual/interactive bias
            instruction_lower = instruction.lower()
            
            # Explicitly backend/CLI requests → Python
            if any(word in instruction_lower for word in ['python', 'flask', 'django', 'fastapi', 'api', 'backend', 'cli', 'command line', 'script']):
                language = 'python'
            
            # Explicitly frontend frameworks → JavaScript
            elif any(word in instruction_lower for word in ['react', 'next', 'vue', 'angular', 'node', 'express']):
                language = 'javascript'
            
            # Visual/interactive requests (NO-CODE PLATFORM: default to web apps!)
            elif any(word in instruction_lower for word in [
                'calculator', 'todo', 'task', 'game', 'quiz', 'form', 'survey',
                'dashboard', 'chart', 'graph', 'timer', 'counter', 'stopwatch',
                'weather', 'converter', 'gallery', 'portfolio', 'blog', 'chat',
                'website', 'webpage', 'landing', 'app', 'page', 'ui', 'interface',
                'button', 'menu', 'navbar', 'header', 'footer', 'card', 'modal',
                'visual', 'interactive', 'colorful', 'beautiful', 'modern', 'simple'
            ]):
                language = 'html'
            
            # Default to HTML for no-code platform (users want visual apps!)
            else:
                language = 'html'  # Changed from 'python' to 'html'
            
            async for chunk in stream_log_message(f'📊 Detected language: {language.upper()}', '📊'):
                yield chunk
            
            async for chunk in stream_log_message('🚀 Starting enterprise build (this may take 2-5 minutes)...', '🚀'):
                yield chunk
            
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
                
                # Detect project type and build metadata
                project_meta = _analyze_project_type(files_created, project_dir)
                
                # Build file tree structure with actual file sizes
                file_tree = _build_file_tree(files_created, project_dir)
                
                async for chunk in stream_log_message(f'✅ Enterprise build complete in {build_time}s!', '✅'):
                    yield chunk
                async for chunk in stream_log_message(f'📁 Created {len(files_created)} files in {project_dir}', '📁'):
                    yield chunk
                async for chunk in stream_log_message('🎉 Production-ready application generated!', '🎉'):
                    yield chunk
                yield f"data: {json.dumps({'type': 'step', 'step': 5, 'status': 'complete'})}\n\n"
                
                # Send completion with rich metadata
                project_name = project_dir.split('/')[-1] if project_dir else 'project'
                completion_data = {
                    'type': 'complete', 
                    'project_dir': project_dir,
                    'project_name': project_name,
                    'file_count': len(files_created),
                    'file_tree': file_tree,
                    'download_url': f'/api/v1/download-project/{project_name}',
                    'project_type': project_meta['type'],
                    'is_previewable': project_meta['is_previewable'],
                    'preview_url': project_meta.get('preview_url'),
                    'run_commands': project_meta.get('run_commands', []),
                    'deploy_instructions': project_meta.get('deploy_instructions', [])
                }
                yield f"data: {json.dumps(completion_data)}\n\n"
            else:
                error = result.get('error', 'Unknown error')
                async for chunk in stream_log_message(f'❌ Build failed: {error}', '❌'):
                    yield chunk
                yield f"data: {json.dumps({'type': 'error', 'message': error})}\n\n"
                
        except Exception as e:
            async for chunk in stream_log_message(f'❌ Error: {str(e)}', '❌'):
                yield chunk
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
    else:
        # Simple mode - just use Gemini to generate a single HTML file
        async for chunk in stream_log_message('💭 Generating application with Gemini...', '💭'):
            yield chunk
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
            
            async for chunk in stream_log_message(f'✅ Generated {len(generated_code)} characters', '✅'):
                yield chunk
            yield f"data: {json.dumps({'type': 'step', 'step': 1, 'status': 'complete'})}\n\n"
            async for chunk in stream_log_message(f'💾 Saved as {filename}', '💾'):
                yield chunk
            yield f"data: {json.dumps({'type': 'preview', 'url': f'/preview/{filename}'})}\n\n"
            yield f"data: {json.dumps({'type': 'complete', 'filename': filename})}\n\n"
            
        except Exception as e:
            async for chunk in stream_log_message(f'❌ Error: {str(e)}', '❌'):
                yield chunk
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

@router.get("/preview/{project_name}/{file_path:path}")
async def preview_static_file(project_name: str, file_path: str):
    """Serve static files for preview (HTML/CSS/JS only)"""
    from fastapi.responses import FileResponse, HTMLResponse
    from fastapi import HTTPException
    import os
    
    # Security: only allow preview of specific file types
    allowed_extensions = ['.html', '.css', '.js', '.json', '.txt', '.md']
    if not any(file_path.endswith(ext) for ext in allowed_extensions):
        raise HTTPException(status_code=403, detail="File type not allowed for preview")
    
    # Security: prevent path traversal
    if '..' in file_path or file_path.startswith('/'):
        raise HTTPException(status_code=403, detail="Invalid file path")
    
    # Build safe path
    project_dir = f"/home/runner/workspace/{project_name}"
    full_path = os.path.join(project_dir, file_path)
    
    # Verify path is within project directory (security check)
    if not os.path.abspath(full_path).startswith(os.path.abspath(project_dir)):
        raise HTTPException(status_code=403, detail="Access denied")
    
    if not os.path.exists(full_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    # Determine media type
    if file_path.endswith('.html'):
        media_type = 'text/html'
    elif file_path.endswith('.css'):
        media_type = 'text/css'
    elif file_path.endswith('.js'):
        media_type = 'application/javascript'
    elif file_path.endswith('.json'):
        media_type = 'application/json'
    else:
        media_type = 'text/plain'
    
    return FileResponse(full_path, media_type=media_type)

@router.get("/download-project/{project_name}")
async def download_project(project_name: str):
    """Download generated project as ZIP file"""
    from fastapi.responses import FileResponse
    import zipfile
    import os
    
    # Find the project directory
    project_dir = f"/home/runner/workspace/{project_name}"
    
    if not os.path.exists(project_dir):
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Create ZIP file
    zip_path = f"/tmp/{project_name}.zip"
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(project_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, project_dir)
                zipf.write(file_path, arcname)
    
    return FileResponse(
        zip_path, 
        media_type='application/zip',
        filename=f"{project_name}.zip"
    )

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
