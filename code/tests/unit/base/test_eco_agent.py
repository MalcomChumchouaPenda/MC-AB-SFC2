import pytest
from model.base import EcoAgent
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
