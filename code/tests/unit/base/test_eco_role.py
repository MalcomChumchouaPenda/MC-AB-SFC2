import pytest
from agentpy import AgentNode
from unittest.mock import Mock
from model.base import EcoRole

# ---------------------------------------------------
# ARCHITECTURE TESTS
# ----------------------------------------------------


def test_inherits_from_agentpy_agentnode():
    # Assert
    assert issubclass(EcoRole, AgentNode)


def test_requires_agent_and_env():
    #  Assert
    with pytest.raises(TypeError, match="'agent' and 'env'"):
        EcoRole()


@pytest.fixture
def role_with_agent_and_env():
    # Given
    agent, env = Mock(), Mock()
    role = EcoRole(agent, env)
    return role, agent, env


def test_has_agent_ref(role_with_agent_and_env):
    # Given
    role, agent, _ = role_with_agent_and_env

    # Assert
    assert role.agent is agent


def test_has_env_ref(role_with_agent_and_env):
    # Given
    role, _, env = role_with_agent_and_env

    # Assert
    assert role.env is env


def test_has_label_attr(role_with_agent_and_env):
    # Given
    role, agent, _ = role_with_agent_and_env

    # Assert
    assert role.label == agent.id


def test_has_name_attr(role_with_agent_and_env):
    # Given
    role, *_ = role_with_agent_and_env

    # Assert
    assert role.name == ""


def test_expose_agent_id(role_with_agent_and_env):
    # Given
    role, agent, _ = role_with_agent_and_env

    # When
    exposed = role.id

    # Then
    assert exposed is agent.id


def test_expose_agent_central_bank_id(role_with_agent_and_env):
    # Given
    role, agent, _ = role_with_agent_and_env

    # When
    exposed = role.cb_id

    # Then
    assert exposed is agent.cb_id


def test_expose_agent_deposit_bank_id(role_with_agent_and_env):
    # Given
    role, agent, _ = role_with_agent_and_env

    # When
    exposed = role.bank_id

    # Then
    assert exposed is agent.bank_id


def test_change_agent_deposit_bank_id(role_with_agent_and_env):
    # Given
    role, agent, _ = role_with_agent_and_env
    new_account = Mock()

    # When
    role.bank_id = new_account

    # Then
    assert agent.bank_id is new_account


def test_expose_agent_country_id(role_with_agent_and_env):
    # Given
    role, agent, _ = role_with_agent_and_env

    # When
    agent.country_id = 2

    # Then
    assert role.country_id == 2
