"""Tests for multi-agent system."""

import pytest
from superagent.core.multi_agent import (
    MultiAgentOrchestrator,
    SpecializedAgent,
    AgentRole
)
from superagent.core.config import Config


@pytest.fixture
def config():
    """Create test configuration."""
    return Config()


@pytest.fixture
def orchestrator(config):
    """Create multi-agent orchestrator."""
    return MultiAgentOrchestrator(config, num_agents=4)


def test_orchestrator_initialization(orchestrator):
    """Test orchestrator initializes correctly."""
    assert len(orchestrator.agents) == 4
    assert orchestrator.num_agents == 4


def test_agent_roles_assigned(orchestrator):
    """Test agents have different roles."""
    roles = [agent.role for agent in orchestrator.agents]
    
    # Should have variety of roles
    assert AgentRole.CODER in roles
    assert AgentRole.DEBUGGER in roles
    assert AgentRole.TESTER in roles
    assert AgentRole.REVIEWER in roles


def test_specialized_agent_creation():
    """Test specialized agent creation."""
    from superagent.core.llm import LLMProvider
    
    llm = LLMProvider("test_key")
    agent = SpecializedAgent(AgentRole.CODER, llm, 0)
    
    assert agent.role == AgentRole.CODER
    assert agent.agent_id == 0
    assert agent.tasks_completed == 0
    assert agent.active is True


@pytest.mark.asyncio
async def test_execute_tasks(orchestrator):
    """Test executing multiple tasks."""
    tasks = [
        {"type": "code", "description": "Write function 1", "context": {}},
        {"type": "test", "description": "Test function 1", "context": {}},
        {"type": "review", "description": "Review code", "context": {}}
    ]
    
    # Note: This would require mocking the LLM in a real test
    # results = await orchestrator.execute_tasks(tasks)
    # assert len(results) == len(tasks)


def test_get_stats(orchestrator):
    """Test statistics retrieval."""
    stats = orchestrator.get_stats()
    
    assert "total_agents" in stats
    assert "tasks_completed" in stats
    assert "agent_breakdown" in stats
    assert stats["total_agents"] == 4


def test_task_prompt_creation():
    """Test task-specific prompt creation."""
    from superagent.core.llm import LLMProvider
    
    llm = LLMProvider("test_key")
    agent = SpecializedAgent(AgentRole.CODER, llm, 0)
    
    task = {
        "type": "code",
        "description": "Create a function",
        "context": {"language": "python"}
    }
    
    prompt = agent._create_task_prompt(task)
    
    assert "Create a function" in prompt
    assert isinstance(prompt, str)





