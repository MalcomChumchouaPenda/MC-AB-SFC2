import pytest
import agentpy as ap
from unittest.mock import Mock
from mcabsfc.base import EcoRole


def test_is_agentnode():
    # Assert
    assert issubclass(EcoRole, ap.AgentNode)


def test_requires_owner_and_space():
    # Assert
    expected = "required positional arguments: 'owner' and 'space'"
    with pytest.raises(TypeError, match=expected):
        EcoRole()


def test_has_owner_and_space_reference():
    # Given
    agent = Mock(id=1)
    space = Mock()
    role = EcoRole(agent, space)

    # Assert
    assert role.owner is agent
    assert role.space is space



def test_has_generated_label():
    # Given
    agent = Mock(id=1)
    space = Mock()
    role = EcoRole(agent, space)

    # Assert
    assert role.label == agent.id
