import pytest
from dataclasses import dataclass
from unittest.mock import Mock
from networkx import DiGraph
import agentpy as ap
from mc_ab_sfc.base import EcoSpace


# ---------------------------------------------------
# ARCHITECTURAL TESTS
# ----------------------------------------------------


def test_is_agentpy_network():
    # Assert
    assert issubclass(EcoSpace, ap.Network)


def test_contains_roles_collection():
    # Given
    model = Mock()
    space = EcoSpace(model)

    # Assert
    assert isinstance(space.roles, dict)



def test_has_directed_graph():
    # Given
    model = Mock()
    space = EcoSpace(model)

    # Assert
    assert isinstance(space.graph, DiGraph)


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


@dataclass(frozen=True)
class FakeRole:
    owner: object = None
    space: object = None
    label: int = 2


def test_add_role_creates_role(agent, space):
    # Given
    key = 'fake_role'

    # When
    role = space.add_role(FakeRole, agent, key)

    # Then
    assert isinstance(role, FakeRole)
    assert role.owner is agent
    assert role.space is space


def test_add_role_creates_node(agent, space):
    # Given
    key = 'fake_role'

    # When
    role = space.add_role(FakeRole, agent, key)

    # Then
    assert role in space.nodes
    


def test_add_role_registers_role(agent, space):
    # Given
    key = 'fake_role'

    # When
    role = space.add_role(FakeRole, agent, key)

    # Then
    assert role is agent.roles["fake_role"]
    
