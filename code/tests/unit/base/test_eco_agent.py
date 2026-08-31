import pytest
import agentpy as ap
from unittest.mock import Mock
from mc_ab_sfc2.base import EcoAgent


def test_is_agentpy_agent():
    # Assert
    assert issubclass(EcoAgent, ap.Agent)


def test_contains_roles_collection():
    # Given
    model = Mock()
    agent = EcoAgent(model)

    # Assert
    assert isinstance(agent.roles, dict)
