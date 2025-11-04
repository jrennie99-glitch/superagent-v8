"""Multi-agent collaboration system for parallel task execution."""

import asyncio
from typing import List, Dict, Any, Optional
from enum import Enum
import structlog

from superagent.core.config import Config
from superagent.core.llm import LLMProvider

logger = structlog.get_logger()


class AgentRole(Enum):
    """Agent roles for specialization."""
    CODER = "coder"
    DEBUGGER = "debugger"
    TESTER = "tester"
    REVIEWER = "reviewer"
    ARCHITECT = "architect"
    SUPERVISOR = "supervisor"
    SUPREME_AGENT = "supreme_agent"


class SpecializedAgent:
    """Specialized agent for specific tasks."""
    
    def __init__(self, role: AgentRole, llm: LLMProvider, agent_id: int):
        """Initialize specialized agent.
        
        Args:
            role: Agent role
            llm: LLM provider
            agent_id: Unique agent ID
        """
        self.role = role
        self.llm = llm
        self.agent_id = agent_id
        self.tasks_completed = 0
        self.active = True
        
        # Role-specific prompts
        self.system_prompts = {
            AgentRole.CODER: """You are an expert software developer. Your role is to 
write clean, efficient, well-documented code following best practices.""",
            
            AgentRole.DEBUGGER: """You are an expert debugger. Your role is to identify 
and fix bugs, optimize performance, and ensure code quality.""",
            
            AgentRole.TESTER: """You are an expert QA engineer. Your role is to write 
comprehensive tests, ensure high coverage, and validate functionality.""",
            
            AgentRole.REVIEWER: """You are an expert code reviewer. Your role is to 
review code for quality, security, performance, and maintainability.""",
            
            AgentRole.ARCHITECT: """You are an expert software architect. Your role is 
to design system architecture, plan implementations, and ensure scalability.""",
            
            AgentRole.SUPERVISOR: """You are an ULTRA-FAST SUPERVISOR. Your role is to 
rapidly verify code correctness, catch critical errors, and ensure the code WORKS. 
You work in parallel with 1 other supervisor. Be FAST, EFFICIENT, and ACCURATE. 
Focus on: functionality, critical bugs, runtime errors, and deployment readiness.""",
            
            AgentRole.SUPREME_AGENT: """You are the SUPREME AGENT - The FINAL AUTHORITY. 
Your role is to review the 2 supervisors' verification and make the ULTIMATE DECISION. 
You have the HIGHEST standards and FINAL SAY on whether code is production-ready. 
You are THOROUGH, DECISIVE, and UNCOMPROMISING on quality. Only PERFECT code passes your review.
Check: correctness, reliability, security, performance, and production readiness."""
        }
    
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a task based on agent role.
        
        Args:
            task: Task dictionary
            
        Returns:
            Task result
        """
        logger.info(
            f"Agent {self.agent_id} executing task",
            role=self.role.value,
            task_type=task.get("type")
        )
        
        prompt = self._create_task_prompt(task)
        system = self.system_prompts.get(self.role, "")
        
        result = await self.llm.generate(prompt, system=system)
        
        self.tasks_completed += 1
        
        return {
            "agent_id": self.agent_id,
            "role": self.role.value,
            "task": task,
            "result": result,
            "success": True
        }
    
    def _create_task_prompt(self, task: Dict[str, Any]) -> str:
        """Create task-specific prompt.
        
        Args:
            task: Task dictionary
            
        Returns:
            Prompt string
        """
        task_type = task.get("type", "general")
        description = task.get("description", "")
        context = task.get("context", {})
        
        if self.role == AgentRole.CODER:
            return f"""Write code for the following task:

Task: {description}

Context:
{context}

Provide complete, production-ready code with error handling and documentation."""
        
        elif self.role == AgentRole.DEBUGGER:
            return f"""Debug the following issue:

Issue: {description}

Code Context:
{context}

Identify the root cause and provide a fix with explanation."""
        
        elif self.role == AgentRole.TESTER:
            return f"""Write comprehensive tests for:

Description: {description}

Code:
{context}

Provide complete test suite with edge cases."""
        
        elif self.role == AgentRole.REVIEWER:
            return f"""Review the following code:

Description: {description}

Code:
{context}

Provide detailed feedback on quality, security, and improvements."""
        
        elif self.role == AgentRole.SUPERVISOR:
            return f"""RAPIDLY VERIFY this code works correctly:

Task: {description}

Code:
{context}

Provide: 
1. WORKS (YES/NO)
2. Critical Issues (if any)
3. Deployment Ready (YES/NO)

Be FAST and EFFICIENT. Focus only on whether code WORKS."""
        
        elif self.role == AgentRole.SUPREME_AGENT:
            return f"""SUPREME AGENT FINAL REVIEW:

Task: {description}

Code & Context:
{context}

You are the FINAL AUTHORITY. Review EVERYTHING and make the ULTIMATE DECISION.

Provide:
1. APPROVED FOR PRODUCTION (YES/NO)
2. Final Assessment (comprehensive)
3. Any show-stopping issues
4. Supreme Agent Verdict

Only approve PERFECT, production-ready code. You have the final say."""
        
        else:
            return f"{description}\n\nContext: {context}"


class MultiAgentOrchestrator:
    """
    Orchestrates multiple specialized agents for parallel task execution.
    
    This enables:
    - Parallel task processing (2x+ speed improvement)
    - Specialized expertise for different task types
    - Load balancing across agents
    - Collaborative problem-solving
    """
    
    def __init__(self, config: Config, num_agents: int = 4):
        """Initialize multi-agent orchestrator.
        
        Args:
            config: Configuration
            num_agents: Number of agents to create
        """
        self.config = config
        self.num_agents = num_agents
        self.agents: List[SpecializedAgent] = []
        self.task_queue: asyncio.Queue = asyncio.Queue()
        self.results: List[Dict[str, Any]] = []
        
        # Initialize LLM provider
        self.llm = LLMProvider(
            api_key=config.anthropic_api_key,
            model=config.model.name,
            temperature=config.model.temperature,
            max_tokens=config.model.max_tokens
        )
        
        # Create specialized agents
        self._create_agents()
        
        logger.info(f"Multi-agent system initialized with {num_agents} agents")
    
    def _create_agents(self):
        """Create specialized agents with different roles."""
        roles = [
            AgentRole.CODER,
            AgentRole.DEBUGGER,
            AgentRole.TESTER,
            AgentRole.REVIEWER
        ]
        
        for i in range(self.num_agents):
            role = roles[i % len(roles)]
            agent = SpecializedAgent(role, self.llm, i)
            self.agents.append(agent)
    
    async def execute_tasks(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Execute tasks in parallel using multiple agents.
        
        Args:
            tasks: List of tasks to execute
            
        Returns:
            List of results
        """
        logger.info(f"Executing {len(tasks)} tasks with {self.num_agents} agents")
        
        # Add tasks to queue
        for task in tasks:
            await self.task_queue.put(task)
        
        # Start agent workers
        workers = [
            asyncio.create_task(self._agent_worker(agent))
            for agent in self.agents
        ]
        
        # Wait for queue to be processed
        await self.task_queue.join()
        
        # Cancel workers
        for worker in workers:
            worker.cancel()
        
        # Wait for workers to finish
        await asyncio.gather(*workers, return_exceptions=True)
        
        logger.info(f"Completed {len(self.results)} tasks")
        
        return self.results
    
    async def _agent_worker(self, agent: SpecializedAgent):
        """Worker coroutine for an agent.
        
        Args:
            agent: Agent to run
        """
        while True:
            try:
                # Get task from queue
                task = await asyncio.wait_for(
                    self.task_queue.get(),
                    timeout=1.0
                )
                
                # Execute task
                result = await agent.execute_task(task)
                self.results.append(result)
                
                # Mark task as done
                self.task_queue.task_done()
                
            except asyncio.TimeoutError:
                continue
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Agent {agent.agent_id} error: {e}")
                self.task_queue.task_done()
    
    async def collaborative_solve(self, problem: str) -> Dict[str, Any]:
        """Solve a complex problem collaboratively.
        
        Args:
            problem: Problem description
            
        Returns:
            Collaborative solution
        """
        logger.info("Starting collaborative problem solving")
        
        # Phase 1: Architecture (Architect designs solution)
        architect_task = {
            "type": "architecture",
            "description": f"Design architecture for: {problem}",
            "context": {}
        }
        
        architect_agent = next(
            (a for a in self.agents if a.role == AgentRole.CODER), 
            self.agents[0]
        )
        arch_result = await architect_agent.execute_task(architect_task)
        
        # Phase 2: Implementation (Coders implement)
        impl_tasks = [
            {
                "type": "code",
                "description": f"Implement component {i} based on architecture",
                "context": {"architecture": arch_result["result"]}
            }
            for i in range(3)
        ]
        
        impl_results = await self.execute_tasks(impl_tasks)
        
        # Phase 3: Testing (Testers write tests)
        test_tasks = [
            {
                "type": "test",
                "description": f"Write tests for implementation {i}",
                "context": {"code": result["result"]}
            }
            for i, result in enumerate(impl_results)
        ]
        
        test_results = await self.execute_tasks(test_tasks)
        
        # Phase 4: Review (Reviewers check everything)
        review_task = {
            "type": "review",
            "description": "Review complete implementation",
            "context": {
                "architecture": arch_result["result"],
                "implementations": [r["result"] for r in impl_results],
                "tests": [r["result"] for r in test_results]
            }
        }
        
        reviewer_agent = next(
            (a for a in self.agents if a.role == AgentRole.REVIEWER),
            self.agents[0]
        )
        review_result = await reviewer_agent.execute_task(review_task)
        
        return {
            "problem": problem,
            "architecture": arch_result["result"],
            "implementations": [r["result"] for r in impl_results],
            "tests": [r["result"] for r in test_results],
            "review": review_result["result"],
            "success": True
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about agent performance.
        
        Returns:
            Statistics dictionary
        """
        return {
            "total_agents": len(self.agents),
            "tasks_completed": sum(a.tasks_completed for a in self.agents),
            "agent_breakdown": [
                {
                    "agent_id": a.agent_id,
                    "role": a.role.value,
                    "tasks": a.tasks_completed
                }
                for a in self.agents
            ]
        }


class SupervisorSystem:
    """
    2-Supervisor system + SUPREME AGENT for ULTIMATE verification.
    
    Features:
    - 2 supervisors work in PARALLEL (fast verification)
    - SUPREME AGENT makes FINAL DECISION (ultimate authority)
    - ULTRA-FAST verification (< 1.5 seconds for supervisors)
    - Supreme Agent final review (< 2.5 seconds total)
    - Ensures code WORKS before deployment
    - Catches critical errors that agents miss
    - Both supervisors must approve + Supreme Agent approval required
    
    Better than Devin's single-check system! Optimized for Railway/Render deployment.
    """
    
    def __init__(self, config: Config):
        """Initialize 2-supervisor + Supreme Agent system.
        
        Args:
            config: Configuration
        """
        self.config = config
        
        # Initialize LLM provider (using fastest model)
        self.llm = LLMProvider(
            api_key=config.anthropic_api_key,
            model=config.model.name,
            temperature=0.0,  # Deterministic for consistency
            max_tokens=1000   # Short responses for speed
        )
        
        # Create 2 supervisors (optimized for speed)
        self.supervisors = [
            SpecializedAgent(AgentRole.SUPERVISOR, self.llm, i)
            for i in range(2)
        ]
        
        # Create SUPREME AGENT (final authority)
        self.supreme_agent = SpecializedAgent(AgentRole.SUPREME_AGENT, self.llm, 999)
        
        logger.info("2-Supervisor + SUPREME AGENT system initialized (optimized for deployment)")
    
    async def verify_code(self, code: str, description: str) -> Dict[str, Any]:
        """Verify code with 2 supervisors + SUPREME AGENT final review.
        
        Args:
            code: Code to verify
            description: What the code should do
            
        Returns:
            Verification result with Supreme Agent decision
        """
        logger.info("🔍 2 Supervisors verifying code in parallel...")
        
        # Create verification task
        task = {
            "type": "supervise",
            "description": f"Verify this code: {description}",
            "context": {"code": code, "expected": description}
        }
        
        # Run both supervisors in PARALLEL (FAST!)
        start_time = asyncio.get_event_loop().time()
        
        results = await asyncio.gather(
            self.supervisors[0].execute_task(task),
            self.supervisors[1].execute_task(task),
            return_exceptions=True
        )
        
        supervisor_elapsed = asyncio.get_event_loop().time() - start_time
        
        # Analyze supervisor results
        approvals = []
        issues = []
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Supervisor {i} error: {result}")
                approvals.append(False)
                issues.append(f"Supervisor {i} crashed")
            else:
                response = result.get("result", "").lower()
                works = "works: yes" in response or "works (yes" in response
                approvals.append(works)
                
                if not works:
                    issues.append(f"Supervisor {i}: {response}")
        
        # Supervisor consensus: Both must approve (2/2)
        supervisor_consensus = sum(approvals) == 2
        
        logger.info(
            f"✅ Supervisors complete in {supervisor_elapsed:.2f}s",
            consensus=supervisor_consensus,
            approvals=f"{sum(approvals)}/2"
        )
        
        # 🔥 SUPREME AGENT FINAL REVIEW (ULTIMATE AUTHORITY!)
        logger.info("👑 SUPREME AGENT making final decision...")
        
        supreme_task = {
            "type": "supreme_review",
            "description": f"Final review: {description}",
            "context": {
                "code": code,
                "description": description,
                "supervisor_consensus": supervisor_consensus,
                "supervisor_approvals": f"{sum(approvals)}/2",
                "supervisor_results": [
                    {
                        "id": i,
                        "approved": approvals[i],
                        "feedback": results[i].get("result", "error") if not isinstance(results[i], Exception) else "crashed"
                    }
                    for i in range(2)
                ],
                "issues": issues
            }
        }
        
        # Supreme Agent makes final decision
        supreme_result = await self.supreme_agent.execute_task(supreme_task)
        supreme_response = supreme_result.get("result", "").lower()
        supreme_approved = "approved for production: yes" in supreme_response or "yes" in supreme_response[:50]
        
        total_elapsed = asyncio.get_event_loop().time() - start_time
        
        # Final verdict: Supervisors + Supreme Agent
        final_verdict = supervisor_consensus and supreme_approved
        
        logger.info(
            f"👑 SUPREME AGENT decision in {total_elapsed:.2f}s total",
            verdict=final_verdict,
            supreme_approved=supreme_approved
        )
        
        return {
            "verified": final_verdict,
            "supervisor_approvals": sum(approvals),
            "supervisor_consensus": supervisor_consensus,
            "supreme_agent_approved": supreme_approved,
            "total_supervisors": 2,
            "elapsed_time": total_elapsed,
            "supervisor_time": supervisor_elapsed,
            "issues": issues if not final_verdict else [],
            "supervisor_results": [
                {
                    "supervisor_id": i,
                    "approved": approvals[i],
                    "result": results[i].get("result", "error") if not isinstance(results[i], Exception) else "crashed"
                }
                for i in range(2)
            ],
            "supreme_agent_result": {
                "approved": supreme_approved,
                "verdict": supreme_result.get("result", "No response"),
                "authority": "FINAL"
            },
            "fast": total_elapsed < 3.0,
            "consensus_model": "2/2 Supervisors + Supreme Agent",
            "status": "✅ APPROVED BY SUPREME AGENT" if final_verdict else "❌ REJECTED BY SUPREME AGENT"
        }
    
    async def rapid_check(self, code: str) -> bool:
        """ULTRA-FAST check if code has obvious errors.
        
        Args:
            code: Code to check
            
        Returns:
            True if code looks good
        """
        # Just use supervisor 1 for ultra-fast check
        task = {
            "type": "rapid_check",
            "description": "Quick syntax and obvious error check",
            "context": {"code": code}
        }
        
        result = await self.supervisors[0].execute_task(task)
        response = result.get("result", "").lower()
        
        return "yes" in response or "pass" in response
    
    def get_stats(self) -> Dict[str, Any]:
        """Get supervisor + Supreme Agent statistics.
        
        Returns:
            Statistics dictionary
        """
        return {
            "total_supervisors": 2,
            "supreme_agent": True,
            "verifications_completed": sum(s.tasks_completed for s in self.supervisors),
            "supreme_agent_reviews": self.supreme_agent.tasks_completed,
            "supervisor_breakdown": [
                {
                    "supervisor_id": s.agent_id,
                    "verifications": s.tasks_completed
                }
                for s in self.supervisors
            ],
            "supreme_agent_stats": {
                "agent_id": self.supreme_agent.agent_id,
                "reviews": self.supreme_agent.tasks_completed,
                "authority": "FINAL"
            },
            "parallel_execution": True,
            "target_speed": "< 3 seconds (total with Supreme Agent)",
            "verification_model": "2 Supervisors (parallel) + Supreme Agent (final)",
            "consensus_model": "2/2 Supervisors + Supreme Agent approval"
        }





