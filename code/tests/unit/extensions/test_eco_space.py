from unittest.mock import Mock
import pytest
from agentpy import AgentIter, AgentList
from model.extensions import EcoSpace

# ---------------------------------------------------
# ARCHITECTURE
# ----------------------------------------------------


def test_inherits_from_agentpy_network():
    # Given
    from agentpy import Network

    # When
    is_derived = issubclass(EcoSpace, Network)

    # Then
    assert is_derived


def test_initializes_env(fake_model):
    # Given
    model = fake_model

    # When
    space = EcoSpace(model)

    # Then
    assert space.env is None


def test_initializes_subspaces_dict(fake_model):
    # Given
    model = fake_model

    # When
    space = EcoSpace(model)

    # Then
    assert space.spaces == {}


def test_initializes_accounts_dict(fake_model):
    # Given
    model = fake_model

    # When
    space = EcoSpace(model)

    # Then
    assert space.accounts == {}


def test_initializes_roles_dict(fake_model):
    # Given
    model = fake_model

    # When
    space = EcoSpace(model)

    # Then
    assert space.roles == {}


# ---------------------------------------------------
# SUB SPACES MANAGEMENT TESTS
# ----------------------------------------------------


@pytest.fixture
def space(fake_model):
    # Given
    model = fake_model
    return EcoSpace(model)


@pytest.fixture
def space_without_subspaces(space):
    # Given
    subspaces = {}
    space.spaces = subspaces
    return space, subspaces


def test_add_space_creates_space(space_without_subspaces):
    # Given
    fake_space = Mock()
    fake_kind = Mock(return_value=fake_space)
    space, _ = space_without_subspaces

    # When
    space.add_space(fake_kind, "fake_space")

    # Then
    fake_kind.assert_called_with(space.model)
    assert fake_space.env is space


def test_add_space_creates_with_kwargs(space_without_subspaces):
    # Given
    fake_space = Mock()
    fake_kind = Mock(return_value=fake_space)
    space, _ = space_without_subspaces

    # When
    space.add_space(fake_kind, "fake_space", x=1, y=2)

    # Then
    fake_kind.assert_called_with(space.model, x=1, y=2)
    assert fake_space.env is space


def test_add_space_returns_new_space(space_without_subspaces):
    # Given
    fake_space = Mock()
    fake_kind = Mock(return_value=fake_space)
    space, _ = space_without_subspaces

    # When
    result = space.add_space(fake_kind, "fake_space")

    # Then
    assert result is fake_space


def test_add_space_registers_subspace(space_without_subspaces):
    # Given
    fake_space = Mock()
    fake_kind = Mock(return_value=fake_space)
    space, subspaces = space_without_subspaces

    # When
    space.add_space(fake_kind, "fake_space")

    # Then
    assert subspaces["fake_space"] == fake_space


# ---------------------------------------------------
# AGENT MANAGEMENT TESTS
# ----------------------------------------------------


class FakeAgent:
    pass


def test_add_agents_uses_appropriate_method(space):
    # Given
    agents = [FakeAgent() for _ in range(2)]
    space.add_fake_agent = Mock()

    # When
    space.add_agents(agents)

    # Then
    for agent in agents:
        space.add_fake_agent.assert_any_call(agent)


# ---------------------------------------------------
# ROLE MANAGEMENT TESTS
# ----------------------------------------------------


@pytest.fixture
def role_with_kind():
    # Given
    role = Mock()
    role.name = "fake_role"
    role_kind = Mock(return_value=role)
    return role, role_kind


@pytest.fixture
def space_and_agent(space):
    # Given
    space.roles = {}
    space.add_account = Mock()
    agent = Mock(roles={})
    return space, agent


def test_add_role_creates_role(space_and_agent, role_with_kind):
    # Given
    _, role_kind = role_with_kind
    space, agent = space_and_agent

    # When
    space.add_role(role_kind, agent)

    # Then
    role_kind.assert_called_with(agent, space)


def test_add_role_creates_role(space_and_agent, role_with_kind):
    # Given
    _, role_kind = role_with_kind
    space, agent = space_and_agent

    # When
    space.add_role(role_kind, agent)

    # Then
    role_kind.assert_called_with(agent, space)


def test_add_role_returns_role(space_and_agent, role_with_kind):
    # Given
    role, role_kind = role_with_kind
    space, agent = space_and_agent

    # When
    result = space.add_role(role_kind, agent)

    # Then
    assert result is role


def test_add_role_add_graph_node(space_and_agent, role_with_kind):
    # Given
    role, role_kind = role_with_kind
    space, agent = space_and_agent
    graph = space.graph

    # When
    space.add_role(role_kind, agent)

    # Then
    assert graph.has_node(role)
    assert space.positions[agent] is role



def test_add_role_registers_role(space_and_agent, role_with_kind):
    # Given
    role, role_kind = role_with_kind
    space, agent = space_and_agent

    # When
    space.add_role(role_kind, agent)

    # Then
    assert role is space.roles[agent.id]
    assert role is agent.roles["fake_role"]



def test_add_role_with_prefix(space_and_agent, role_with_kind):
    # Given
    role, role_kind = role_with_kind
    space, agent = space_and_agent

    # When
    space.add_role(role_kind, agent, prefix="any")

    # Then
    assert role.prefix == "any"
    assert role is agent.roles["any_fake_role"]


def test_add_role_creates_account_if_no_account(space_and_agent, role_with_kind):
    # Given
    _, role_kind = role_with_kind
    space, agent = space_and_agent
    agent.account = None

    # When
    space.add_role(role_kind, agent)

    # Then
    space.add_account.assert_called_with(agent)


def test_add_role_doesnt_create_account_if_account(space_and_agent, role_with_kind):
    # Given
    _, role_kind = role_with_kind
    space, agent = space_and_agent
    agent.account = Mock()

    # When
    space.add_role(role_kind, agent)

    # Then
    space.add_account.assert_not_called()


@pytest.fixture
def space_with_role(space_and_agent):
    # Given
    space, agent = space_and_agent
    role = Mock()
    role.agent = agent
    role.name = "fake_role"
    agent.roles["fake_role"] = role
    space.roles = {agent.id: role}
    space.graph.add_node(role)
    return space, role


def test_remove_role_removes_graph_node(space_with_role):
    # Given
    space, role = space_with_role
    graph = space.graph

    # When
    space.remove_role(role)

    # Then
    assert not graph.has_node(role)


def test_remove_role_unregisters_role(space_with_role):
    # Given
    space, role = space_with_role
    agent = role.agent

    # When
    space.remove_role(role)

    # Then
    assert len(agent.roles) == 0
    assert len(space.roles) == 0


@pytest.fixture
def space_with_roles(space):
    # Given
    roles = [Mock(id=i) for i in range(2)]
    space.roles = {role.id: role for role in roles}
    return space, roles


def test_find_all_roles_filter_by_pattern(space_with_roles):
    # Given
    space, roles = space_with_roles
    roles[0].name = "other_role"
    roles[1].name = "fake_role"

    # When
    result = space.find_all_roles("fake")

    # Then
    assert list(result) == [roles[1]]


def test_find_all_roles_returns_agent_list(space_with_roles):
    # Given
    space, roles = space_with_roles
    roles[0].name = "other_role"
    roles[1].name = "fake_role"

    # When
    result = space.find_all_roles("fake_role")

    # Then
    assert isinstance(result, AgentList)


def test_find_random_roles_filter_by_pattern(space_with_roles):
    # Given
    space, roles = space_with_roles
    roles[0].name = "other_role"
    roles[1].name = "fake_role"

    # When
    result = space.find_random_roles("fake", 2)

    # Then
    assert list(result) == [roles[1]]


@pytest.mark.parametrize("size, expected", [(1, 1), (2, 2), (3, 2)])
def test_find_random_roles_with_various_size(space_with_roles, size, expected):
    # Given
    space, roles = space_with_roles
    roles[0].name = "fake_role"
    roles[1].name = "fake_role"

    # When
    result = space.find_random_roles("fake_role", size)

    # Then
    assert len(result) == expected


def test_find_random_roles_returns_agent_list(space_with_roles):
    # Given
    space, roles = space_with_roles
    roles[0].name = "fake_role"
    roles[1].name = "fake_role"

    # When
    result = space.find_random_roles("fake_role", 2)

    # Then
    assert isinstance(result, AgentList)


# ---------------------------------------------------
# LINKS/NEIGHBORS MANAGEMENT
# ----------------------------------------------------


@pytest.fixture
def space_with_edges(space):
    # Given
    roles = [Mock() for _ in range(3)]
    graph = space.graph
    graph.add_edge(roles[0], roles[1], variable=10)
    graph.add_edge(roles[0], roles[2], variable=20)
    return space, roles


def test_neighbors_returns_role_agent_iter(space_with_edges):
    # Given
    space, roles = space_with_edges

    # When
    result = space.neighbors(roles[1])

    # Then
    assert isinstance(result, AgentIter)
    assert list(result) == [roles[0]]


def test_links_returns_edge_list(space_with_edges):
    # Given
    space, roles = space_with_edges

    # When
    result = space.links(roles[1], "supplier")

    # Then
    assert result == [{"supplier": roles[0], "variable": 10}]


# ---------------------------------------------------
# ACCOUNT MANAGEMENT
# ----------------------------------------------------

FakeAccount = Mock()


@pytest.fixture
def space_without_accounts(monkeypatch, space):
    # Given
    monkeypatch.setattr("model.extensions.EcoAccount", FakeAccount)
    space.accounts = {}
    return space


def test_add_account_create_new_account(space_without_accounts):
    # Given
    space = space_without_accounts
    agent = Mock(id=1)

    # When
    account = space.add_account(agent)

    # Then
    FakeAccount.assert_called_with()
    assert account is FakeAccount.return_value


def test_add_account_registers_new_account(space_without_accounts):
    # Given
    agent = Mock(id=1)
    space = space_without_accounts

    # When
    account = space.add_account(agent)

    # Then
    assert account == space.accounts[agent.id]
    assert account is agent.account


def test_add_account_delegates_process_to_env(space_without_accounts):
    # Given
    env, agent = Mock(), Mock(id=1)
    space = space_without_accounts
    space.env = env

    # When
    account = space.add_account(agent)

    # Then
    env.add_account.assert_called_with(agent)
    assert env.add_account.return_value is account


def test_add_account_doesnt_register_env_account(space_without_accounts):
    # Given
    env, agent = Mock(), Mock(id=1)
    space = space_without_accounts
    space.env = env

    # When
    space.add_account(agent)

    # Then
    assert agent.id not in space.accounts


@pytest.fixture
def space_with_accounts(space):
    # Given
    accounts = {}
    for i in range(2):
        account = dict(x=0)
        accounts[i] = account
    space.accounts = accounts
    return space, accounts


def test_transfer_stock_decr_source_account_stock(space_with_accounts):
    # Given
    source, target = 0, 1
    space, accounts = space_with_accounts

    # When
    space.transfer_stock("x", source, target, 100)

    # Then
    assert accounts[source]["x"] == -100


def test_transfer_stock_incr_target_account_stock(space_with_accounts):
    # Given
    source, target = 0, 1
    space, accounts = space_with_accounts

    # When
    space.transfer_stock("x", source, target, 100)

    # Then
    assert accounts[target]["x"] == 100


def test_transfer_stock_uses_env_method(space_with_accounts):
    # Given
    env = Mock()
    space, _ = space_with_accounts
    space.env = env

    # When
    space.transfer_stock("x", 1, 2, 100)

    # Then
    env.transfer_stock.assert_called_with("x", 1, 2, 100)


def test_get_stock_returns_identified_account_stock(space_with_accounts):
    # Given
    account_id = 1
    space, accounts = space_with_accounts
    accounts[account_id]["x"] = 100

    # When
    value = space.get_stock("x", account_id)

    # Then
    assert value == 100


def test_get_stock_uses_env_method(space_with_accounts):
    # Given
    env = Mock()
    space, _ = space_with_accounts
    space.env = env
    account_id = 1

    # When
    value = space.get_stock("x", account_id)

    # Then
    env.get_stock.assert_called_with("x", account_id)
    assert value == env.get_stock.return_value


def test_make_transaction_decr_source_account_flow(space_with_accounts):
    # Given
    source, target = 0, 1
    space, accounts = space_with_accounts

    # When
    space.make_transaction("x", source, target, 100)

    # Then
    assert accounts[source]["x"] == -100


def test_make_transaction_incr_target_account_flow(space_with_accounts):
    # Given
    source, target = 0, 1
    space, accounts = space_with_accounts

    # When
    space.make_transaction("x", source, target, 100)

    # Then
    assert accounts[target]["x"] == 100


def test_make_transaction_uses_available_env_method(space_with_accounts):
    # Given
    env = Mock()
    source, target = 0, 1
    space, _ = space_with_accounts
    space.env = env

    # When
    space.make_transaction("x", source, target, 100)

    # Then
    env.make_transaction.assert_called_with("x", source, target, 100)


# ---------------------------------------------------
# EVOLUTION TESTS
# ----------------------------------------------------


@pytest.fixture
def space_before_evolution(space_without_subspaces):
    # Given
    space, _ = space_without_subspaces
    space.update_state = Mock()
    space.clear_defaults = Mock()
    return space


def test_evolve_update_all_state(space_before_evolution):
    # Given
    subspace = Mock()
    space = space_before_evolution
    space.spaces["fake_market"] = subspace

    # When
    space.evolve()

    # Then
    space.update_state.assert_called_once()
    subspace.update_state.assert_called_once()


def test_evolve_clear_all_defaults(space_before_evolution):
    # Given
    subspace = Mock()
    space = space_before_evolution
    space.spaces["fake_market"] = subspace

    # When
    space.evolve()

    # Then
    space.clear_defaults.assert_called_once()
    subspace.clear_defaults.assert_called_once()


def test_update_state_is_not_implemented(fake_model):
    # Given
    model = fake_model

    # When
    space = EcoSpace(model)

    # Then
    with pytest.raises(NotImplementedError):
        space.update_state()


def test_clear_defaults_is_not_implemented(fake_model):
    # Given
    model = fake_model

    # When
    space = EcoSpace(model)

    # Then
    with pytest.raises(NotImplementedError):
        space.clear_defaults()
