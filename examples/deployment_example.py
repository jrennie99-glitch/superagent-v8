"""Deployment example."""

import asyncio
from pathlib import Path
from superagent import SuperAgent, Config


async def main():
    """Demonstrate deployment capabilities."""
    
    config = Config()
    
    async with SuperAgent(config) as agent:
        # First, create a simple web app
        print("Creating a sample web application...\n")
        
        result = await agent.execute_instruction(
            "Create a simple Flask web app with a home route that returns 'Hello World'",
            project_name="hello_world_app"
        )
        
        project_path = Path(agent.workspace) / result['project']
        print(f"✓ Project created at: {project_path}\n")
        
        # Run tests
        print("Running tests...\n")
        test_results = await agent.tester.run_tests(project_path)
        
        if test_results['success']:
            print("✓ All tests passed\n")
        else:
            print("⚠ Some tests failed\n")
        
        # Deploy to Heroku (simulated in this example)
        print("Deploying to Heroku...\n")
        
        deploy_result = await agent.deployer.deploy(
            project_path,
            platform="heroku"
        )
        
        if deploy_result['success']:
            print(f"✓ Deployment successful!")
            if deploy_result.get('url'):
                print(f"  URL: {deploy_result['url']}")
        else:
            print(f"✗ Deployment failed: {deploy_result.get('error', 'Unknown error')}")
            print("\nNote: This example requires Heroku CLI to be installed")
            print("and configured. For testing without deployment, run:")
            print("  superagent create 'your instruction' --workspace ./test")
        
        print("\n✓ Example complete!")


if __name__ == "__main__":
    asyncio.run(main())





