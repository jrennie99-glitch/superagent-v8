"""Tests for advanced debugger."""

import pytest
from pathlib import Path
import ast
from superagent.modules.debugger import AdvancedDebugger
from superagent.core.llm import LLMProvider
from superagent.core.config import DebuggingConfig


@pytest.fixture
def llm():
    """Create LLM provider."""
    return LLMProvider("test_key")


@pytest.fixture
def config():
    """Create debugging config."""
    return DebuggingConfig()


@pytest.fixture
def debugger(llm, config):
    """Create debugger instance."""
    return AdvancedDebugger(llm, config)


def test_error_patterns_loaded(debugger):
    """Test error patterns are loaded."""
    assert len(debugger.error_patterns) > 0
    assert "NameError" in debugger.error_patterns
    assert "TypeError" in debugger.error_patterns


@pytest.mark.asyncio
async def test_analyze_valid_file(debugger, tmp_path):
    """Test analyzing a valid Python file."""
    code = '''
def add(a, b):
    """Add two numbers."""
    return a + b
'''
    
    file_path = tmp_path / "valid.py"
    file_path.write_text(code)
    
    results = await debugger.analyze_file(file_path)
    
    # Valid code should have minimal issues
    assert isinstance(results, dict)
    assert "errors" in results


@pytest.mark.asyncio
async def test_analyze_syntax_error(debugger, tmp_path):
    """Test analyzing file with syntax error."""
    code = '''
def broken_function(
    print("Missing closing parenthesis")
'''
    
    file_path = tmp_path / "broken.py"
    file_path.write_text(code)
    
    results = await debugger.analyze_file(file_path)
    
    assert len(results["errors"]) > 0
    assert results["errors"][0]["type"] == "SyntaxError"


def test_check_code_smells(debugger):
    """Test code smell detection."""
    code = '''
def very_long_function(a, b, c, d, e, f, g):
    """Function with too many parameters."""
    line1 = 1
    line2 = 2
    # ... imagine 50+ more lines
    return a + b
'''
    
    tree = ast.parse(code)
    smells = debugger._check_code_smells(tree, code)
    
    # Should detect too many parameters
    assert len(smells) > 0


def test_extract_error_context(debugger, tmp_path):
    """Test error context extraction."""
    code = '''line 1
line 2
line 3 with error
line 4
line 5'''
    
    file_path = tmp_path / "test.py"
    file_path.write_text(code)
    
    error = {"file": str(file_path), "line": 3}
    context = debugger._extract_error_context(error)
    
    assert "line 3" in context
    assert ">>>" in context  # Error marker


def test_complexity_summary(debugger):
    """Test complexity summary calculation."""
    data = [
        {
            "file": "test1.py",
            "complexity": [
                {"name": "func1", "complexity": 5},
                {"name": "func2", "complexity": 3}
            ]
        },
        {
            "file": "test2.py",
            "complexity": [
                {"name": "func3", "complexity": 7}
            ]
        }
    ]
    
    summary = debugger._summarize_complexity(data)
    
    assert summary["total_files"] == 2
    assert summary["total_functions"] == 3
    assert summary["average_complexity"] == (5 + 3 + 7) / 3





