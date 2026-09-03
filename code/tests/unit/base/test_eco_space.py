import pytest
from unittest.mock import Mock
from agentpy import Network, AgentDList
from model.base import EcoSpace

# ---------------------------------------------------
# ARCHITECTURE TESTS
# ----------------------------------------------------


def test_is_agentpy_network():
    # Assert
    assert issubclass(EcoSpace, Network)


@pytest.fixture
def space_before_setup():
    # Given
    model = Mock()
    space = EcoSpace(model)
    return space


def test_has_root_space_ref(space_before_setup):
    # Given
    space = space_before_setup

    # When
    space.setup()

    # Then
    assert space.root_space is None


def test_has_sub_spaces_dict(space_before_setup):
    # Given
    space = space_before_setup

    # When
    space.setup()

    # Then
    assert space.sub_spaces == {}


def test_has_accounts_dlist(space_before_setup):
    # Given
    space = space_before_setup

    # When
    space.setup()

    # Then
    assert isinstance(space.accounts, AgentDList)


# ---------------------------------------------------
# SUB SPACES MANAGEMENT TESTS
# ----------------------------------------------------


@pytest.fixture
def space_with_sub_spaces(space_before_setup):
    # Given
    sub_spaces = {}
    space = space_before_setup
    space.sub_spaces = sub_spaces
    return space, sub_spaces


def test_add_space_register_sub_space(space_with_sub_spaces):
    # Given
    space, sub_spaces = space_with_sub_spaces
    new_space = Mock(root_space=None)

    # When
    space.add_space(new_space, "fake_market")

    # Then
    assert sub_spaces["fake_market"] == new_space
    assert space is new_space.root_space


# ---------------------------------------------------
# ACCOUNT MANAGEMENT TESTS
# ----------------------------------------------------

FakeAccount = Mock()


@pytest.fixture
def space_with_accounts(monkeypatch, space_before_setup):
    # Given
    accounts = []
    space = space_before_setup
    space.accounts = accounts
    monkeypatch.setattr("model.base.EcoAccount", FakeAccount)
    return space, accounts


def test_add_account_create_new_account(space_with_accounts):
    # Given
    agent = Mock()
    space, _ = space_with_accounts

    # When
    account = space.add_account(agent)

    # Then
    FakeAccount.assert_called_with(agent.model)
    assert account is FakeAccount.return_value


def test_add_account_register_new_account(space_with_accounts):
    # Given
    agent = Mock()
    space, accounts = space_with_accounts

    # When
    account = space.add_account(agent)

    # Then
    assert account in accounts
    assert account is agent.account
    assert account.agent_id == agent.id


# ---------------------------------------------------
# EVOLUTION TESTS
# ----------------------------------------------------

@pytest.fixture
def space_before_evolution(space_with_sub_spaces):
    # Given
    space, _ = space_with_sub_spaces
    space.update_state = Mock()
    space.clear_defaults = Mock()
    return space


def test_evolve_update_all_state(space_before_evolution):
    # Given
    sub_space = Mock()
    space = space_before_evolution
    space.sub_spaces["fake_market"] = sub_space

    # When
    space.evolve()

    # Then
    space.update_state.assert_called_once()
    sub_space.update_state.assert_called_once()


def test_evolve_clear_all_defaults(space_before_evolution):
    # Given
    sub_space = Mock()
    space = space_before_evolution
    space.sub_spaces["fake_market"] = sub_space

    # When
    space.evolve()

    # Then
    space.clear_defaults.assert_called_once()
    sub_space.clear_defaults.assert_called_once()


def test_update_state_is_not_implemented(space_before_setup):
    # Given
    space = space_before_setup

    # Assert
    with pytest.raises(NotImplementedError):
        space.update_state()


def test_clear_defaults_is_not_implemented(space_before_setup):
    # Given
    space = space_before_setup

    # Assert
    with pytest.raises(NotImplementedError):
        space.clear_defaults()

# ---------------------------------------------------
# ROLE MANAGEMENT TESTS
# ----------------------------------------------------

@pytest.fixture
def role_with_kind():
    # Given
    role = Mock()
    role_kind = Mock(return_value=role)
    return role, role_kind


def test_add_role_creates_role(space_before_setup, role_with_kind):
    # Given
    role, role_kind = role_with_kind
    space = space_before_setup
    agent = Mock(roles={})

    # When
    space.add_role(role_kind, agent, "fake_role")

    # Then
    role_kind.assert_called_with(space.model)
    role.setup.assert_called_with()
    assert role.space is space
    assert role.agent is agent


def test_add_role_returns_role(space_before_setup, role_with_kind):
    # Given
    role, role_kind = role_with_kind
    space = space_before_setup
    agent = Mock(roles={})

    # When
    result = space.add_role(role_kind, agent, "fake_role")

    # Then
    assert result is role


def test_add_role_add_graph_node(space_before_setup, role_with_kind):
    # Given
    role, role_kind = role_with_kind
    space = space_before_setup
    agent = Mock(roles={})
    graph = space.graph

    # When
    space.add_role(role_kind, agent, "fake_role")

    # Then
    assert graph.has_node(role)


def test_add_role_registers_role(space_before_setup, role_with_kind):
    # Given
    role, role_kind = role_with_kind
    space = space_before_setup
    agent = Mock(roles={})

    # When
    space.add_role(role_kind, agent, "fake_role")

    # Then
    assert role.name == "fake_role"
    assert agent.roles["fake_role"] is role


@pytest.fixture
def space_with_role(space_before_setup):
    # Given
    agent, role = Mock(), Mock()
    space = space_before_setup
    space.graph.add_node(role)
    agent.roles = {"fake_role": role}
    role.name = "fake_role"
    role.agent = agent
    return space, role


def test_remove_role_remove_graph_node(space_with_role):
    # Given
    space, role = space_with_role
    graph = space.graph

    # When
    space.remove_role(role)

    # Then
    assert not graph.has_node(role)


def test_remove_role_un_registers_role(space_with_role):
    # Given
    space, role = space_with_role
    agent = role.agent

    # When
    space.remove_role(role)

    # Then
    assert len(agent.roles) == 0
