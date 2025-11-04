# SuperAgent Examples

This directory contains example scripts demonstrating SuperAgent's capabilities.

## Examples

### 1. Basic Usage (`basic_usage.py`)

Demonstrates basic SuperAgent usage:
- Creating an agent
- Executing a simple instruction
- Viewing results and statistics

```bash
python examples/basic_usage.py
```

### 2. Multi-Agent Collaboration (`multi_agent_example.py`)

Shows how to use multiple specialized agents:
- Creating a multi-agent orchestrator
- Collaborative problem solving
- Agent statistics and performance

```bash
python examples/multi_agent_example.py
```

### 3. Advanced Debugging (`debugging_example.py`)

Demonstrates debugging capabilities:
- Error detection and analysis
- Automatic fix suggestions
- Code complexity analysis
- Visual debug reports

```bash
python examples/debugging_example.py
```

### 4. Deployment (`deployment_example.py`)

Shows deployment workflow:
- Creating a web application
- Running tests
- Deploying to cloud platforms

```bash
python examples/deployment_example.py
```

## Requirements

Make sure you have:
1. Installed SuperAgent: `pip install -e .`
2. Set up your `.env` file with API keys
3. (Optional) Redis running for caching

## Sample Workflow

```python
import asyncio
from superagent import SuperAgent

async def main():
    async with SuperAgent() as agent:
        result = await agent.execute_instruction(
            "Create a REST API with user authentication"
        )
        print(f"Project: {result['project']}")

asyncio.run(main())
```

## Notes

- Examples create temporary workspaces/projects
- Some examples require external services (Redis, Heroku CLI)
- All examples use Claude 3.5 Sonnet for code generation





