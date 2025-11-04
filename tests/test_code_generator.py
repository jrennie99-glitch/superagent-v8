"""Tests for code generator module."""

import pytest
from pathlib import Path
from superagent.modules.code_generator import CodeGenerator
from superagent.core.llm import LLMProvider
from superagent.core.cache import CacheManager


@pytest.fixture
def llm():
    """Create LLM provider mock."""
    # In real tests, use a mock
    return LLMProvider("test_key", model="claude-3-5-sonnet-20241022")


@pytest.fixture
def cache(tmp_path):
    """Create cache manager."""
    return CacheManager(cache_dir=str(tmp_path / ".cache"))


@pytest.fixture
def generator(llm, cache):
    """Create code generator."""
    return CodeGenerator(llm, cache)


def test_language_detection(generator):
    """Test programming language detection."""
    files = ["test.py", "main.py"]
    lang = generator._detect_language(files)
    assert lang == "python"
    
    files = ["index.js", "app.js"]
    lang = generator._detect_language(files)
    assert lang == "javascript"
    
    files = ["Main.java"]
    lang = generator._detect_language(files)
    assert lang == "java"


def test_code_cleaning(generator):
    """Test generated code cleaning."""
    code_with_markdown = '''```python
def hello():
    print("Hello")
```'''
    
    cleaned = generator._clean_generated_code(code_with_markdown)
    assert "```" not in cleaned
    assert "def hello():" in cleaned


def test_language_configs(generator):
    """Test language configurations are loaded."""
    assert "python" in generator.language_configs
    assert "javascript" in generator.language_configs
    assert generator.language_configs["python"]["extension"] == ".py"
    assert generator.language_configs["javascript"]["extension"] == ".js"


@pytest.mark.asyncio
async def test_generation_prompt_creation(generator):
    """Test generation prompt creation."""
    prompt = generator._create_generation_prompt(
        "api/routes.py",
        "Create REST API routes",
        "python"
    )
    
    assert "python" in prompt.lower()
    assert "routes.py" in prompt
    assert "REST API" in prompt





