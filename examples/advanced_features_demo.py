"""Demonstration of SuperAgent advanced features."""

import asyncio
from pathlib import Path
from superagent import SuperAgent, Config
from superagent.modules.code_reviewer import CodeReviewer
from superagent.modules.refactoring_engine import RefactoringEngine
from superagent.modules.doc_generator import DocumentationGenerator
from superagent.modules.codebase_query import CodebaseQueryEngine
from superagent.modules.performance_profiler import PerformanceProfiler
from superagent.modules.plugin_system import PluginManager, FormatterPlugin


async def main():
    """
    Demonstrate all advanced features of SuperAgent.
    
    This example showcases:
    1. Code Review with security analysis
    2. Intelligent Refactoring
    3. Automatic Documentation
    4. Natural Language Querying
    5. Performance Profiling
    6. Plugin System
    """
    
    print("=" * 60)
    print("SuperAgent Advanced Features Demo")
    print("=" * 60)
    
    config = Config()
    
    async with SuperAgent(config, workspace="./demo_workspace") as agent:
        
        # Create sample project
        print("\n1. Creating sample project...")
        result = await agent.execute_instruction(
            "Create a Python module with a function that calculates fibonacci numbers"
        )
        print(f"✓ Project created: {result['project']}")
        
        project_path = Path(agent.workspace) / result['project']
        
        # Find the generated Python file
        py_files = list(project_path.rglob("*.py"))
        if not py_files:
            print("No Python files found in project")
            return
        
        sample_file = py_files[0]
        print(f"✓ Sample file: {sample_file}")
        
        # 2. CODE REVIEW
        print("\n2. Performing AI Code Review...")
        reviewer = CodeReviewer(agent.llm)
        review = await reviewer.review_file(sample_file)
        
        print(f"   Grade: {review['overall_grade']}")
        print(f"   Security Score: {review['scores']['security']:.1f}/100")
        print(f"   Quality Score: {review['scores']['quality']:.1f}/100")
        
        if review.get('security'):
            print(f"   Security Issues: {len(review['security'])}")
        
        if review.get('ai_suggestions'):
            print(f"   AI Suggestions: {len(review['ai_suggestions'])}")
            if review['ai_suggestions']:
                print(f"     • {review['ai_suggestions'][0].get('suggestion', '')[:80]}...")
        
        # 3. REFACTORING
        print("\n3. Analyzing for Refactoring Opportunities...")
        refactor_engine = RefactoringEngine(agent.llm)
        refactorings = await refactor_engine.suggest_refactorings(sample_file)
        
        if refactorings:
            print(f"   Found {len(refactorings)} refactoring suggestions")
            for i, ref in enumerate(refactorings[:2], 1):
                print(f"   {i}. {ref.get('type', '')}: {ref.get('description', '')[:60]}...")
        else:
            print("   ✓ No refactorings needed - code looks great!")
        
        # 4. DOCUMENTATION GENERATION
        print("\n4. Generating Documentation...")
        doc_gen = DocumentationGenerator(agent.llm)
        
        # Generate README
        readme = await doc_gen.generate_readme(project_path)
        readme_path = project_path / "README_GENERATED.md"
        readme_path.write_text(readme)
        print(f"   ✓ README generated: {readme_path}")
        
        # Extract API docs
        api_docs = await doc_gen.generate_api_docs(project_path)
        print(f"   ✓ Found {len(api_docs['functions'])} functions")
        print(f"   ✓ Found {len(api_docs['classes'])} classes")
        
        # 5. CODEBASE QUERYING
        print("\n5. Natural Language Codebase Querying...")
        query_engine = CodebaseQueryEngine(agent.llm, agent.cache)
        
        # Index the codebase
        await query_engine.index_codebase(project_path)
        print(f"   ✓ Indexed {len(query_engine.index['functions'])} functions")
        
        # Ask a question
        question = "What functions are implemented in this project?"
        answer = await query_engine.query(question, project_path)
        print(f"   Question: {question}")
        print(f"   Answer: {answer['answer'][:100]}...")
        
        # 6. PERFORMANCE PROFILING
        print("\n6. Performance Profiling...")
        profiler = PerformanceProfiler(agent.llm)
        
        # Create a test function to profile
        test_code = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# Calculate fibonacci of 20
result = fibonacci(20)
"""
        
        # Benchmark
        benchmark = await profiler.benchmark_code(test_code, iterations=10)
        print(f"   Average execution time: {benchmark['avg_time']*1000:.2f}ms")
        print(f"   Min time: {benchmark['min_time']*1000:.2f}ms")
        print(f"   Max time: {benchmark['max_time']*1000:.2f}ms")
        
        # 7. PLUGIN SYSTEM
        print("\n7. Plugin System...")
        plugin_mgr = PluginManager()
        
        # Load built-in plugins
        formatter_plugin = FormatterPlugin()
        await plugin_mgr.load_plugin(FormatterPlugin, agent)
        
        print(f"   ✓ Loaded plugins: {', '.join(p['name'] for p in plugin_mgr.list_plugins())}")
        
        # Test formatter plugin
        unformatted_code = "def test( x,y ):return x+y"
        # formatted = await plugin_mgr.execute_plugin("formatter", unformatted_code)
        print("   ✓ Formatter plugin ready")
        
        # 8. SUMMARY
        print("\n" + "=" * 60)
        print("Demo Complete! Advanced Features Demonstrated:")
        print("=" * 60)
        print("✓ AI-Powered Code Review (Security + Quality)")
        print("✓ Intelligent Refactoring Suggestions")
        print("✓ Automatic Documentation Generation")
        print("✓ Natural Language Codebase Querying")
        print("✓ Performance Profiling & Benchmarking")
        print("✓ Extensible Plugin System")
        print("\nSuperAgent is truly superb! 🚀")
        print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())





