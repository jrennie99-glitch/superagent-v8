"""
Enterprise generation endpoint to add to api.py

This provides the /generate-enterprise endpoint that uses
the enhanced code generator for high-quality output.
"""

# Add these request/response models to api.py:

class EnterpriseGenerateRequest(BaseModel):
    """Request for enterprise-quality code generation."""
    instruction: str
    app_name: str
    app_type: str = "calculator"  # calculator, dashboard, form, todo, timer
    language: str = "html"  # For web apps


class EnterpriseGenerateResponse(BaseModel):
    """Response from enterprise code generation."""
    success: bool
    app_name: str
    app_type: str
    files: Dict[str, str]
    quality_score: float
    quality_report: Dict[str, Any]
    ready_to_use: bool
    instructions: str
    error: Optional[str] = None


# Add this endpoint to api.py:

@app.post("/generate-enterprise", response_model=EnterpriseGenerateResponse)
async def generate_enterprise_app(
    request: EnterpriseGenerateRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    Generate enterprise-quality, fully functional applications.
    
    This endpoint uses the enhanced code generator that produces
    professional, working applications instead of broken prototypes.
    
    Args:
        request: Enterprise generation request
        api_key: API key for authentication
        
    Returns:
        Complete application with quality report
    """
    try:
        logger.info(f"Enterprise generation request: {request.app_type} - {request.app_name}")
        
        # Initialize components
        from superagent.core.llm import LLMProvider
        from superagent.core.cache import CacheManager
        
        # Get API key from environment
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        if not anthropic_key:
            raise HTTPException(
                status_code=500,
                detail="ANTHROPIC_API_KEY not configured. Enterprise generation requires Claude API."
            )
        
        # Initialize LLM
        llm = LLMProvider(
            api_key=anthropic_key,
            model="claude-sonnet-4-5-20250929",
            temperature=0.7,
            max_tokens=8000
        )
        
        # Initialize cache
        cache = CacheManager(
            redis_url=f"redis://{os.getenv('REDIS_HOST', 'localhost')}:{os.getenv('REDIS_PORT', '6379')}",
            cache_dir="./cache",
            ttl=3600
        )
        
        try:
            await cache.connect()
        except Exception as e:
            logger.warning(f"Redis not available, using disk cache: {e}")
        
        # Initialize enterprise generator
        generator = EnterpriseCodeGenerator(llm, cache)
        
        # Generate enterprise-quality app
        result = await generator.generate_enterprise_web_app(
            description=request.instruction,
            app_name=request.app_name,
            app_type=request.app_type
        )
        
        # Close cache
        await cache.close()
        
        # Extract quality score
        quality_score = 0
        if result.get('quality_report'):
            qr = result['quality_report']
            # Calculate overall score from components
            html_score = 100 if qr.get('html_complete') else 0
            css_score = 100 if qr.get('css_present') else 0
            js_score = 100 if qr.get('js_functional') else 0
            quality_score = (html_score + css_score + js_score) / 3
        
        return EnterpriseGenerateResponse(
            success=result.get('success', True),
            app_name=result['app_name'],
            app_type=result['app_type'],
            files=result['files'],
            quality_score=quality_score,
            quality_report=result['quality_report'],
            ready_to_use=result['ready_to_use'],
            instructions=result['instructions'],
            error=None
        )
        
    except Exception as e:
        logger.error(f"Enterprise generation failed: {e}")
        import traceback
        traceback.print_exc()
        
        return EnterpriseGenerateResponse(
            success=False,
            app_name=request.app_name,
            app_type=request.app_type,
            files={},
            quality_score=0,
            quality_report={},
            ready_to_use=False,
            instructions="",
            error=str(e)
        )


# Also add a simpler endpoint that enhances the existing /generate:

@app.post("/generate-enhanced")
async def generate_code_enhanced(
    request: GenerateRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    Enhanced code generation endpoint that uses better prompts.
    
    This is a drop-in replacement for /generate that produces
    better quality code while maintaining the same interface.
    
    Args:
        request: Generation request
        api_key: API key
        
    Returns:
        Generated code with quality improvements
    """
    try:
        # Use Anthropic Claude for better quality
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        
        if anthropic_key:
            # Use Claude for better quality
            from anthropic import Anthropic
            
            client = Anthropic(api_key=anthropic_key)
            
            # Enhanced prompt with enterprise requirements
            enhanced_prompt = f"""Generate complete, enterprise-quality {request.language} code for:

{request.instruction}

REQUIREMENTS:
- Complete, working code (no placeholders or TODOs)
- Proper error handling and validation
- Clean, well-documented code with comments
- Follow {request.language} best practices
- Include all necessary imports/dependencies
- Production-ready quality

Provide ONLY the code, no explanations."""

            message = client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=4000,
                temperature=0.7,
                messages=[
                    {
                        "role": "user",
                        "content": enhanced_prompt
                    }
                ]
            )
            
            code = message.content[0].text
            model_used = "claude-sonnet-4-5"
            
        else:
            # Fallback to Groq with enhanced prompt
            from groq import Groq
            
            groq_key = os.getenv("GROQ_API_KEY")
            if not groq_key:
                raise HTTPException(status_code=500, detail="No API keys configured")
            
            client = Groq(api_key=groq_key)
            
            enhanced_prompt = f"""Generate complete, production-ready {request.language} code for:

{request.instruction}

Requirements:
- Complete, working code
- Proper error handling
- Well-documented with comments
- Follow best practices
- No placeholders or TODOs

Provide only the code."""
            
            completion = client.chat.completions.create(
                model="llama-3.1-70b-versatile",
                messages=[
                    {"role": "system", "content": f"You are an expert {request.language} programmer. Generate clean, complete, production-ready code."},
                    {"role": "user", "content": enhanced_prompt}
                ],
                temperature=0.3,
                max_tokens=3000
            )
            
            code = completion.choices[0].message.content
            model_used = "llama-3.1-70b"
        
        # Clean up code (remove markdown if present)
        if "```" in code:
            lines = code.split('\n')
            cleaned_lines = []
            in_code_block = False
            
            for line in lines:
                if line.strip().startswith("```"):
                    in_code_block = not in_code_block
                    continue
                if in_code_block or "```" not in code:
                    cleaned_lines.append(line)
            
            code = '\n'.join(cleaned_lines).strip()
        
        return {
            "success": True,
            "code": code,
            "language": request.language,
            "model": model_used,
            "enhanced": True
        }
        
    except Exception as e:
        logger.error(f"Enhanced code generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
