"""Advanced CLI commands for new features."""

import asyncio
import click
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
import structlog

from superagent.core.agent import SuperAgent
from superagent.core.config import Config
from superagent.modules.code_reviewer import CodeReviewer
from superagent.modules.refactoring_engine import RefactoringEngine
from superagent.modules.doc_generator import DocumentationGenerator
from superagent.modules.codebase_query import CodebaseQueryEngine
from superagent.modules.performance_profiler import PerformanceProfiler

console = Console()
logger = structlog.get_logger()


@click.group()
def advanced():
    """Advanced SuperAgent features."""
    pass


@advanced.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--config', '-c', help='Configuration file')
def review(file_path, config):
    """
    Perform comprehensive code review.
    
    Example:
        superagent review ./src/main.py
    """
    console.print(Panel.fit(
        f"[bold cyan]Code Review[/bold cyan]\n"
        f"File: {file_path}",
        title="AI-Powered Code Review"
    ))
    
    async def run():
        cfg = Config(config) if config else Config()
        
        async with SuperAgent(cfg) as agent:
            reviewer = CodeReviewer(agent.llm)
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Analyzing code...", total=None)
                
                result = await reviewer.review_file(Path(file_path))
                
                progress.update(task, description="Complete!", completed=True)
            
            # Display results
            console.print(f"\n[bold]Overall Grade: {result['overall_grade']}[/bold]")
            
            # Scores
            scores_table = Table(title="Quality Scores")
            scores_table.add_column("Metric", style="cyan")
            scores_table.add_column("Score", style="green")
            
            for metric, score in result['scores'].items():
                scores_table.add_row(metric.title(), f"{score:.1f}/100")
            
            console.print(scores_table)
            
            # Security issues
            if result.get('security'):
                console.print(f"\n[bold red]Security Issues: {len(result['security'])}[/bold red]")
                for issue in result['security'][:5]:
                    console.print(f"  • {issue['description']} (Line {issue.get('line', '?')})")
            
            # AI Suggestions
            if result.get('ai_suggestions'):
                console.print(f"\n[bold blue]AI Suggestions:[/bold blue]")
                for sug in result['ai_suggestions'][:3]:
                    console.print(f"  • [{sug.get('category', 'General')}] {sug.get('suggestion', '')}")
    
    asyncio.run(run())


@advanced.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--type', '-t', help='Refactoring type')
@click.option('--config', '-c', help='Configuration file')
def refactor(file_path, type, config):
    """
    Suggest or apply code refactorings.
    
    Example:
        superagent refactor ./src/main.py
    """
    console.print(Panel.fit(
        f"[bold magenta]Refactoring Engine[/bold magenta]\n"
        f"File: {file_path}",
        title="AI-Powered Refactoring"
    ))
    
    async def run():
        cfg = Config(config) if config else Config()
        
        async with SuperAgent(cfg) as agent:
            engine = RefactoringEngine(agent.llm)
            
            console.print("\n[bold]Analyzing code...[/bold]")
            suggestions = await engine.suggest_refactorings(Path(file_path))
            
            if suggestions:
                table = Table(title="Refactoring Suggestions")
                table.add_column("#", style="cyan")
                table.add_column("Type", style="magenta")
                table.add_column("Description", style="white")
                
                for i, sug in enumerate(suggestions, 1):
                    table.add_row(
                        str(i),
                        sug.get('type', ''),
                        sug.get('description', '')[:100]
                    )
                
                console.print(table)
            else:
                console.print("[green]✓ No refactorings needed - code looks good![/green]")
    
    asyncio.run(run())


@advanced.command()
@click.argument('project_path', type=click.Path(exists=True))
@click.option('--type', '-t', type=click.Choice(['readme', 'api', 'tutorial', 'openapi']),
              default='readme', help='Documentation type')
@click.option('--output', '-o', help='Output file')
@click.option('--config', '-c', help='Configuration file')
def document(project_path, type, output, config):
    """
    Generate documentation automatically.
    
    Example:
        superagent document ./my_project --type readme
        superagent document ./my_project --type api --output docs/api.md
    """
    console.print(Panel.fit(
        f"[bold green]Documentation Generator[/bold green]\n"
        f"Project: {project_path}\n"
        f"Type: {type}",
        title="Auto Documentation"
    ))
    
    async def run():
        cfg = Config(config) if config else Config()
        
        async with SuperAgent(cfg) as agent:
            doc_gen = DocumentationGenerator(agent.llm)
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Generating documentation...", total=None)
                
                if type == 'readme':
                    result = await doc_gen.generate_readme(Path(project_path))
                    output_file = output or Path(project_path) / "README.md"
                elif type == 'api':
                    result = await doc_gen.generate_api_docs(Path(project_path))
                    result = str(result)  # Convert to string for display
                    output_file = output or Path(project_path) / "docs" / "API.md"
                elif type == 'tutorial':
                    result = await doc_gen.generate_tutorial(Path(project_path))
                    output_file = output or Path(project_path) / "TUTORIAL.md"
                elif type == 'openapi':
                    result = await doc_gen.generate_openapi_spec(Path(project_path))
                    result = str(result)
                    output_file = output or Path(project_path) / "openapi.yaml"
                
                progress.update(task, description="Complete!", completed=True)
            
            # Save result
            if output_file:
                Path(output_file).parent.mkdir(parents=True, exist_ok=True)
                Path(output_file).write_text(result if isinstance(result, str) else str(result))
                console.print(f"\n[green]✓ Documentation saved to: {output_file}[/green]")
            else:
                console.print(f"\n{result[:500]}...")
    
    asyncio.run(run())


@advanced.command()
@click.argument('project_path', type=click.Path(exists=True))
@click.argument('question')
@click.option('--config', '-c', help='Configuration file')
def query(project_path, question, config):
    """
    Query codebase using natural language.
    
    Example:
        superagent query ./my_project "Where is authentication implemented?"
        superagent query ./my_project "How does the caching work?"
    """
    console.print(Panel.fit(
        f"[bold blue]Codebase Query[/bold blue]\n"
        f"Question: {question}",
        title="AI Code Understanding"
    ))
    
    async def run():
        cfg = Config(config) if config else Config()
        
        async with SuperAgent(cfg) as agent:
            query_engine = CodebaseQueryEngine(agent.llm, agent.cache)
            
            # Index codebase
            console.print("\n[dim]Indexing codebase...[/dim]")
            await query_engine.index_codebase(Path(project_path))
            
            # Answer question
            console.print("[dim]Analyzing...[/dim]\n")
            result = await query_engine.query(question, Path(project_path))
            
            # Display answer
            console.print(Panel(
                result['answer'],
                title="Answer",
                style="green"
            ))
            
            # Show references
            if result.get('references'):
                console.print("\n[bold]References:[/bold]")
                for ref in result['references']:
                    console.print(f"  • {ref.get('file', '')}:{ref.get('line', '')} - {ref.get('description', '')}")
            
            # Show related
            if result.get('related'):
                console.print("\n[bold]Related:[/bold]")
                for item in result['related']:
                    console.print(f"  • {item}")
    
    asyncio.run(run())


@advanced.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--config', '-c', help='Configuration file')
def profile(file_path, config):
    """
    Profile code performance and get optimization suggestions.
    
    Example:
        superagent profile ./src/slow_function.py
    """
    console.print(Panel.fit(
        f"[bold yellow]Performance Profiler[/bold yellow]\n"
        f"File: {file_path}",
        title="Performance Analysis"
    ))
    
    async def run():
        cfg = Config(config) if config else Config()
        
        async with SuperAgent(cfg) as agent:
            profiler = PerformanceProfiler(agent.llm)
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Profiling code...", total=None)
                
                result = await profiler.profile_file(Path(file_path))
                
                progress.update(task, description="Complete!", completed=True)
            
            # Display bottlenecks
            if result.get('bottlenecks'):
                table = Table(title="Performance Bottlenecks")
                table.add_column("Function", style="cyan")
                table.add_column("Time (s)", style="yellow")
                table.add_column("Severity", style="red")
                
                for bottleneck in result['bottlenecks']:
                    table.add_row(
                        bottleneck['function'][:50],
                        f"{bottleneck['time']:.3f}",
                        bottleneck['severity']
                    )
                
                console.print(table)
            
            # Display suggestions
            if result.get('suggestions'):
                console.print("\n[bold]Optimization Suggestions:[/bold]")
                for sug in result['suggestions']:
                    impact = sug.get('impact', 'medium')
                    color = 'red' if impact == 'high' else 'yellow' if impact == 'medium' else 'green'
                    console.print(f"  [{color}]●[/{color}] {sug.get('suggestion', '')}")
    
    asyncio.run(run())


if __name__ == "__main__":
    advanced()





