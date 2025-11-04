"""Multi-agent collaboration example."""

import asyncio
from superagent import Config
from superagent.core.multi_agent import MultiAgentOrchestrator


async def main():
    """Demonstrate multi-agent collaboration."""
    
    config = Config()
    
    # Create multi-agent orchestrator with 4 agents
    orchestrator = MultiAgentOrchestrator(config, num_agents=4)
    
    print("Multi-Agent System initialized with 4 specialized agents")
    print("Roles: Coder, Debugger, Tester, Reviewer\n")
    
    # Collaborative problem solving
    problem = """
    Create a user authentication system with:
    - User registration with email validation
    - Login with JWT tokens
    - Password hashing with bcrypt
    - Session management
    - Rate limiting for security
    """
    
    print(f"Problem: {problem.strip()}\n")
    print("Starting collaborative solution...\n")
    
    result = await orchestrator.collaborative_solve(problem)
    
    print("✓ Collaborative solution complete!\n")
    print("Architecture:")
    print(result['architecture'][:500] + "...\n")
    
    print(f"Implementations: {len(result['implementations'])}")
    print(f"Tests: {len(result['tests'])}")
    print(f"Review: Available\n")
    
    # Show agent statistics
    stats = orchestrator.get_stats()
    print("Agent Statistics:")
    for agent in stats['agent_breakdown']:
        print(f"  - Agent {agent['agent_id']} ({agent['role']}): {agent['tasks']} tasks")
    
    print(f"\nTotal tasks completed: {stats['tasks_completed']}")


if __name__ == "__main__":
    asyncio.run(main())





