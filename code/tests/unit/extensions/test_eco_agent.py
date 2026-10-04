import pytest
from model.extensions import EcoAgent
from unittest.mock import Mock

# ---------------------------------------------------
# ARCHITECTURE
# ----------------------------------------------------


def test_inherits_from_agentpy_agent():
    # Given
    from agentpy import Agent

    # When
    is_derived = issubclass(EcoAgent, Agent)

    # Then
    assert is_derived


@pytest.fixture
def agent():
    # Given
    model = Mock()
    agent = EcoAgent(model)
    return agent


def test_initializes_roles_dict(fake_model):
    # Given
    model = fake_model

    # When
    agent = EcoAgent(model)

    # Then
    assert agent.roles == {}


def test_initializes_account(fake_model):
    # Given
    model = fake_model

    # When
    agent = EcoAgent(model)

    # Then
    assert agent.account is None


def test_initializes_country_pos(fake_model):
    # Given
    model = fake_model

    # When
    agent = EcoAgent(model)

    # Then
    assert agent.country_pos == 0
