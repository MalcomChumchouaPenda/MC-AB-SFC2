import pytest
from agentpy.objects import Object
from unittest.mock import Mock
from model.base import EcoRole


def test_is_not_agentpy_object():
    # Assert
    assert not issubclass(EcoRole, Object)


def test_has_default_name_attr():
    # Assert
    assert EcoRole.name == ''


def test_requires_agent_and_space():
    # Assert
    expected = "required positional arguments: 'agent' and 'space'"
    with pytest.raises(TypeError, match=expected):
        EcoRole()


def test_has_agent_and_space_refs():
    # Given
    agent = Mock()
    space = Mock()
    role = EcoRole(agent, space)

    # Assert
    assert role.agent is agent
    assert role.space is space

