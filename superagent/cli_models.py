"""Model management CLI commands for SuperAgent."""

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
import structlog

from superagent.core.model_manager import ModelCapabilities, ModelManager, ClaudeModel

console = Console()
logger = structlog.get_logger()


@click.group()
def models():
    """Manage AI models for SuperAgent."""
    pass


@models.command()
def list():
    """
    List all available Claude models.
    
    Shows model specifications, capabilities, and pricing.
    """
    console.print(Panel.fit(
        "[bold cyan]Available Claude Models[/bold cyan]\n"
        "Choose the best model for your needs",
        title="Model Selection"
    ))
    
    table = Table(title="\n Available Models", box=box.ROUNDED)
    table.add_column("Model", style="cyan", no_wrap=True)
    table.add_column("Description", style="white")
    table.add_column("Context", style="magenta")
    table.add_column("Speed", style="yellow")
    table.add_column("Cost/MTok", style="green")
    table.add_column("Best For", style="blue")
    
    for model in ModelCapabilities.list_models():
        table.add_row(
            model["name"],
            model["description"][:40],
            f"{model['context_window']:,}",
            model["capabilities"]["speed"],
            f"${model['cost_per_mtok_input']:.2f}",
            model["recommended_for"][0].replace("_", " ")
        )
    
    console.print(table)
    
    # Show recommendations
    console.print("\n[bold]Quick Recommendations:[/bold]")
    console.print("  🚀 [cyan]Best for Coding:[/cyan] Claude 3.5 Sonnet (Latest)")
    console.print("  🧠 [cyan]Most Capable:[/cyan] Claude 3 Opus")
    console.print("  ⚡ [cyan]Fastest:[/cyan] Claude 3 Haiku")
    console.print("  💰 [cyan]Most Economical:[/cyan] Claude 3 Haiku\n")


@models.command()
@click.argument('model1')
@click.argument('model2')
def compare(model1, model2):
    """
    Compare two models.
    
    Example:
        superagent models compare claude-3-5-sonnet-20241022 claude-3-opus-20240229
    """
    console.print(Panel.fit(
        f"[bold magenta]Model Comparison[/bold magenta]\n"
        f"Comparing: {model1} vs {model2}",
        title="Comparison"
    ))
    
    comparison = ModelCapabilities.compare_models(model1, model2)
    
    if "error" in comparison:
        console.print(f"[red]Error: {comparison['error']}[/red]")
        return
    
    table = Table(box=box.ROUNDED)
    table.add_column("Metric", style="cyan")
    table.add_column("Model 1", style="green")
    table.add_column("Model 2", style="yellow")
    
    m1 = comparison["model1"]
    m2 = comparison["model2"]
    
    table.add_row("Name", m1["name"], m2["name"])
    table.add_row("Context Window", f"{m1['context']:,}", f"{m2['context']:,}")
    table.add_row("Input Cost", f"${m1['cost_input']:.2f}/MTok", f"${m2['cost_input']:.2f}/MTok")
    table.add_row("Output Cost", f"${m1['cost_output']:.2f}/MTok", f"${m2['cost_output']:.2f}/MTok")
    table.add_row("Speed", m1["speed"], m2["speed"])
    
    console.print(table)
    console.print(f"\n💡 {comparison['recommendation']}\n")


@models.command()
@click.argument('task_type')
def recommend(task_type):
    """
    Get model recommendation for a task type.
    
    Task types:
        - code_generation
        - debugging
        - refactoring
        - testing
        - documentation
        - simple_task
        - complex_problem
    
    Example:
        superagent models recommend code_generation
    """
    recommended = ModelCapabilities.get_recommended_model(task_type)
    info = ModelCapabilities.get_model_info(recommended)
    
    if not info:
        console.print(f"[red]Unknown task type: {task_type}[/red]")
        console.print("\nAvailable task types:")
        console.print("  - code_generation, debugging, refactoring")
        console.print("  - testing, documentation")
        console.print("  - simple_task, complex_problem")
        return
    
    console.print(Panel.fit(
        f"[bold green]Recommended Model[/bold green]\n\n"
        f"Task: {task_type.replace('_', ' ').title()}\n"
        f"Model: [cyan]{info['name']}[/cyan]\n"
        f"Reason: {info['description']}\n\n"
        f"Context: {info['context_window']:,} tokens\n"
        f"Speed: {info['capabilities']['speed']}\n"
        f"Cost: ${info['cost_per_mtok_input']:.2f} input / ${info['cost_per_mtok_output']:.2f} output per MTok",
        title="Recommendation"
    ))


@models.command()
@click.argument('model_name')
def info(model_name):
    """
    Show detailed information about a model.
    
    Example:
        superagent models info claude-3-5-sonnet-20241022
    """
    model_info = ModelCapabilities.get_model_info(model_name)
    
    if not model_info:
        console.print(f"[red]Model not found: {model_name}[/red]")
        console.print("\nUse 'superagent models list' to see available models.")
        return
    
    console.print(Panel.fit(
        f"[bold cyan]{model_info['name']}[/bold cyan]\n\n"
        f"{model_info['description']}\n\n"
        f"[bold]Specifications:[/bold]\n"
        f"  • Context Window: {model_info['context_window']:,} tokens\n"
        f"  • Max Output: {model_info['max_output']:,} tokens\n"
        f"  • Input Cost: ${model_info['cost_per_mtok_input']:.2f} per MTok\n"
        f"  • Output Cost: ${model_info['cost_per_mtok_output']:.2f} per MTok\n\n"
        f"[bold]Capabilities:[/bold]\n"
        f"  • Coding: {model_info['capabilities']['coding']}\n"
        f"  • Reasoning: {model_info['capabilities']['reasoning']}\n"
        f"  • Speed: {model_info['capabilities']['speed']}\n"
        f"  • Vision: {'Yes' if model_info['capabilities']['vision'] else 'No'}\n\n"
        f"[bold]Best For:[/bold]\n" +
        "\n".join(f"  • {task.replace('_', ' ').title()}" for task in model_info['recommended_for']),
        title="Model Information"
    ))


@models.command()
@click.argument('input_tokens', type=int)
@click.argument('output_tokens', type=int)
@click.option('--model', '-m', help='Model to estimate (default: current)')
def estimate_cost(input_tokens, output_tokens, model):
    """
    Estimate cost for token usage.
    
    Example:
        superagent models estimate-cost 10000 2000
        superagent models estimate-cost 10000 2000 --model claude-3-opus-20240229
    """
    model = model or ClaudeModel.LATEST.value
    
    manager = ModelManager()
    cost = manager.estimate_cost(input_tokens, output_tokens, model)
    
    if "error" in cost:
        console.print(f"[red]Error: {cost['error']}[/red]")
        return
    
    console.print(Panel.fit(
        f"[bold yellow]Cost Estimate[/bold yellow]\n\n"
        f"Model: [cyan]{cost['model']}[/cyan]\n\n"
        f"Input: {cost['input_tokens']:,} tokens → [green]${cost['input_cost']:.4f}[/green]\n"
        f"Output: {cost['output_tokens']:,} tokens → [green]${cost['output_cost']:.4f}[/green]\n\n"
        f"[bold]Total: [green]${cost['total_cost']:.4f}[/green][/bold]",
        title="Cost Estimate"
    ))


@models.command()
def current():
    """Show the currently configured model."""
    from superagent.core.config import Config
    
    config = Config()
    model_name = config.model.name
    info = ModelCapabilities.get_model_info(model_name)
    
    console.print(Panel.fit(
        f"[bold green]Current Model[/bold green]\n\n"
        f"Model: [cyan]{info['name'] if info else model_name}[/cyan]\n"
        f"Provider: {config.model.provider}\n"
        f"Temperature: {config.model.temperature}\n"
        f"Max Tokens: {config.model.max_tokens}",
        title="Configuration"
    ))
    
    if info:
        console.print(f"\n💡 {info['description']}\n")


@models.command()
def update_guide():
    """
    Show guide for updating to newer Claude models.
    
    Explains how to use the latest models and prepare for future releases.
    """
    console.print(Panel.fit(
        "[bold cyan]Claude Model Update Guide[/bold cyan]\n\n"
        "[bold]Current Status:[/bold]\n"
        "✓ Using Claude 3.5 Sonnet (Latest available)\n"
        "✓ Claude 3.5 is the most advanced model\n\n"
        "[bold]Note:[/bold] There is no Claude 4.5 yet.\n"
        "Claude 3.5 Sonnet is the latest and most capable model.\n\n"
        "[bold]Available Claude Models:[/bold]\n"
        "  • Claude 3.5 Sonnet (Latest) - Recommended\n"
        "  • Claude 3 Opus - Most capable\n"
        "  • Claude 3 Sonnet - Balanced\n"
        "  • Claude 3 Haiku - Fastest\n\n"
        "[bold]How to Switch Models:[/bold]\n"
        "1. Edit config.yaml:\n"
        "   models:\n"
        "     primary:\n"
        "       name: 'claude-3-5-sonnet-20241022'\n\n"
        "2. Or set environment variable:\n"
        "   export CLAUDE_MODEL='claude-3-opus-20240229'\n\n"
        "3. Use CLI:\n"
        "   superagent models list\n"
        "   superagent models info <model-name>\n\n"
        "[bold]Preparing for Future Models:[/bold]\n"
        "✓ Model manager supports auto-detection\n"
        "✓ Easy configuration updates\n"
        "✓ Backward compatibility maintained\n\n"
        "When Claude 4.x is released, simply update\n"
        "the model name in config.yaml!",
        title="Model Updates"
    ))


if __name__ == "__main__":
    models()





