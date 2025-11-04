"""
Autonomous Planner - Multi-step task execution with self-correction
"""
import asyncio
from typing import List, Dict, Optional
from enum import Enum
from dataclasses import dataclass
from datetime import datetime


class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"


@dataclass
class Task:
    """Individual task in the plan"""
    id: int
    description: str
    status: TaskStatus
    dependencies: List[int]
    result: Optional[str] = None
    error: Optional[str] = None
    retries: int = 0
    max_retries: int = 3


class AutonomousPlanner:
    """Plan and execute multi-step projects autonomously"""
    
    def __init__(self):
        self.tasks: List[Task] = []
        self.execution_log: List[Dict] = []
    
    def create_plan(self, objective: str, language: str) -> List[Task]:
        """Break down objective into actionable tasks"""
        
        # Analyze objective to create task breakdown
        tasks = []
        
        if "full-stack" in objective.lower() or "web app" in objective.lower():
            tasks = [
                Task(1, "Design database schema", TaskStatus.PENDING, []),
                Task(2, "Create backend API endpoints", TaskStatus.PENDING, [1]),
                Task(3, "Build frontend UI", TaskStatus.PENDING, []),
                Task(4, "Connect frontend to backend", TaskStatus.PENDING, [2, 3]),
                Task(5, "Add authentication", TaskStatus.PENDING, [2]),
                Task(6, "Implement error handling", TaskStatus.PENDING, [2, 3]),
                Task(7, "Add tests", TaskStatus.PENDING, [2, 3, 4])
            ]
        elif "api" in objective.lower():
            tasks = [
                Task(1, "Define API endpoints", TaskStatus.PENDING, []),
                Task(2, "Implement data models", TaskStatus.PENDING, []),
                Task(3, "Create route handlers", TaskStatus.PENDING, [1, 2]),
                Task(4, "Add validation", TaskStatus.PENDING, [3]),
                Task(5, "Implement authentication", TaskStatus.PENDING, [3]),
                Task(6, "Add error handling", TaskStatus.PENDING, [3]),
                Task(7, "Write tests", TaskStatus.PENDING, [3, 4, 5])
            ]
        elif "automation" in objective.lower() or "script" in objective.lower():
            tasks = [
                Task(1, "Define automation workflow", TaskStatus.PENDING, []),
                Task(2, "Implement core logic", TaskStatus.PENDING, [1]),
                Task(3, "Add error handling", TaskStatus.PENDING, [2]),
                Task(4, "Add logging", TaskStatus.PENDING, [2]),
                Task(5, "Create configuration", TaskStatus.PENDING, [2]),
                Task(6, "Add tests", TaskStatus.PENDING, [2, 3, 4])
            ]
        else:
            # Generic task breakdown
            tasks = [
                Task(1, "Analyze requirements", TaskStatus.PENDING, []),
                Task(2, "Design solution architecture", TaskStatus.PENDING, [1]),
                Task(3, "Implement core functionality", TaskStatus.PENDING, [2]),
                Task(4, "Add error handling", TaskStatus.PENDING, [3]),
                Task(5, "Optimize performance", TaskStatus.PENDING, [3]),
                Task(6, "Add documentation", TaskStatus.PENDING, [3]),
                Task(7, "Create tests", TaskStatus.PENDING, [3, 4])
            ]
        
        self.tasks = tasks
        return tasks
    
    def get_next_task(self) -> Optional[Task]:
        """Get next executable task (dependencies met)"""
        for task in self.tasks:
            if task.status == TaskStatus.PENDING:
                # Check if all dependencies are completed
                dependencies_met = all(
                    self.tasks[dep_id - 1].status == TaskStatus.COMPLETED
                    for dep_id in task.dependencies
                )
                if dependencies_met:
                    return task
        return None
    
    async def execute_task(self, task: Task, executor_func) -> bool:
        """Execute a single task with retry logic"""
        task.status = TaskStatus.IN_PROGRESS
        
        self.log_event({
            "task_id": task.id,
            "event": "started",
            "description": task.description,
            "timestamp": datetime.now().isoformat()
        })
        
        try:
            # Execute task using provided executor function
            result = await executor_func(task.description)
            
            task.result = result
            task.status = TaskStatus.COMPLETED
            
            self.log_event({
                "task_id": task.id,
                "event": "completed",
                "description": task.description,
                "timestamp": datetime.now().isoformat()
            })
            
            return True
        
        except Exception as e:
            task.error = str(e)
            task.retries += 1
            
            if task.retries < task.max_retries:
                task.status = TaskStatus.RETRYING
                self.log_event({
                    "task_id": task.id,
                    "event": "retrying",
                    "error": str(e),
                    "retry_count": task.retries,
                    "timestamp": datetime.now().isoformat()
                })
                
                # Retry after brief delay
                await asyncio.sleep(2)
                return await self.execute_task(task, executor_func)
            else:
                task.status = TaskStatus.FAILED
                self.log_event({
                    "task_id": task.id,
                    "event": "failed",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
                return False
    
    def log_event(self, event: Dict):
        """Log execution event"""
        self.execution_log.append(event)
    
    def get_progress(self) -> Dict:
        """Get current execution progress"""
        total = len(self.tasks)
        completed = sum(1 for t in self.tasks if t.status == TaskStatus.COMPLETED)
        failed = sum(1 for t in self.tasks if t.status == TaskStatus.FAILED)
        in_progress = sum(1 for t in self.tasks if t.status == TaskStatus.IN_PROGRESS)
        
        return {
            "total_tasks": total,
            "completed": completed,
            "failed": failed,
            "in_progress": in_progress,
            "progress_percentage": (completed / total * 100) if total > 0 else 0,
            "tasks": [
                {
                    "id": t.id,
                    "description": t.description,
                    "status": t.status.value,
                    "error": t.error
                }
                for t in self.tasks
            ]
        }
    
    def analyze_failures(self) -> Dict:
        """Analyze failed tasks and suggest corrections"""
        failed_tasks = [t for t in self.tasks if t.status == TaskStatus.FAILED]
        
        suggestions = []
        for task in failed_tasks:
            suggestions.append({
                "task_id": task.id,
                "description": task.description,
                "error": task.error,
                "suggestion": f"Review dependencies and retry with adjusted approach"
            })
        
        return {
            "failed_count": len(failed_tasks),
            "suggestions": suggestions
        }
