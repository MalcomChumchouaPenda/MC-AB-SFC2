import pytest
from agentpy import Agent
from unittest.mock import Mock
from model.base import EcoAgent

# ---------------------------------------------------
# ARCHITECTURE TESTS
# ----------------------------------------------------


def test_is_agentpy_agent():
    # Assert
    assert issubclass(EcoAgent, Agent)


@pytest.fixture
def agent_before_setup():
    # Given
    model = Mock()
    agent = EcoAgent(model)
    return agent


def test_has_roles_dict(agent_before_setup):
    # Given
    agent = agent_before_setup

    # When
    agent.setup()

    # Assert
    assert agent.roles == {}


def test_has_account_ref(agent_before_setup):
    # Given
    agent = agent_before_setup

    # When
    agent.setup()

    # Assert
    assert agent.account is None


def test_has_central_bank_account_ref(agent_before_setup):
    # Given
    agent = agent_before_setup

    # When
    agent.setup()

    # Assert
    assert agent.cb_account is None


def test_has_deposit_bank_account_ref(agent_before_setup):
    # Given
    agent = agent_before_setup

    # When
    agent.setup()

    # Assert
    assert agent.bank_account is None
