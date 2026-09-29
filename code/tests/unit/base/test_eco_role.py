import pytest
from unittest.mock import Mock
from model.base import EcoRole

# ---------------------------------------------------
# ARCHITECTURE
# ----------------------------------------------------


def test_inherits_from_agentpy_agentnode():
    # Given
    from agentpy import AgentNode

    # When
    is_derived = issubclass(EcoRole, AgentNode)

    # Then
    assert is_derived


def test_requires_agent_and_env():
    # Given
    required = "'agent' and 'env'"

    #  When
    with pytest.raises(TypeError) as error:
        EcoRole()

    # Then
    assert required in str(error)


def test_initializes_agent():
    # Given
    agent, env = Mock(), Mock()

    # When
    role = EcoRole(agent, env)

    # Then
    assert role.agent is agent


def test_initializes_env():
    # Given
    agent, env = Mock(), Mock()

    # When
    role = EcoRole(agent, env)

    # Then
    assert role.env is env


def test_initializes_label_with_agent_id():
    # Given
    agent, env = Mock(), Mock()

    # When
    role = EcoRole(agent, env)

    # Then
    assert role.label == agent.id


def test_initializes_name():
    # Given
    agent, env = Mock(), Mock()

    # When
    role = EcoRole(agent, env)

    # Then
    assert role.name == ""


def test_initializes_group():
    # Given
    agent, env = Mock(), Mock()

    # When
    role = EcoRole(agent, env)

    # Then
    assert role.group == ""


def test_expose_agent_id():
    # Given
    agent, env = Mock(), Mock()
    role = EcoRole(agent, env)

    # When
    exposed = role.id

    # Then
    assert exposed is agent.id


def test_expose_agent_central_bank_id():
    # Given
    agent, env = Mock(), Mock()
    role = EcoRole(agent, env)

    # When
    exposed = role.cb_id

    # Then
    assert exposed is agent.cb_id


def test_expose_agent_deposit_demander_id():
    # Given
    agent, env = Mock(), Mock()
    role = EcoRole(agent, env)

    # When
    exposed = role.bank_id

    # Then
    assert exposed is agent.bank_id


def test_change_agent_deposit_demander_id():
    # Given
    agent, env = Mock(), Mock()
    role = EcoRole(agent, env)

    # When
    role.bank_id = 2

    # Then
    assert agent.bank_id == 2


def test_expose_agent_country_id():
    # Given
    agent, env = Mock(), Mock()
    role = EcoRole(agent, env)

    # When
    agent.country_id = 2

    # Then
    assert role.country_id == 2
