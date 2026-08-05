
import pytest
import agentpy as ap
from unittest.mock import Mock
from mcabsfc.base import EcoAgent


@pytest.fixture
def model():
    return Mock()


def test_is_agentpy_agent(model):
    # When 
    agent = EcoAgent(model)

    # Then
    assert isinstance(agent, ap.Agent)


def test_contains_roles_collection(model):
    # When 
    agent = EcoAgent(model)

    # Then
    assert isinstance(agent.roles, dict)
