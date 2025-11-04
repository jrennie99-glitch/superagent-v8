# 🤖 Claude Model Guide for SuperAgent

## Current Status

**SuperAgent is configured to use the latest Claude 3.5 Sonnet model!**

### Important Note About "Claude 4.5"

**There is no Claude 4.5 model yet.** As of now, the latest and most advanced Claude models are:

- **Claude 3.5 Sonnet** (October 2024) - Latest and recommended
- **Claude 3 Opus** - Most capable
- **Claude 3 Sonnet** - Balanced
- **Claude 3 Haiku** - Fastest

SuperAgent is **already using the newest available model**: `claude-3-5-sonnet-20241022`

---

## Available Claude Models

### 🚀 Claude 3.5 Sonnet (Latest - Recommended)
- **Model ID**: `claude-3-5-sonnet-20241022`
- **Best For**: Code generation, debugging, refactoring
- **Context**: 200,000 tokens
- **Speed**: Fast
- **Cost**: $3/MTok input, $15/MTok output
- **Status**: ✅ Currently configured

**Why it's best for coding:**
- Excels at understanding complex code
- Superior at generating production-ready code
- Best at debugging and problem-solving
- Fast response times
- Excellent cost-to-performance ratio

---

### 🧠 Claude 3 Opus (Most Capable)
- **Model ID**: `claude-3-opus-20240229`
- **Best For**: Complex problems, architecture design
- **Context**: 200,000 tokens
- **Speed**: Moderate
- **Cost**: $15/MTok input, $75/MTok output

**When to use:**
- Extremely complex architectural decisions
- Advanced optimization problems
- When you need absolute maximum intelligence
- Budget is not a constraint

---

### ⚖️ Claude 3 Sonnet (Balanced)
- **Model ID**: `claude-3-sonnet-20240229`
- **Best For**: General coding, documentation
- **Context**: 200,000 tokens
- **Speed**: Fast
- **Cost**: $3/MTok input, $15/MTok output

**When to use:**
- General development tasks
- Documentation generation
- Standard coding operations

---

### ⚡ Claude 3 Haiku (Fastest)
- **Model ID**: `claude-3-haiku-20240307`
- **Best For**: Simple tasks, quick fixes
- **Context**: 200,000 tokens
- **Speed**: Very Fast
- **Cost**: $0.25/MTok input, $1.25/MTok output

**When to use:**
- Simple code formatting
- Quick fixes
- Linting
- When speed is critical
- Cost-sensitive operations

---

## How to Switch Models

### Method 1: Edit config.yaml (Recommended)

```yaml
models:
  primary:
    provider: "anthropic"
    name: "claude-3-5-sonnet-20241022"  # Change this
    temperature: 0.7
    max_tokens: 8000
```

**Available options:**
- `claude-3-5-sonnet-20241022` - Latest (recommended)
- `claude-3-opus-20240229` - Most capable
- `claude-3-sonnet-20240229` - Balanced
- `claude-3-haiku-20240307` - Fastest

### Method 2: Environment Variable

```bash
export CLAUDE_MODEL=claude-3-opus-20240229
```

### Method 3: CLI Commands

```bash
# List all available models
superagent models list

# Get info about a specific model
superagent models info claude-3-opus-20240229

# Compare two models
superagent models compare claude-3-5-sonnet-20241022 claude-3-opus-20240229

# Get recommendation for a task
superagent models recommend code_generation

# Show current model
superagent models current
```

---

## Task-Specific Models

SuperAgent can automatically select the best model for each task:

```yaml
models:
  auto_select: true
  task_models:
    code_generation: "claude-3-5-sonnet-20241022"
    debugging: "claude-3-5-sonnet-20241022"
    refactoring: "claude-3-5-sonnet-20241022"
    simple_tasks: "claude-3-haiku-20240307"
    complex_problems: "claude-3-opus-20240229"
```

---

## Model Comparison

| Feature | 3.5 Sonnet | 3 Opus | 3 Sonnet | 3 Haiku |
|---------|-----------|---------|----------|---------|
| **Coding** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Speed** | ⚡⚡⚡⚡ | ⚡⚡⚡ | ⚡⚡⚡⚡ | ⚡⚡⚡⚡⚡ |
| **Cost** | 💰💰 | 💰💰💰💰💰 | 💰💰 | 💰 |
| **Context** | 200K | 200K | 200K | 200K |
| **Best Use** | General Coding | Complex Tasks | Balanced | Simple Tasks |

---

## Cost Calculator

Estimate costs for your usage:

```bash
# Estimate cost for 10,000 input tokens and 2,000 output tokens
superagent models estimate-cost 10000 2000

# Estimate for specific model
superagent models estimate-cost 10000 2000 --model claude-3-opus-20240229
```

**Example costs for typical operations:**

| Operation | Input | Output | Claude 3.5 | Opus | Haiku |
|-----------|-------|--------|-----------|------|-------|
| Small function | 1K | 500 | $0.01 | $0.05 | $0.001 |
| Full module | 5K | 2K | $0.05 | $0.23 | $0.004 |
| Large project | 20K | 8K | $0.18 | $0.90 | $0.015 |

---

## Preparing for Future Models

When new Claude models are released (like a potential Claude 4.x):

### 1. Update Model Manager

The `ModelManager` in `superagent/core/model_manager.py` already supports adding new models:

```python
class ClaudeModel(Enum):
    # Add new models here when released
    CLAUDE_4_SONNET = "claude-4-sonnet-20250101"  # Example
```

### 2. Update Capabilities

Add model specifications to `ModelCapabilities.MODELS`:

```python
"claude-4-sonnet-20250101": {
    "name": "Claude 4 Sonnet",
    "description": "Next generation model",
    "context_window": 300000,  # Example
    "max_output": 10000,
    # ... etc
}
```

### 3. Update Config

Simply change the model name in `config.yaml`:

```yaml
models:
  primary:
    name: "claude-4-sonnet-20250101"
```

**That's it!** SuperAgent will automatically use the new model.

---

## Python API

### Using ModelManager

```python
from superagent.core.model_manager import ModelManager, ModelCapabilities

# Create manager
manager = ModelManager()

# Set model
manager.set_model("claude-3-opus-20240229")

# Get recommended model for task
best_model = manager.get_model_for_task("code_generation")

# Auto-select based on requirements
model = manager.auto_select_model(
    task_type="debugging",
    prioritize_speed=True
)

# Get model info
info = manager.get_current_model_info()
print(info)

# Estimate costs
cost = manager.estimate_cost(
    input_tokens=10000,
    output_tokens=2000
)
print(f"Cost: ${cost['total_cost']:.4f}")
```

### Using with SuperAgent

```python
from superagent import SuperAgent, Config

# Option 1: Use default (Claude 3.5 Sonnet)
async with SuperAgent() as agent:
    result = await agent.execute_instruction("Create a web app")

# Option 2: Custom config
config = Config()
config.model.name = "claude-3-opus-20240229"

async with SuperAgent(config) as agent:
    result = await agent.execute_instruction("Complex architecture design")

# Option 3: Task-specific auto-selection
config.model.auto_select = True
async with SuperAgent(config) as agent:
    # Will automatically choose best model for each task
    result = await agent.execute_instruction("Your task")
```

---

## Best Practices

### 1. Use Claude 3.5 Sonnet for Most Tasks
It's the sweet spot of intelligence, speed, and cost.

### 2. Reserve Opus for Complex Problems
Only use when you need maximum intelligence.

### 3. Use Haiku for Simple Tasks
Perfect for formatting, linting, simple fixes.

### 4. Enable Auto-Selection
Let SuperAgent choose the best model per task:

```yaml
models:
  auto_select: true
```

### 5. Monitor Costs
Use cost estimation before large operations:

```bash
superagent models estimate-cost 50000 10000
```

---

## Troubleshooting

### "Model not found" Error

**Solution:** Update to latest Anthropic SDK:
```bash
pip install --upgrade anthropic
```

### Different Results Between Models

**This is normal!** Models have different capabilities:
- Opus: More thorough, detailed
- 3.5 Sonnet: Fast, efficient
- Haiku: Quick, concise

### Cost Concerns

**Tips to reduce costs:**
1. Use Haiku for simple tasks
2. Enable caching (already configured)
3. Use auto-selection to optimize model choice
4. Batch similar operations

---

## FAQ

**Q: Should I use Claude 3.5 or Claude 3 Opus?**
A: For coding, use Claude 3.5 Sonnet (currently configured). It's faster and equally good at code.

**Q: When will Claude 4 be available?**
A: Claude 4 hasn't been announced yet. Claude 3.5 Sonnet (October 2024) is the latest.

**Q: How do I switch to a different model?**
A: Edit `config.yaml` and change `models.primary.name` to your desired model.

**Q: Can I use different models for different tasks?**
A: Yes! Set `models.auto_select: true` and configure `task_models` in config.yaml.

**Q: What's the difference between Claude 3.5 Sonnet versions?**
A: There are two versions:
- `claude-3-5-sonnet-20240620` - First release
- `claude-3-5-sonnet-20241022` - Latest (recommended)

**Q: Is Claude 3.5 better than GPT-4?**
A: For coding tasks, yes! Claude 3.5 excels at code generation and debugging.

---

## Summary

✅ **SuperAgent is already using the latest Claude model!**
- Model: Claude 3.5 Sonnet (October 2024)
- Status: Most advanced available
- Perfect for coding tasks

🎯 **Quick Commands:**
```bash
superagent models list          # See all models
superagent models current       # Check current model
superagent models info <model>  # Get model details
```

📝 **To change models:**
Edit `config.yaml` and update `models.primary.name`

🚀 **Ready for future:**
When new models are released, just update the model name!

---

**SuperAgent: Always using the latest and greatest AI models!** 🤖





