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


def test_has_env_ref(space_before_setup):
    # Given
    space = space_before_setup

    # When
    space.setup()

    # Then
    assert space.env is None


def test_has_sub_spaces_dict(space_before_setup):
    # Given
    space = space_before_setup

    # When
    space.setup()

    # Then
    assert space.spaces == {}


def test_has_accounts_dict(space_before_setup):
    # Given
    space = space_before_setup

    # When
    space.setup()

    # Then
    assert space.accounts == {}



# ---------------------------------------------------
# SUB SPACES MANAGEMENT TESTS
# ----------------------------------------------------


@pytest.fixture
def space_with_sub_spaces(space_before_setup):
    # Given
    sub_spaces = {}
    space = space_before_setup
    space.spaces = sub_spaces
    return space, sub_spaces


def test_add_space_creates_space(space_with_sub_spaces):
    # Given
    fake_space = Mock()
    fake_kind = Mock(return_value=fake_space)
    space, _ = space_with_sub_spaces

    # When
    space.add_space(fake_kind, "fake_space")

    # Then
    fake_kind.assert_called_with(space.model)
    assert fake_space.env is space


def test_add_space_creates_with_kwargs(space_with_sub_spaces):
    # Given
    fake_space = Mock()
    fake_kind = Mock(return_value=fake_space)
    space, _ = space_with_sub_spaces

    # When
    space.add_space(fake_kind, "fake_space", x=1, y=2)

    # Then
    fake_kind.assert_called_with(space.model, x=1, y=2)
    assert fake_space.env is space


def test_add_space_returns_new_space(space_with_sub_spaces):
    # Given
    fake_space = Mock()
    fake_kind = Mock(return_value=fake_space)
    space, _ = space_with_sub_spaces

    # When
    result = space.add_space(fake_kind, "fake_space")

    # Then
    assert result is fake_space


def test_add_space_registers_sub_space(space_with_sub_spaces):
    # Given
    fake_space = Mock()
    fake_kind = Mock(return_value=fake_space)
    space, sub_spaces = space_with_sub_spaces

    # When
    space.add_space(fake_kind, "fake_space")

    # Then
    assert sub_spaces["fake_space"] == fake_space


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
    space.spaces["fake_market"] = sub_space

    # When
    space.evolve()

    # Then
    space.update_state.assert_called_once()
    sub_space.update_state.assert_called_once()


def test_evolve_clear_all_defaults(space_before_evolution):
    # Given
    sub_space = Mock()
    space = space_before_evolution
    space.spaces["fake_market"] = sub_space

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
    assert role.env is space
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


# ---------------------------------------------------
# ACCOUNT MANAGEMENT
# ----------------------------------------------------

FakeAccount = Mock()


@pytest.fixture
def space_with_no_accounts(monkeypatch, space_before_setup):
    # Given
    monkeypatch.setattr("model.base.EcoAccount", FakeAccount)
    space = space_before_setup
    space.accounts = {}
    return space


def test_add_account_create_new_account(space_with_no_accounts):
    # Given
    agent = Mock(id=1)
    space = space_with_no_accounts

    # When
    account = space.add_account(agent)

    # Then
    FakeAccount.assert_called_with()
    assert account is FakeAccount.return_value


def test_add_account_registers_new_account(space_with_no_accounts):
    # Given
    agent = Mock(id=1)
    space = space_with_no_accounts

    # When
    account = space.add_account(agent)

    # Then
    assert account == space.accounts[agent.id]
    assert account is agent.account


def test_add_account_delegates_process_to_env(space_with_no_accounts):
    # Given
    env, agent = Mock(), Mock(id=1)
    space = space_with_no_accounts
    space.env = env

    # When
    account = space.add_account(agent)

    # Then
    env.add_account.assert_called_with(agent)
    assert env.add_account.return_value is account


def test_add_account_doesnt_register_env_account(space_with_no_accounts):
    # Given
    env, agent = Mock(), Mock(id=1)
    space = space_with_no_accounts
    space.env = env

    # When
    space.add_account(agent)

    # Then
    assert agent.id not in space.accounts



@pytest.fixture
def space_with_two_accounts(space_before_setup):
    # Given
    source, target = 1, 2
    space = space_before_setup
    space.accounts = {source:Mock(), target:Mock()}
    return space, source, target


def test_transfer_debit_source_account(space_with_two_accounts):
    # Given
    space, source, target = space_with_two_accounts
    source_account = space.accounts[source]

    # When
    space.transfer("x", source, target, 100)

    # Then
    source_account.debit.assert_called_with("x", 100)


def test_transfer_credit_target_account(space_with_two_accounts):
    # Given
    space, source, target = space_with_two_accounts
    target_account = space.accounts[target]

    # When
    space.transfer("x", source, target, 100)

    # Then
    target_account.credit.assert_called_with("x", 100)


def test_transfer_delegates_process_to_env(space_with_two_accounts):
    # Given
    env = Mock()
    space, source, target = space_with_two_accounts
    space.env = env

    # When
    space.transfer("x", source, target, 100)

    # Then
    env.transfer.assert_called_with("x", source, target, 100)


