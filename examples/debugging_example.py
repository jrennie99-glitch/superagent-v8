"""Advanced debugging example."""

import asyncio
from pathlib import Path
from superagent import SuperAgent, Config


async def main():
    """Demonstrate advanced debugging capabilities."""
    
    # Create a sample project with bugs
    sample_code = '''
def calculate_average(numbers):
    total = 0
    for num in numbers:
        total += num
    return total / len(numbers)  # Bug: Division by zero if empty list

def fetch_user_data(user_id):
    # Bug: Missing import
    response = requests.get(f"https://api.example.com/users/{user_id}")
    return response.json()

def process_data(data):
    # Bug: Potential KeyError
    return data["result"]["value"]
'''
    
    # Setup sample project
    project_path = Path("./debug_example_project")
    project_path.mkdir(exist_ok=True)
    (project_path / "buggy_code.py").write_text(sample_code)
    
    print("Created sample project with intentional bugs\n")
    
    # Initialize agent
    config = Config()
    async with SuperAgent(config) as agent:
        print("Running advanced debugger...\n")
        
        # Debug the project
        results = await agent.debugger.debug_project(project_path)
        
        # Show errors
        if results['errors']:
            print(f"Found {len(results['errors'])} errors:\n")
            for i, error in enumerate(results['errors'], 1):
                print(f"{i}. {error.get('type', 'Error')} at line {error.get('line', 0)}")
                print(f"   {error.get('message', '')}\n")
        
        # Show warnings
        if results['warnings']:
            print(f"Found {len(results['warnings'])} warnings:\n")
            for i, warning in enumerate(results['warnings'], 1):
                print(f"{i}. {warning.get('message', '')}\n")
        
        # Auto-fix errors
        if results['errors'] and config.debugging.auto_fix_enabled:
            print("Applying automatic fixes...\n")
            fixes = await agent.debugger.auto_fix_errors(results['errors'])
            
            for i, fix in enumerate(fixes, 1):
                print(f"Fix {i} (confidence: {fix['confidence']:.0%}):")
                print(f"  Root cause: {fix['root_cause']}")
                print(f"  Fix: {fix['explanation'][:100]}...\n")
        
        # Show complexity report
        if results.get('complexity_report'):
            print("Code Complexity:")
            summary = results['complexity_report'].get('summary', {})
            print(f"  - Total files: {summary.get('total_files', 0)}")
            print(f"  - Total functions: {summary.get('total_functions', 0)}")
            print(f"  - Average complexity: {summary.get('average_complexity', 0):.2f}")
        
        print("\n✓ Debug analysis complete!")


if __name__ == "__main__":
    asyncio.run(main())





