import pytest
from unittest.mock import Mock
from model.extensions import EcoRole

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
    required = "'agent_id' and 'env'"

    #  When
    with pytest.raises(TypeError) as error:
        EcoRole()

    # Then
    assert required in str(error)


def test_initializes_agent():
    # Given
    env = Mock()
    agent_id = 1

    # When
    role = EcoRole(agent_id, env)

    # Then
    assert role.agent_id == agent_id


def test_initializes_env():
    # Given
    env = Mock()
    agent_id = 1

    # When
    role = EcoRole(agent_id, env)

    # Then
    assert role.env is env


def test_initializes_label_with_agent_id():
    # Given
    env = Mock()
    agent_id = 1

    # When
    role = EcoRole(agent_id, env)

    # Then
    assert role.label == agent_id


def test_initializes_id_with_agent_id():
    # Given
    env = Mock()
    agent_id = 1

    # When
    role = EcoRole(agent_id, env)

    # Then
    assert role.id is agent_id


def test_initializes_name():
    # Given
    env = Mock()
    agent_id = 1

    # When
    role = EcoRole(agent_id, env)

    # Then
    assert role.name == ""


def test_initializes_group():
    # Given
    env = Mock()
    agent_id = 1

    # When
    role = EcoRole(agent_id, env)

    # Then
    assert role.group == ""


def test_expose_agent_id():
    # Given
    env = Mock()
    agent_id = 1
    role = EcoRole(agent_id, env)

    # When
    exposed = role.id

    # Then
    assert exposed is agent_id
