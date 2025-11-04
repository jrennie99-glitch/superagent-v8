"""Pytest configuration and fixtures."""

import pytest
import os
from pathlib import Path


def pytest_configure(config):
    """Configure pytest."""
    config.addinivalue_line(
        "markers", "benchmark: mark test as a benchmark test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )


@pytest.fixture(scope="session")
def test_api_key():
    """Provide test API key."""
    return os.getenv("ANTHROPIC_API_KEY", "test_key")


@pytest.fixture
def mock_llm_response():
    """Mock LLM response for testing."""
    return """
def add(a, b):
    '''Add two numbers.'''
    return a + b
"""


@pytest.fixture(autouse=True)
def reset_environment(monkeypatch):
    """Reset environment for each test."""
    # Set test environment variables
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test_key")
    monkeypatch.setenv("CACHE_ENABLED", "false")





