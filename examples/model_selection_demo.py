"""Demonstration of model selection and management in SuperAgent."""

import asyncio
from superagent import SuperAgent, Config
from superagent.core.model_manager import ModelManager, ModelCapabilities, ClaudeModel


async def demo_model_info():
    """Show information about available models."""
    
    print("=" * 60)
    print("SuperAgent Model Selection Demo")
    print("=" * 60)
    
    print("\n1. Available Claude Models:")
    print("-" * 60)
    
    models = ModelCapabilities.list_models()
    
    for model in models:
        print(f"\n📦 {model['name']}")
        print(f"   ID: {model['id']}")
        print(f"   Description: {model['description']}")
        print(f"   Context: {model['context_window']:,} tokens")
        print(f"   Speed: {model['capabilities']['speed']}")
        print(f"   Cost: ${model['cost_per_mtok_input']:.2f} input / ${model['cost_per_mtok_output']:.2f} output")
        print(f"   Best for: {', '.join(model['recommended_for'][:2])}")


async def demo_model_comparison():
    """Compare different models."""
    
    print("\n\n2. Model Comparison:")
    print("-" * 60)
    
    # Compare Claude 3.5 Sonnet vs Claude 3 Opus
    comparison = ModelCapabilities.compare_models(
        ClaudeModel.CLAUDE_3_5_SONNET_LATEST.value,
        ClaudeModel.CLAUDE_3_OPUS_LATEST.value
    )
    
    print(f"\n🆚 {comparison['model1']['name']} vs {comparison['model2']['name']}")
    print(f"\nContext Window:")
    print(f"  • Model 1: {comparison['model1']['context']:,} tokens")
    print(f"  • Model 2: {comparison['model2']['context']:,} tokens")
    
    print(f"\nSpeed:")
    print(f"  • Model 1: {comparison['model1']['speed']}")
    print(f"  • Model 2: {comparison['model2']['speed']}")
    
    print(f"\nCost (per MTok):")
    print(f"  • Model 1: ${comparison['model1']['cost_input']:.2f} input, ${comparison['model1']['cost_output']:.2f} output")
    print(f"  • Model 2: ${comparison['model2']['cost_input']:.2f} input, ${comparison['model2']['cost_output']:.2f} output")
    
    print(f"\n💡 {comparison['recommendation']}")


async def demo_model_recommendations():
    """Show recommended models for different tasks."""
    
    print("\n\n3. Task-Specific Recommendations:")
    print("-" * 60)
    
    tasks = [
        "code_generation",
        "debugging",
        "simple_task",
        "complex_problem",
        "documentation"
    ]
    
    for task in tasks:
        recommended = ModelCapabilities.get_recommended_model(task)
        info = ModelCapabilities.get_model_info(recommended)
        
        print(f"\n📋 {task.replace('_', ' ').title()}")
        print(f"   Recommended: {info['name']}")
        print(f"   Why: {info['description']}")


async def demo_cost_estimation():
    """Estimate costs for different operations."""
    
    print("\n\n4. Cost Estimation:")
    print("-" * 60)
    
    manager = ModelManager()
    
    operations = [
        ("Small function", 1000, 500),
        ("Full module", 5000, 2000),
        ("Large project", 20000, 8000),
    ]
    
    for op_name, input_tok, output_tok in operations:
        print(f"\n💰 {op_name} ({input_tok:,} input, {output_tok:,} output):")
        
        for model_name in [ClaudeModel.CLAUDE_3_5_SONNET_LATEST.value,
                          ClaudeModel.CLAUDE_3_OPUS_LATEST.value,
                          ClaudeModel.CLAUDE_3_HAIKU.value]:
            
            cost = manager.estimate_cost(input_tok, output_tok, model_name)
            info = ModelCapabilities.get_model_info(model_name)
            
            print(f"   {info['name']}: ${cost['total_cost']:.4f}")


async def demo_model_switching():
    """Demonstrate switching between models."""
    
    print("\n\n5. Model Switching:")
    print("-" * 60)
    
    # Create different configurations
    configs = {
        "Fast (Haiku)": ClaudeModel.CLAUDE_3_HAIKU.value,
        "Balanced (3.5 Sonnet)": ClaudeModel.CLAUDE_3_5_SONNET_LATEST.value,
        "Most Capable (Opus)": ClaudeModel.CLAUDE_3_OPUS_LATEST.value,
    }
    
    for name, model in configs.items():
        config = Config()
        config.model.name = model
        
        info = ModelCapabilities.get_model_info(model)
        
        print(f"\n⚙️  {name}")
        print(f"   Model: {info['name']}")
        print(f"   Speed: {info['capabilities']['speed']}")
        print(f"   Use for: {info['recommended_for'][0].replace('_', ' ')}")


async def demo_auto_selection():
    """Demonstrate automatic model selection."""
    
    print("\n\n6. Automatic Model Selection:")
    print("-" * 60)
    
    manager = ModelManager()
    
    scenarios = [
        {
            "task": "code_generation",
            "description": "Generate REST API",
            "prioritize_speed": False,
            "prioritize_cost": False
        },
        {
            "task": "simple_task",
            "description": "Format code",
            "prioritize_speed": True,
            "prioritize_cost": True
        },
        {
            "task": "complex_problem",
            "description": "Design microservices",
            "prioritize_speed": False,
            "prioritize_cost": False
        }
    ]
    
    for scenario in scenarios:
        selected = manager.auto_select_model(
            task_type=scenario["task"],
            prioritize_speed=scenario.get("prioritize_speed", False),
            prioritize_cost=scenario.get("prioritize_cost", False)
        )
        
        info = ModelCapabilities.get_model_info(selected)
        
        print(f"\n🎯 {scenario['description']}")
        print(f"   Task Type: {scenario['task']}")
        print(f"   Auto-selected: {info['name']}")
        print(f"   Reason: {info['description']}")


async def demo_using_with_superagent():
    """Show how to use different models with SuperAgent."""
    
    print("\n\n7. Using Models with SuperAgent:")
    print("-" * 60)
    
    print("\n✅ Default configuration (Claude 3.5 Sonnet):")
    config = Config()
    print(f"   Model: {config.model.name}")
    print(f"   Temperature: {config.model.temperature}")
    print(f"   Max tokens: {config.model.max_tokens}")
    
    print("\n✅ Custom configuration (Claude 3 Opus):")
    config_opus = Config()
    config_opus.model.name = ClaudeModel.CLAUDE_3_OPUS_LATEST.value
    print(f"   Model: {config_opus.model.name}")
    
    print("\n✅ Speed-optimized (Claude 3 Haiku):")
    config_fast = Config()
    config_fast.model.name = ClaudeModel.CLAUDE_3_HAIKU.value
    print(f"   Model: {config_fast.model.name}")
    
    print("\n💡 To use in your code:")
    print("""
    config = Config()
    config.model.name = "claude-3-5-sonnet-20241022"
    
    async with SuperAgent(config) as agent:
        result = await agent.execute_instruction("Your task")
    """)


async def main():
    """Run all demos."""
    
    try:
        await demo_model_info()
        await demo_model_comparison()
        await demo_model_recommendations()
        await demo_cost_estimation()
        await demo_model_switching()
        await demo_auto_selection()
        await demo_using_with_superagent()
        
        print("\n" + "=" * 60)
        print("Demo Complete!")
        print("=" * 60)
        
        print("\n✅ Key Takeaways:")
        print("  • Claude 3.5 Sonnet is the latest and best for coding")
        print("  • Use Claude 3 Opus for complex problems")
        print("  • Use Claude 3 Haiku for simple/fast tasks")
        print("  • SuperAgent can auto-select models per task")
        print("  • Easy to switch models via config")
        
        print("\n📚 Learn More:")
        print("  • Read MODEL_GUIDE.md for full documentation")
        print("  • Run 'superagent models list' to see all models")
        print("  • Run 'superagent models current' to check config")
        
        print("\n🚀 SuperAgent is already using the latest Claude 3.5 Sonnet!")
        
    except KeyboardInterrupt:
        print("\n\nDemo cancelled.")


if __name__ == "__main__":
    asyncio.run(main())





