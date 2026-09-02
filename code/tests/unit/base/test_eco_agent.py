import pytest
from agentpy import Agent
from unittest.mock import Mock
from model.base import EcoAgent


def test_is_agentpy_agent():
    # Assert
    assert issubclass(EcoAgent, Agent)


@pytest.fixture
def agent():
    # Given
    model = Mock()
    agent = EcoAgent(model)
    return agent


def test_contains_roles_collection(agent):
    # When
    agent.setup()

    # Assert
    assert isinstance(agent.roles, dict)


