import pytest
import agentpy as ap
from unittest.mock import Mock
from mcabsfc.base import EcoAgent


def test_is_agentpy_agent():
    # Assert
    assert issubclass(EcoAgent, ap.Agent)


def test_contains_roles_collection():
    # Arrange
    model = Mock()
    agent = EcoAgent(model)

    # Assert
    assert isinstance(agent.roles, dict)
