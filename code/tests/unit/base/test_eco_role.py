import pytest
from agentpy.objects import Object
from unittest.mock import Mock
from model.base import EcoRole


def test_is_agentpy_object():
    # Assert
    assert issubclass(EcoRole, Object)


def test_requires_model_agent_id_and_space():
    # Assert
    expected = "required positional arguments: 'model', 'agent_id', and 'space'"
    with pytest.raises(TypeError, match=expected):
        EcoRole()


def test_has_agent_id_and_space_reference():
    # Given
    model = Mock()
    space = Mock()
    role = EcoRole(model, 1, space)

    # Assert
    assert role.agent_id == 1
    assert role.space is space

