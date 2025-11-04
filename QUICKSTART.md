# SuperAgent Quick Start Guide

Get started with SuperAgent in 5 minutes!

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/superagent.git
cd superagent

# Install dependencies
pip install -r requirements.txt

# Install SuperAgent
pip install -e .
```

## Configuration

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Add your Anthropic API key to `.env`:
```env
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

## Your First Project

### Option 1: Command Line

Create a simple web API:
```bash
superagent create "Build a Flask REST API with a /health endpoint"
```

### Option 2: Python Script

```python
import asyncio
from superagent import SuperAgent

async def main():
    async with SuperAgent() as agent:
        result = await agent.execute_instruction(
            "Create a Python calculator with add and multiply functions"
        )
        print(f"✓ Project created: {result['project']}")

asyncio.run(main())
```

### Option 3: REST API

Start the API server:
```bash
uvicorn superagent.api:app --reload
```

Make a request:
```bash
curl -X POST http://localhost:8000/execute \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key" \
  -d '{"instruction": "Create a simple todo app"}'
```

## Common Tasks

### Debug a Project
```bash
superagent debug ./my_project --fix
```

### Run Tests
```bash
superagent test ./my_project
```

### Deploy
```bash
superagent deploy ./my_project --platform heroku
```

### Use Multi-Agent Mode
```bash
superagent create "Build a microservices app" --multi-agent
```

## Examples

Check the `examples/` directory:

- `basic_usage.py` - Simple agent usage
- `multi_agent_example.py` - Multi-agent collaboration
- `debugging_example.py` - Advanced debugging
- `deployment_example.py` - Cloud deployment

Run any example:
```bash
python examples/basic_usage.py
```

## Next Steps

1. Read the [full documentation](README.md)
2. Explore the [API reference](docs/API.md)
3. Try the [examples](examples/)
4. Run the [benchmarks](tests/test_performance.py)

## Troubleshooting

**Issue**: "ANTHROPIC_API_KEY not set"
- **Solution**: Make sure you've created `.env` and added your API key

**Issue**: Redis connection error
- **Solution**: SuperAgent works without Redis using disk cache

**Issue**: Import errors
- **Solution**: Run `pip install -e .` to install in development mode

## Support

- 📧 Email: support@superagent.dev
- 💬 Discord: [Join our community](https://discord.gg/superagent)
- 🐛 Issues: [GitHub Issues](https://github.com/yourusername/superagent/issues)

Happy coding with SuperAgent! 🚀





