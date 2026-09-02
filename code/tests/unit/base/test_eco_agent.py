import pytest
from agentpy import Agent
from unittest.mock import Mock
from model.base import EcoAgent


def test_is_agentpy_agent():
    # Assert
    assert issubclass(EcoAgent, Agent)


def test_contains_roles_collection():
    # Given
    model = Mock()
    agent = EcoAgent(model)

    # Assert
    assert isinstance(agent.roles, dict)
