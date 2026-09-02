import pytest
from unittest.mock import Mock
from networkx import DiGraph, Graph
from agentpy.objects import Object
from model.base import EcoSpace

# ---------------------------------------------------
# ARCHITECTURE TESTS
# ----------------------------------------------------


def test_is_agentpy_object():
    # Assert
    assert issubclass(EcoSpace, Object)



# ---------------------------------------------------
# BEHAVIORAL TESTS
# ----------------------------------------------------


@pytest.fixture
def space():
    # Given
    model = Mock()
    return EcoSpace(model)


@pytest.fixture
def agent():
    # Given
    return Mock(id=1, roles={})


def test_add_role_creates_role(agent, space):
    # Given
    key = "fake_role"
    fake_cls = Mock()
    model = space.model

    # When
    role = space.add_role(fake_cls, agent, key)

    # Then
    fake_cls.assert_called_with(model, agent.id, space)
    assert role is fake_cls.return_value


def test_add_role_registers_role(agent, space):
    # Given
    key = "fake_role"
    fake_cls = Mock()

    # When
    role = space.add_role(fake_cls, agent, key)

    # Then
    assert role is agent.roles["fake_role"]
