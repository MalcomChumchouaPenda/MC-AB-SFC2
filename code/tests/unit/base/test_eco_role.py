import pytest
from agentpy.objects import Object
from unittest.mock import Mock
from model.base import EcoRole


def test_is_agentpy_object():
    # Assert
    assert issubclass(EcoRole, Object)


@pytest.fixture
def role():
    # Given
    model = Mock()
    role = EcoRole(model)
    return role


def test_has_default_name_attr(role):
    # When
    role.setup()

    # Assert
    assert role.name == ''


def test_has_default_agent_ref(role):
    # When
    role.setup()

    # Assert
    assert role.agent is None


def test_has_default_space_ref(role):
    # When
    role.setup()

    # Assert
    assert role.space is None

