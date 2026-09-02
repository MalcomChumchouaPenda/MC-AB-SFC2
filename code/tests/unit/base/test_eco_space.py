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



def test_add_role_creates_and_setup_role(space):
    # Given
    agent = Mock(roles={})
    FakeRole = Mock()

    # When
    role = space.add_role(FakeRole, agent)

    # Then
    FakeRole.assert_called_with(space.model)
    role.setup.assert_called_once_with()
    assert role is FakeRole.return_value


def test_add_role_link_role_to_agent_and_space(space):
    # Given
    agent = Mock(roles={})
    FakeRole = Mock()

    # When
    role = space.add_role(FakeRole, agent)

    # Then
    assert role.space is space
    assert role.agent is agent


def test_add_role_registers_role_with_name(space):
    # Given
    agent = Mock(roles={})
    role = Mock()
    role.name = "fake"
    FakeRole = Mock(return_value=role)

    # When
    role = space.add_role(FakeRole, agent)

    # Then
    print(agent.roles)
    assert role is agent.roles["fake"]

    
def test_add_role_add_graph_node(space):
    # Given
    agent = Mock(roles={})
    FakeRole = Mock()

    # When
    role = space.add_role(FakeRole, agent)

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
def space_with_role():
    # Given
    space = EcoSpace(model=Mock())
    space.setup()
    role, agent = Mock(), Mock()
    role.agent = agent
    role.name = "fake"
    agent.roles = {"fake":role}
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


def test_remove_role_unlink_role_to_agent_and_space(space_with_role):
    # Given
    space, role, _ = space_with_role

    # When
    space.remove_role(role)

    # Then
    assert role.space is None
    assert role.agent is None

    