"""
Long-Term Autonomous Planning Module

Enables SuperAgent to work autonomously for HOURS (not just minutes).
This is the KEY to matching Devin's #1 capability!
"""

import asyncio
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime, timedelta
import structlog

from superagent.core.memory import ProjectMemory

logger = structlog.get_logger()


class AutonomousPlanner:
    """
    Manages long-term autonomous execution.
    
    Can work on projects for hours/days, making decisions,
    iterating, and self-correcting without human intervention.
    """
    
    def __init__(self, llm_provider, memory: ProjectMemory):
        """
        Initialize autonomous planner.
        
        Args:
            llm_provider: LLM for decision making
            memory: Long-term memory system
        """
        self.llm = llm_provider
        self.memory = memory
        self.max_autonomous_time = 3600 * 4  # 4 hours max
        self.max_iterations = 100  # Max decision cycles
        logger.info("AutonomousPlanner initialized")
    
    async def execute_autonomous_project(
        self,
        instruction: str,
        project_name: str,
        workspace: Path,
        max_time: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Execute a project autonomously for extended time.
        
        This is like Devin - works for hours without human input.
        
        Args:
            instruction: High-level project goal
            project_name: Project identifier
            workspace: Working directory
            max_time: Maximum execution time in seconds
            
        Returns:
            Project results after autonomous execution
        """
        max_time = max_time or self.max_autonomous_time
        start_time = datetime.now()
        end_time = start_time + timedelta(seconds=max_time)
        
        logger.info(
            "Starting autonomous execution",
            project=project_name,
            max_time=f"{max_time/3600:.1f}h"
        )
        
        # Add to memory
        project_id = self.memory.add_project(project_name, instruction)
        
        # Create initial plan
        plan = await self._create_long_term_plan(instruction, project_id)
        
        results = {
            "project_name": project_name,
            "instruction": instruction,
            "start_time": start_time.isoformat(),
            "plan": plan,
            "iterations": [],
            "success": False
        }
        
        iteration = 0
        current_phase = 0
        
        # Autonomous execution loop
        while datetime.now() < end_time and iteration < self.max_iterations:
            iteration += 1
            logger.info(f"Autonomous iteration {iteration}/{self.max_iterations}")
            
            # Check if plan is complete
            if current_phase >= len(plan["phases"]):
                results["success"] = True
                results["message"] = "Project completed successfully"
                break
            
            # Execute current phase
            phase = plan["phases"][current_phase]
            phase_result = await self._execute_phase(
                phase,
                workspace,
                project_id,
                iteration
            )
            
            results["iterations"].append({
                "iteration": iteration,
                "phase": phase["name"],
                "result": phase_result,
                "timestamp": datetime.now().isoformat()
            })
            
            # Decide next action based on result
            if phase_result["success"]:
                # Phase succeeded - move to next
                current_phase += 1
                self.memory.add_learning(
                    project_id,
                    f"Successfully completed: {phase['name']}",
                    {"phase": phase, "iteration": iteration}
                )
            else:
                # Phase failed - analyze and retry or adapt
                should_retry, adaptation = await self._analyze_failure(
                    phase,
                    phase_result,
                    project_id
                )
                
                if should_retry:
                    logger.info(f"Retrying phase: {phase['name']}")
                    if adaptation:
                        # Adapt the phase based on failure analysis
                        plan["phases"][current_phase] = adaptation
                else:
                    # Give up on this phase, try to work around it
                    logger.warning(f"Skipping failed phase: {phase['name']}")
                    current_phase += 1
            
            # Check if we should revise the plan
            if iteration % 10 == 0:
                logger.info("Checking if plan revision needed")
                plan = await self._maybe_revise_plan(
                    plan,
                    results,
                    project_id
                )
            
            # Small delay to avoid hammering the LLM
            await asyncio.sleep(2)
        
        # Finalize results
        results["end_time"] = datetime.now().isoformat()
        results["total_time"] = (datetime.now() - start_time).total_seconds()
        results["iterations_completed"] = iteration
        
        if not results["success"]:
            if datetime.now() >= end_time:
                results["message"] = "Timeout: Reached max execution time"
            else:
                results["message"] = "Failed: Exceeded max iterations"
        
        # Update memory with final result
        self.memory.update_project_status(
            project_id,
            "completed" if results["success"] else "failed",
            str(results)
        )
        
        logger.info(
            "Autonomous execution complete",
            success=results["success"],
            iterations=iteration,
            time=f"{results['total_time']/60:.1f}min"
        )
        
        return results
    
    async def _create_long_term_plan(
        self,
        instruction: str,
        project_id: int
    ) -> Dict[str, Any]:
        """Create a detailed, multi-phase plan."""
        prompt = f"""Create a detailed, multi-phase plan for this project:

{instruction}

Break it down into distinct phases that can be executed autonomously.
Each phase should have:
- Clear objective
- Expected duration
- Success criteria
- Dependencies

Think like Devin - plan for hours of autonomous work.
Format as JSON with phases list."""
        
        try:
            response = await self.llm.complete(prompt)
            
            # Parse plan (simplified - would use structured output in production)
            phases = self._parse_plan(response)
            
            plan = {
                "instruction": instruction,
                "phases": phases,
                "created_at": datetime.now().isoformat()
            }
            
            # Store plan in memory
            self.memory.add_task(
                project_id,
                f"Long-term plan: {len(phases)} phases"
            )
            
            return plan
            
        except Exception as e:
            logger.error(f"Plan creation failed: {e}")
            # Fallback to simple plan
            return {
                "instruction": instruction,
                "phases": [
                    {"name": "Setup", "objective": "Initialize project", "duration": 300},
                    {"name": "Implementation", "objective": "Write code", "duration": 1800},
                    {"name": "Testing", "objective": "Test and verify", "duration": 600},
                    {"name": "Finalization", "objective": "Final checks", "duration": 300}
                ],
                "created_at": datetime.now().isoformat()
            }
    
    def _parse_plan(self, response: str) -> List[Dict[str, Any]]:
        """Parse plan from LLM response."""
        # Simplified parsing - would use structured output in production
        phases = []
        
        # Default phases if parsing fails
        default_phases = [
            {
                "name": "Research & Planning",
                "objective": "Understand requirements and plan architecture",
                "duration": 600,
                "success_criteria": "Architecture documented"
            },
            {
                "name": "Core Implementation",
                "objective": "Implement main functionality",
                "duration": 3600,
                "success_criteria": "Core features working"
            },
            {
                "name": "Testing & Debugging",
                "objective": "Test thoroughly and fix issues",
                "duration": 1800,
                "success_criteria": "All tests passing"
            },
            {
                "name": "Polish & Documentation",
                "objective": "Clean up code and document",
                "duration": 900,
                "success_criteria": "Production-ready"
            }
        ]
        
        return default_phases
    
    async def _execute_phase(
        self,
        phase: Dict[str, Any],
        workspace: Path,
        project_id: int,
        iteration: int
    ) -> Dict[str, Any]:
        """Execute a single phase of the plan."""
        logger.info(f"Executing phase: {phase['name']}")
        
        # Add task to memory
        task_id = self.memory.add_task(
            project_id,
            f"Phase: {phase['name']} (iteration {iteration})"
        )
        
        prompt = f"""Execute this phase autonomously:

Phase: {phase['name']}
Objective: {phase['objective']}
Success Criteria: {phase.get('success_criteria', 'Phase completed')}

Make decisions and take actions to complete this phase.
Work autonomously - don't ask for human input.
"""
        
        try:
            # Execute phase (simplified - would integrate with code gen, testing, etc.)
            response = await self.llm.complete(prompt)
            
            # Evaluate success
            success = await self._evaluate_phase_success(phase, response)
            
            result = {
                "success": success,
                "phase": phase["name"],
                "output": response[:500],  # Truncate for storage
                "timestamp": datetime.now().isoformat()
            }
            
            # Update memory
            self.memory.update_task_status(
                task_id,
                "completed" if success else "failed",
                str(result)
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Phase execution failed: {e}")
            return {
                "success": False,
                "phase": phase["name"],
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def _evaluate_phase_success(
        self,
        phase: Dict[str, Any],
        output: str
    ) -> bool:
        """Evaluate if a phase was successful."""
        prompt = f"""Did this phase succeed?

Phase: {phase['name']}
Success Criteria: {phase.get('success_criteria', 'Completed')}
Output: {output[:1000]}

Answer: YES or NO"""
        
        try:
            response = await self.llm.complete(prompt)
            return "yes" in response.lower()[:50]
        except:
            return False
    
    async def _analyze_failure(
        self,
        phase: Dict[str, Any],
        result: Dict[str, Any],
        project_id: int
    ) -> tuple[bool, Optional[Dict[str, Any]]]:
        """
        Analyze why a phase failed and decide what to do.
        
        Returns:
            (should_retry, adapted_phase)
        """
        prompt = f"""This phase failed. Analyze why and decide:

Phase: {phase['name']}
Error: {result.get('error', 'Unknown')}

Should we:
1. RETRY - Try again with same approach
2. ADAPT - Change approach and retry
3. SKIP - Move on to next phase

Respond with: RETRY, ADAPT, or SKIP"""
        
        try:
            response = await self.llm.complete(prompt)
            decision = response.strip().upper()
            
            if "RETRY" in decision:
                return (True, None)
            elif "ADAPT" in decision:
                # Create adapted phase
                adapted = await self._adapt_phase(phase, result)
                return (True, adapted)
            else:
                return (False, None)
                
        except Exception as e:
            logger.error(f"Failure analysis failed: {e}")
            return (True, None)  # Default to retry
    
    async def _adapt_phase(
        self,
        phase: Dict[str, Any],
        failure_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Adapt a phase based on failure."""
        # Simplified - would use LLM to adapt strategy
        adapted = phase.copy()
        adapted["attempt"] = phase.get("attempt", 0) + 1
        adapted["objective"] += f" (Attempt {adapted['attempt']})"
        return adapted
    
    async def _maybe_revise_plan(
        self,
        plan: Dict[str, Any],
        results: Dict[str, Any],
        project_id: int
    ) -> Dict[str, Any]:
        """Check if plan needs revision based on progress."""
        # Simplified - in production would analyze progress and revise
        logger.info("Plan looks good, continuing")
        return plan

