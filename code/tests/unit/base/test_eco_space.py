import pytest
from unittest.mock import Mock
from networkx import Graph
from agentpy.objects import Object
from model.base import EcoSpace

# ---------------------------------------------------
# ARCHITECTURE TESTS
# ----------------------------------------------------


def test_is_agentpy_object():
    # Assert
    assert issubclass(EcoSpace, Object)


@pytest.fixture
def space():
    # Given
    model = Mock()
    space = EcoSpace(model)
    space.setup()
    return space


def test_has_graph(space):
    # Assert
    assert isinstance(space.graph, Graph)


# ---------------------------------------------------
# BEHAVIORAL TESTS
# ----------------------------------------------------



def test_add_role_creates_role(space):
    # Given
    agent = Mock(roles={})
    FakeRole = Mock()

    # When
    role = space.add_role(FakeRole, agent, "fake")

    # Then
    FakeRole.assert_called_with(agent, space)
    assert role is FakeRole.return_value


def test_add_role_registers_role(space):
    # Given
    agent = Mock(roles={})
    FakeRole = Mock()

    # When
    role = space.add_role(FakeRole, agent, 'fake')

    # Then
    print(agent.roles)
    assert role is agent.roles["fake"]

    
def test_add_role_add_graph_node(space):
    # Given
    agent = Mock(roles={})
    FakeRole = Mock()

    # When
    role = space.add_role(FakeRole, agent, 'fake')

    # Then
    assert space.graph.has_node(role)

    
@pytest.fixture
def role_and_agent():
    # Given
    agent, role = Mock(), Mock()
    agent.roles = {'fake':role}
    role.name = "fake"
    role.agent = agent
    return role, agent

@pytest.fixture
def space_with_role(role_and_agent):
    # Given
    role, agent = role_and_agent
    space = EcoSpace(model=Mock())
    space.setup()
    space.graph.add_node(role)
    return space, role, agent


def test_remove_role_unregisters_role(space_with_role):
    # Given
    space, role, agent = space_with_role

    # When
    space.remove_role(role)

    # Then
    assert len(agent.roles) == 0

    
def test_remove_role_remove_graph_node(space_with_role):
    # Given
    space, role, _ = space_with_role

    # When
    space.remove_role(role)

    # Then
    assert not space.graph.has_node(role)
