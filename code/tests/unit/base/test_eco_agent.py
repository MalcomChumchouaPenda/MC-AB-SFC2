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
def agent():
    # Given
    model = Mock()
    agent = EcoAgent(model)
    return agent


def test_has_roles_dict(agent):
    # Assert
    assert agent.roles == {}


def test_has_account_ref(agent):
    # Assert
    assert agent.account is None


def test_has_central_bank_id_ref(agent):
    # Assert
    assert agent.cb_id is None


def test_has_deposit_bank_id_ref(agent):
    # Assert
    assert agent.bank_id is None


def test_has_default_country_id(agent):
    # Assert
    assert agent.country_id == 0
