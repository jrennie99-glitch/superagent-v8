"""
Build Progress Tracker for SuperAgent v8
Provides detailed, real-time progress updates like Replit/Cursor/Bolt
"""
import asyncio
from typing import Dict, List, Callable, Optional
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class BuildStage(Enum):
    """Build stages for progress tracking"""
    PLANNING = "planning"
    CODE_GENERATION = "code_generation"
    FILE_CREATION = "file_creation"
    DEPENDENCY_INSTALL = "dependency_install"
    SERVER_START = "server_start"
    TESTING = "testing"
    DEPLOYMENT = "deployment"
    COMPLETE = "complete"
    FAILED = "failed"

class BuildProgress:
    """Track and report build progress in real-time"""
    
    def __init__(self):
        self.stages: List[Dict] = []
        self.current_stage: Optional[BuildStage] = None
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.callbacks: List[Callable] = []
        self.logs: List[str] = []
    
    def start(self):
        """Start tracking build progress"""
        self.start_time = datetime.now()
        self.stages = []
        self.logs = []
        logger.info("Build progress tracking started")
    
    def add_stage(self, stage: BuildStage, message: str, status: str = "in_progress"):
        """
        Add a new build stage
        
        Args:
            stage: The build stage
            message: Descriptive message
            status: "in_progress", "complete", or "failed"
        """
        stage_data = {
            "stage": stage.value,
            "message": message,
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "elapsed_seconds": (datetime.now() - self.start_time).total_seconds() if self.start_time else 0
        }
        
        self.stages.append(stage_data)
        self.current_stage = stage
        
        # Add to logs
        emoji = {
            "in_progress": "⏳",
            "complete": "✅",
            "failed": "❌"
        }.get(status, "📋")
        
        log_message = f"{emoji} [{stage.value.upper()}] {message}"
        self.logs.append(log_message)
        logger.info(log_message)
        
        # Notify callbacks
        for callback in self.callbacks:
            try:
                callback(stage_data)
            except Exception as e:
                logger.error(f"Error in progress callback: {e}")
    
    def update_stage(self, status: str, message: Optional[str] = None):
        """Update the current stage status"""
        if self.stages:
            self.stages[-1]["status"] = status
            if message:
                self.stages[-1]["message"] = message
                self.logs.append(f"  └─ {message}")
    
    def add_log(self, message: str, level: str = "info"):
        """Add a detailed log message"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.logs.append(log_entry)
        
        if level == "error":
            logger.error(message)
        elif level == "warning":
            logger.warning(message)
        else:
            logger.info(message)
    
    def complete(self, success: bool = True):
        """Mark build as complete"""
        self.end_time = datetime.now()
        final_stage = BuildStage.COMPLETE if success else BuildStage.FAILED
        status = "complete" if success else "failed"
        
        elapsed = (self.end_time - self.start_time).total_seconds() if self.start_time else 0
        
        message = f"Build {'completed successfully' if success else 'failed'} in {elapsed:.1f}s"
        self.add_stage(final_stage, message, status)
    
    def get_summary(self) -> Dict:
        """Get build progress summary"""
        elapsed = 0
        if self.start_time:
            end = self.end_time or datetime.now()
            elapsed = (end - self.start_time).total_seconds()
        
        return {
            "stages": self.stages,
            "current_stage": self.current_stage.value if self.current_stage else None,
            "total_stages": len(self.stages),
            "completed_stages": len([s for s in self.stages if s["status"] == "complete"]),
            "failed_stages": len([s for s in self.stages if s["status"] == "failed"]),
            "elapsed_seconds": elapsed,
            "logs": self.logs,
            "is_complete": self.end_time is not None,
            "success": self.stages[-1]["status"] == "complete" if self.stages else False
        }
    
    def get_detailed_log(self) -> str:
        """Get formatted detailed log"""
        return "\n".join(self.logs)
    
    def register_callback(self, callback: Callable):
        """Register a callback for progress updates"""
        self.callbacks.append(callback)

# Global progress tracker
build_progress = BuildProgress()

# Helper functions for common build stages
async def track_planning(progress: BuildProgress, instruction: str):
    """Track architecture planning stage"""
    progress.add_stage(
        BuildStage.PLANNING,
        f"Planning architecture for: {instruction[:50]}...",
        "in_progress"
    )
    progress.add_log("Analyzing requirements")
    progress.add_log("Determining tech stack")
    progress.add_log("Creating file structure plan")

async def track_code_generation(progress: BuildProgress, code_length: int):
    """Track code generation stage"""
    progress.update_stage("complete", "Architecture planning complete")
    progress.add_stage(
        BuildStage.CODE_GENERATION,
        f"Generating code ({code_length} characters)...",
        "in_progress"
    )
    progress.add_log(f"AI generating {code_length} characters of code")
    progress.add_log("Applying best practices and patterns")

async def track_file_creation(progress: BuildProgress, files: List[str]):
    """Track file creation stage"""
    progress.update_stage("complete", f"Code generation complete ({len(files)} files)")
    progress.add_stage(
        BuildStage.FILE_CREATION,
        f"Creating {len(files)} application files...",
        "in_progress"
    )
    for file in files:
        progress.add_log(f"Creating {file}")
        await asyncio.sleep(0.1)  # Small delay for visual effect

async def track_dependencies(progress: BuildProgress, packages: List[str]):
    """Track dependency installation"""
    progress.update_stage("complete", "Files created successfully")
    progress.add_stage(
        BuildStage.DEPENDENCY_INSTALL,
        f"Installing {len(packages)} dependencies...",
        "in_progress"
    )
    for package in packages:
        progress.add_log(f"Installing {package}")
        await asyncio.sleep(0.2)

async def track_server_start(progress: BuildProgress, port: int):
    """Track server startup"""
    progress.update_stage("complete", "Dependencies installed")
    progress.add_stage(
        BuildStage.SERVER_START,
        f"Starting development server on port {port}...",
        "in_progress"
    )
    progress.add_log(f"Server listening on http://localhost:{port}")
