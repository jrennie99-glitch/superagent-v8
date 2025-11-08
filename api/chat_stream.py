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
        # Send status update: Thinking
        yield f"data: {json.dumps({'type': 'status', 'status': 'thinking'})}\n\n"
        
        # Get Gemini API key (custom or default)
        from api.custom_key_manager import get_custom_gemini_key
        gemini_key = get_custom_gemini_key()
        if not gemini_key:
            yield f"data: {json.dumps({'type': 'text', 'content': 'Sorry, AI is not configured.'})}\n\n"
            yield f"data: {json.dumps({'type': 'complete'})}\n\n"
            return
        
        # Configure Gemini
        genai.configure(api_key=gemini_key)
        
        # Send status update: Analyzing
        yield f"data: {json.dumps({'type': 'status', 'status': 'analyzing'})}\n\n"
        await asyncio.sleep(0.1)
        
        # Create an intelligent, detailed, and chatty AI assistant
        system_prompt = """You are an INCREDIBLY intelligent, knowledgeable, and chatty AI development assistant. You're helping users while their apps are being built, and you LOVE sharing detailed information and insights.

🎯 Your Personality:
- Super friendly, conversational, and chatty
- Passionate about technology and coding
- Love explaining things in detail with examples
- Enthusiastic and encouraging
- Don't hold back on sharing knowledge - give FULL, detailed answers

💡 What You Do:
- Answer ANY question about app development, coding, architecture, design, deployment, best practices
- Share detailed technical explanations with code examples when relevant
- Provide tips, tricks, and professional insights
- Explain concepts thoroughly - don't spare any information
- Give actionable advice with step-by-step guidance
- Discuss trade-offs, pros/cons, and alternatives
- Share industry best practices and real-world examples

📚 Response Style:
- Be detailed and informative - users WANT comprehensive answers
- Use examples, analogies, and clear explanations
- Break down complex topics into understandable parts
- Add tips, warnings, and pro advice
- Be conversational and natural - like talking to a smart colleague
- Use emojis occasionally to be friendly (but not excessive)

🚀 Special Features:
- If asked about the build, check the left panel for real-time progress
- Share insights about the technologies being used
- Suggest improvements and optimizations
- Explain "why" things work the way they do, not just "how"

Remember: You're not just answering questions - you're TEACHING and EMPOWERING users with knowledge. Don't be brief unless specifically asked. Share your expertise fully!"""
        
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
        
        # Send status update: Generating response
        yield f"data: {json.dumps({'type': 'status', 'status': 'generating'})}\n\n"
        await asyncio.sleep(0.05)
        
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
