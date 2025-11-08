"""
Interactive Chat Streaming API - Chat with AI during builds
Provides real-time conversational responses while builds are running
"""

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import asyncio
import json
import os
import google.generativeai as genai

router = APIRouter(prefix="/api/v1", tags=["Chat"])

class ChatRequest(BaseModel):
    message: str

async def stream_chat_response(message: str):
    """Stream AI chat response word-by-word - FULLY NON-BLOCKING"""
    
    try:
        # Get Gemini API key
        gemini_key = os.getenv("GEMINI_API_KEY")
        if not gemini_key:
            yield f"data: {json.dumps({'type': 'text', 'content': 'Sorry, AI is not configured.'})}\n\n"
            yield f"data: {json.dumps({'type': 'complete'})}\n\n"
            return
        
        # Configure Gemini
        genai.configure(api_key=gemini_key)
        
        # Create a helpful AI assistant persona
        system_prompt = """You are a helpful AI assistant helping users while their app is being built. 
You should:
- Answer questions about app development, coding, features, design, deployment
- Give brief, helpful, friendly responses (2-3 sentences max)
- Be encouraging and supportive
- If asked about the build status, remind them to check the build log panel on the left
- Keep responses conversational and natural

Keep all responses SHORT and helpful - this is a quick chat during a build!"""
        
        # Generate response using Gemini STREAMING API
        model = genai.GenerativeModel('gemini-2.0-flash')
        full_prompt = f"{system_prompt}\n\nUser: {message}\nAssistant:"
        
        # Create queue for thread-safe communication
        from asyncio import Queue
        chunk_queue = Queue()
        
        # Capture the running event loop for cross-thread communication
        loop = asyncio.get_running_loop()
        
        def generate_in_thread(event_loop):
            """Run ENTIRE Gemini streaming iteration in thread (non-blocking)"""
            try:
                # Generate with streaming enabled
                response_stream = model.generate_content(full_prompt, stream=True)
                
                # Iterate and push chunks to queue
                for chunk in response_stream:
                    if hasattr(chunk, 'text') and chunk.text:
                        # Put chunk in queue for async processing (thread-safe)
                        asyncio.run_coroutine_threadsafe(
                            chunk_queue.put(chunk.text),
                            event_loop
                        )
                
                # Signal completion
                asyncio.run_coroutine_threadsafe(
                    chunk_queue.put(None),
                    event_loop
                )
            except Exception as e:
                # Put error in queue
                asyncio.run_coroutine_threadsafe(
                    chunk_queue.put({'error': str(e)}),
                    event_loop
                )
        
        # Start thread as background task (don't await - run concurrently)
        asyncio.create_task(asyncio.to_thread(generate_in_thread, loop))
        
        # Stream chunks from queue as they arrive (non-blocking)
        while True:
            chunk_text = await chunk_queue.get()
            
            # Check for completion signal
            if chunk_text is None:
                break
            
            # Check for error
            if isinstance(chunk_text, dict) and 'error' in chunk_text:
                raise Exception(chunk_text['error'])
            
            # Stream the chunk word-by-word for smooth effect
            words = chunk_text.split()
            for word in words:
                yield f"data: {json.dumps({'type': 'text', 'content': word + ' '})}\n\n"
                await asyncio.sleep(0.02)  # Small delay for smooth streaming
        
        # Mark as complete
        yield f"data: {json.dumps({'type': 'complete'})}\n\n"
        
    except Exception as e:
        print(f"Chat error: {str(e)}")
        yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

@router.post("/chat-stream")
async def chat_stream(request: ChatRequest):
    """Stream conversational AI responses during builds"""
    return StreamingResponse(
        stream_chat_response(request.message),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
