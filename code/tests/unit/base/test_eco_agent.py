import pytest
import agentpy as ap
from unittest.mock import Mock
from mc_ab_sfc.base import EcoAgent


def test_is_agentpy_agent():
    # Assert
    assert issubclass(EcoAgent, ap.Agent)


def test_contains_roles_collection():
    # Given
    model = Mock()
    agent = EcoAgent(model)

    # Assert
    assert isinstance(agent.roles, dict)


def test_has_update_history_method():
    # Given
    model = Mock()
    agent = EcoAgent(model)

    # Assert
    assert callable(agent.update_history)
