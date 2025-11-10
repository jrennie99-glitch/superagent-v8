# Quick Start - Enterprise Code Generation

## Generate Your First Enterprise App

### Step 1: Set API Key
```bash
export ANTHROPIC_API_KEY="your-key-here"
```

### Step 2: Create Python Script

```python
import asyncio
from superagent import SuperAgent

async def main():
    async with SuperAgent() as agent:
        result = await agent.enterprise_generator.generate_enterprise_web_app(
            description="Create a professional calculator with basic operations",
            app_name="my_calculator",
            app_type="calculator"
        )
        
        # Save file
        for filename, content in result['files'].items():
            with open(filename, 'w') as f:
                f.write(content)
        
        print(f"✅ Created: {filename}")
        print(f"📊 Quality: {result['quality_report']['overall_score']}/100")

asyncio.run(main())
```

### Step 3: Run
```bash
python your_script.py
```

### Step 4: Open in Browser
```bash
open my_calculator.html
```

## Test the System

```bash
cd /home/ubuntu/superagent-v8
python test_enterprise_calculator.py
```

## Key Differences

### Old Way (Low Quality)
```python
agent.code_generator.generate_project(...)
# Result: Often broken, incomplete
```

### New Way (Enterprise Quality)
```python
agent.enterprise_generator.generate_enterprise_web_app(...)
# Result: Professional, fully functional
```

## Quality Scores

- **90-100**: Excellent, production-ready ✅
- **80-89**: Good, ready to use ✅
- **70-79**: Acceptable, needs minor fixes ⚠️
- **Below 70**: Needs improvement ❌

## App Types Supported

- `calculator` - Calculators (basic, scientific)
- `dashboard` - Admin panels, analytics
- `form` - Contact, survey, registration
- `todo` - Task managers, checklists
- `timer` - Countdown, stopwatch, pomodoro

## More Info

- **Full Guide**: `ENTERPRISE_MODE_GUIDE.md`
- **Summary**: `IMPROVEMENTS_SUMMARY.md`
- **Test**: `test_enterprise_calculator.py`

---

**That's it!** Start creating enterprise-quality apps now! 🚀
