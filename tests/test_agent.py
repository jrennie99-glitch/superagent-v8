"""Tests for core agent functionality."""

import pytest
import asyncio
from pathlib import Path
from superagent.core.agent import SuperAgent
from superagent.core.config import Config


@pytest.fixture
def config():
    """Create test configuration."""
    return Config()


@pytest.fixture
async def agent(config, tmp_path):
    """Create test agent."""
    agent = SuperAgent(config, workspace=str(tmp_path))
    await agent.initialize()
    yield agent
    await agent.shutdown()


@pytest.mark.asyncio
async def test_agent_initialization(agent):
    """Test agent initializes correctly."""
    assert agent is not None
    assert agent.llm is not None
    assert agent.cache is not None
    assert agent.code_generator is not None


@pytest.mark.asyncio
async def test_execute_simple_instruction(agent):
    """Test executing a simple instruction."""
    instruction = "Create a Python function that adds two numbers"
    result = await agent.execute_instruction(instruction)
    
    assert result['success'] is True
    assert result['project'] is not None
    assert len(result['results']) > 0


@pytest.mark.asyncio
async def test_project_creation(agent, tmp_path):
    """Test project creation and setup."""
    project_name = "test_project"
    await agent._setup_project(project_name)
    
    project_path = tmp_path / project_name
    assert project_path.exists()
    assert project_path.is_dir()


@pytest.mark.asyncio
async def test_stats_tracking(agent):
    """Test statistics are tracked correctly."""
    stats = agent._get_stats()
    
    assert 'llm_stats' in stats
    assert 'iteration_count' in stats
    assert stats['iteration_count'] >= 0


def test_project_name_generation(agent):
    """Test project name generation from instruction."""
    instruction = "Create a REST API with Authentication"
    name = agent._generate_project_name(instruction)
    
    assert isinstance(name, str)
    assert len(name) > 0
    assert ' ' not in name





