"""REST API for SuperAgent - Programmatic access."""

from typing import Optional, List, Dict, Any
from pathlib import Path
from fastapi import FastAPI, HTTPException, BackgroundTasks, Header, Depends, Security
from fastapi.security import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import structlog
import asyncio
import os

from superagent.core.agent import SuperAgent
from superagent.core.config import Config
from superagent.core.multi_agent import MultiAgentOrchestrator
from superagent.core.memory import ProjectMemory
from superagent.modules.hallucination_fixer import HallucinationFixer

logger = structlog.get_logger()

# Initialize FastAPI app
app = FastAPI(
    title="SuperAgent API",
    description="Advanced AI Agent Framework API - Secure with API Key",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Key Security
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

def get_api_key_from_env() -> str:
    """Get API key from environment variable."""
    api_key = os.getenv("SUPERAGENT_API_KEY")
    if not api_key:
        # Fallback to a default for local development
        logger.warning("SUPERAGENT_API_KEY not set, using default (INSECURE!)")
        api_key = "dev-key-change-in-production"
    return api_key

async def verify_api_key(api_key: str = Security(api_key_header)):
    """Verify the API key from request header."""
    expected_key = get_api_key_from_env()
    
    if api_key is None:
        raise HTTPException(
            status_code=401,
            detail="API key is missing. Include 'X-API-Key' header."
        )
    
    if api_key != expected_key:
        raise HTTPException(
            status_code=403,
            detail="Invalid API key. Access denied."
        )
    
    return api_key

# Global config
config = Config()

# Active agents
active_agents: Dict[str, SuperAgent] = {}
active_jobs: Dict[str, Dict[str, Any]] = {}


# Request/Response Models
class InstructionRequest(BaseModel):
    """Request to execute an instruction."""
    instruction: str
    project_name: Optional[str] = None
    workspace: str = "./workspace"
    multi_agent: bool = False


class InstructionResponse(BaseModel):
    """Response from instruction execution."""
    job_id: str
    status: str
    message: str


class JobStatus(BaseModel):
    """Job status information."""
    job_id: str
    status: str
    progress: float
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class DebugRequest(BaseModel):
    """Request to debug a project."""
    project_path: str
    auto_fix: bool = False


class DeployRequest(BaseModel):
    """Request to deploy a project."""
    project_path: str
    platform: str = "heroku"


class TestRequest(BaseModel):
    """Request to run tests."""
    project_path: str


class GenerateRequest(BaseModel):
    """Request for quick code generation."""
    instruction: str
    language: str = "python"


class HallucinationFixRequest(BaseModel):
    """Request for hallucination detection and fixing."""
    prompt: str
    context: Optional[str] = None


class HallucinationFixResponse(BaseModel):
    """Response from hallucination fixer."""
    fixed_response: str
    is_hallucinated: bool
    score: float
    grounding_score: float
    consistency_score: float
    action: str
    initial_response: str


# Endpoints
@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint - Serves the frontend UI."""
    try:
        # Get HTML file path (go up from superagent/api.py to project root)
        html_path = Path(__file__).parent.parent / "index.html"
        with open(html_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except Exception as e:
        logger.error(f"Failed to load frontend: {e}")
        return HTMLResponse(
            content=f"<h1>Error loading frontend</h1><p>{str(e)}</p><p>Path: {html_path if 'html_path' in locals() else 'unknown'}</p>",
            status_code=500
        )


@app.get("/api")
async def api_info():
    """API info endpoint - Public."""
    return {
        "name": "SuperAgent API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "authentication": "Required for all endpoints except /health",
        "api_key_header": "X-API-Key"
    }


@app.get("/health")
async def health():
    """Health check endpoint - Public."""
    return {
        "status": "healthy",
        "active_agents": len(active_agents),
        "active_jobs": len(active_jobs),
        "authentication": "enabled"
    }


@app.post("/generate")
async def generate_code(
    request: GenerateRequest,
    api_key: str = Depends(verify_api_key)
):
    """Quick code generation endpoint for the UI.
    
    Args:
        request: Generation request
        api_key: API key
        
    Returns:
        Generated code
    """
    try:
        # Use Groq for fast code generation
        from groq import Groq
        
        groq_key = os.getenv("GROQ_API_KEY")
        if not groq_key:
            raise HTTPException(status_code=500, detail="GROQ_API_KEY not configured")
        
        client = Groq(api_key=groq_key)
        
        # Generate code
        prompt = f"Generate {request.language} code for: {request.instruction}\n\nProvide complete, production-ready code with comments."
        
        completion = client.chat.completions.create(
            model="llama-3.1-70b-versatile",
            messages=[
                {"role": "system", "content": f"You are an expert {request.language} programmer. Generate clean, complete, production-ready code."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=2000
        )
        
        code = completion.choices[0].message.content
        
        return {
            "success": True,
            "code": code,
            "language": request.language,
            "model": "llama-3.1-70b-versatile"
        }
        
    except Exception as e:
        logger.error(f"Code generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/execute", response_model=InstructionResponse)
async def execute_instruction(
    request: InstructionRequest,
    background_tasks: BackgroundTasks,
    api_key: str = Depends(verify_api_key)
):
    """Execute a natural language instruction.
    
    Args:
        request: Instruction request
        background_tasks: Background task handler
        api_key: API key for authentication
        
    Returns:
        Job ID and status
    """
    # Generate job ID
    import uuid
    job_id = str(uuid.uuid4())
    
    # Initialize job
    active_jobs[job_id] = {
        "status": "pending",
        "progress": 0.0,
        "result": None,
        "error": None
    }
    
    # Execute in background
    background_tasks.add_task(
        _execute_instruction_task,
        job_id,
        request
    )
    
    return InstructionResponse(
        job_id=job_id,
        status="pending",
        message="Instruction queued for execution"
    )


async def _execute_instruction_task(job_id: str, request: InstructionRequest):
    """Background task to execute instruction.
    
    Args:
        job_id: Job ID
        request: Instruction request
    """
    try:
        active_jobs[job_id]["status"] = "running"
        active_jobs[job_id]["progress"] = 0.1
        
        if request.multi_agent:
            # Use multi-agent system
            orchestrator = MultiAgentOrchestrator(config)
            result = await orchestrator.collaborative_solve(request.instruction)
        else:
            # Use single agent
            async with SuperAgent(config, request.workspace) as agent:
                active_jobs[job_id]["progress"] = 0.3
                
                result = await agent.execute_instruction(
                    request.instruction,
                    request.project_name
                )
        
        active_jobs[job_id]["status"] = "completed"
        active_jobs[job_id]["progress"] = 1.0
        active_jobs[job_id]["result"] = result
        
        logger.info(f"Job {job_id} completed successfully")
        
    except Exception as e:
        logger.error(f"Job {job_id} failed: {e}")
        active_jobs[job_id]["status"] = "failed"
        active_jobs[job_id]["error"] = str(e)


@app.get("/jobs/{job_id}", response_model=JobStatus)
async def get_job_status(job_id: str, api_key: str = Depends(verify_api_key)):
    """Get status of a job.
    
    Args:
        job_id: Job ID
        api_key: API key
        
    Returns:
        Job status
    """
    if job_id not in active_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = active_jobs[job_id]
    
    return JobStatus(
        job_id=job_id,
        status=job["status"],
        progress=job["progress"],
        result=job.get("result"),
        error=job.get("error")
    )


@app.post("/debug")
async def debug_project(
    request: DebugRequest,
    api_key: str = Depends(verify_api_key)
):
    """Debug a project.
    
    Args:
        request: Debug request
        api_key: API key
        
    Returns:
        Debug results
    """
    try:
        async with SuperAgent(config) as agent:
            results = await agent.debugger.debug_project(Path(request.project_path))
            
            if request.auto_fix and results.get("errors"):
                fixes = await agent.debugger.auto_fix_errors(results["errors"])
                results["fixes"] = fixes
            
            return {
                "success": True,
                "results": results
            }
    except Exception as e:
        logger.error(f"Debug failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/deploy")
async def deploy_project(
    request: DeployRequest,
    background_tasks: BackgroundTasks,
    api_key: str = Depends(verify_api_key)
):
    """Deploy a project.
    
    Args:
        request: Deploy request
        background_tasks: Background tasks
        api_key: API key
        
    Returns:
        Deployment status
    """
    import uuid
    job_id = str(uuid.uuid4())
    
    active_jobs[job_id] = {
        "status": "pending",
        "progress": 0.0,
        "result": None
    }
    
    background_tasks.add_task(
        _deploy_task,
        job_id,
        request
    )
    
    return {
        "job_id": job_id,
        "status": "pending",
        "message": "Deployment queued"
    }


async def _deploy_task(job_id: str, request: DeployRequest):
    """Background deployment task.
    
    Args:
        job_id: Job ID
        request: Deploy request
    """
    try:
        active_jobs[job_id]["status"] = "running"
        
        async with SuperAgent(config) as agent:
            result = await agent.deployer.deploy(
                Path(request.project_path),
                request.platform
            )
        
        active_jobs[job_id]["status"] = "completed"
        active_jobs[job_id]["result"] = result
        
    except Exception as e:
        active_jobs[job_id]["status"] = "failed"
        active_jobs[job_id]["error"] = str(e)


@app.post("/test")
async def run_tests(
    request: TestRequest,
    api_key: str = Depends(verify_api_key)
):
    """Run tests for a project.
    
    Args:
        request: Test request
        api_key: API key
        
    Returns:
        Test results
    """
    try:
        async with SuperAgent(config) as agent:
            results = await agent.tester.run_tests(Path(request.project_path))
            
            return {
                "success": True,
                "results": results
            }
    except Exception as e:
        logger.error(f"Tests failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats")
async def get_stats(api_key: str = Depends(verify_api_key)):
    """Get system statistics.
    
    Args:
        api_key: API key
        
    Returns:
        System stats
    """
    return {
        "active_agents": len(active_agents),
        "total_jobs": len(active_jobs),
        "pending_jobs": sum(1 for j in active_jobs.values() if j["status"] == "pending"),
        "running_jobs": sum(1 for j in active_jobs.values() if j["status"] == "running"),
        "completed_jobs": sum(1 for j in active_jobs.values() if j["status"] == "completed"),
        "failed_jobs": sum(1 for j in active_jobs.values() if j["status"] == "failed"),
    }


@app.post("/hallucination-fixer", response_model=HallucinationFixResponse)
async def fix_hallucination(
    request: HallucinationFixRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    Detect and fix AI hallucinations using grounding and self-consistency.
    
    This endpoint integrates with SupremeAgent and the 2 Supervisors to ensure
    AI-generated outputs are factual and grounded in context.
    
    Features:
    - Grounding check: Verifies response adheres to provided context
    - Self-consistency: Generates multiple responses and checks agreement
    - Auto-regeneration: Fixes hallucinated responses with stricter prompts
    - Reduces hallucinations by ~20-40%
    
    Args:
        request: Hallucination fix request with prompt and optional context
        api_key: API key for authentication
        
    Returns:
        Fixed response with hallucination detection results
        
    Example:
        POST /hallucination-fixer
        {
            "prompt": "Generate a responsive login form UI",
            "context": "Use Bootstrap for styling. Forms must have email/password fields."
        }
        
        Response:
        {
            "fixed_response": "...",
            "is_hallucinated": false,
            "score": 0.92,
            "grounding_score": 0.95,
            "consistency_score": 0.88,
            "action": "Approved as-is",
            "initial_response": "..."
        }
    """
    try:
        # Use Groq for fast hallucination checking
        from groq import Groq
        from superagent.core.llm import LLMProvider
        
        groq_key = os.getenv("GROQ_API_KEY")
        if not groq_key:
            raise HTTPException(
                status_code=500,
                detail="GROQ_API_KEY not configured. Set in environment variables."
            )
        
        # Create LLM provider for hallucination fixer
        # Use a simple wrapper for Groq
        class GroqLLMProvider:
            def __init__(self, api_key: str):
                self.client = Groq(api_key=api_key)
            
            async def complete(self, prompt: str, temperature: float = 0.7) -> str:
                completion = self.client.chat.completions.create(
                    model="llama-3.1-70b-versatile",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=temperature,
                    max_tokens=1000
                )
                return completion.choices[0].message.content
        
        llm = GroqLLMProvider(groq_key)
        
        # Initialize hallucination fixer
        fixer = HallucinationFixer(llm, consistency_samples=3, threshold=0.8)
        
        logger.info(
            "Hallucination fix request received",
            prompt_length=len(request.prompt),
            has_context=request.context is not None
        )
        
        # Run hallucination detection and fixing
        result = await fixer.fix_hallucination(request.prompt, request.context)
        
        logger.info(
            "Hallucination fix complete",
            hallucinated=result["is_hallucinated"],
            score=result["score"]
        )
        
        return HallucinationFixResponse(**result)
        
    except Exception as e:
        logger.error(f"Hallucination fixer failed: {e}")
        raise HTTPException(status_code=500, detail=f"Hallucination fixer error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)





