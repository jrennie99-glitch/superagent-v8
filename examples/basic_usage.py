"""Basic usage example for SuperAgent."""

import asyncio
from superagent import SuperAgent, Config


async def main():
    """Demonstrate basic SuperAgent usage."""
    
    # Initialize configuration
    config = Config()
    
    # Create agent
    async with SuperAgent(config, workspace="./example_workspace") as agent:
        print("SuperAgent initialized successfully!")
        
        # Execute a simple instruction
        instruction = "Create a Python Flask REST API with 2 endpoints: /health and /api/data"
        
        print(f"\nExecuting instruction: {instruction}")
        
        result = await agent.execute_instruction(
            instruction=instruction,
            project_name="my_flask_api"
        )
        
        print(f"\n✓ Project created: {result['project']}")
        print(f"✓ Files generated: {len(result['results'])}")
        
        # Show statistics
        stats = result['stats']
        print(f"\nStatistics:")
        print(f"  - Tokens used: {stats['llm_stats']['total_tokens_used']}")
        print(f"  - Iterations: {stats['iteration_count']}")
        
        print("\n✓ Example completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())





