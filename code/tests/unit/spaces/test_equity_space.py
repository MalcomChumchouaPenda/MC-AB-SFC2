import pytest
from unittest.mock import Mock
from mc_ab_sfc.spaces import EquitySpace

# ---------------------------------------------------
# ARCHITECTURE TESTS
# ----------------------------------------------------


def test_is_eco_space():
    # Given
    from mc_ab_sfc.base import EcoSpace

    # Assert
    assert issubclass(EquitySpace, EcoSpace)


# ---------------------------------------------------
# BEHAVIORAL TESTS
# ----------------------------------------------------


class FakeRole:
    pass


@pytest.fixture
def space():
    # Given
    model = Mock()
    space = EquitySpace(model)
    return space


def test_add_equity_holder_creates_appropriate_role(space, monkeypatch):
    # Given
    household = Mock()
    space.add_role = Mock()
    monkeypatch.setattr("mc_ab_sfc.spaces.EquityHolderRole", FakeRole)

    # When
    equity_holder = space.add_equity_holder(household)

    # Then
    space.add_role.assert_called_with(FakeRole, household, "equity_holder")
    assert equity_holder is space.add_role.return_value


def test_add_equity_issuer_creates_appropriate_role(space, monkeypatch):
    # Given
    agent = Mock()
    space.add_role = Mock()
    monkeypatch.setattr("mc_ab_sfc.spaces.EquityIssuerRole", FakeRole)

    # When
    equity_issuer = space.add_equity_issuer(agent)

    # Then
    space.add_role.assert_called_with(FakeRole, agent, "equity_issuer")
    assert equity_issuer is space.add_role.return_value


def test_assign_equity_holder_add_edge(space):
    # Given
    issuer = Mock()
    holder = Mock()
    graph = space.graph
    graph.add_nodes_from([issuer, holder])

    # When
    space.assign_equity_holder(issuer, holder, 0.5)

    # Then
    assert len(graph.edges) == 1
    assert graph.has_edge(holder, issuer)
    assert graph[holder][issuer]["share"] == 0.5


@pytest.fixture
def issuer(space):
    # Given
    issuer = Mock()
    space.graph.add_node(issuer)
    return issuer


@pytest.fixture
def holders(space):
    # Given
    holders = [Mock() for _ in range(3)]
    space.graph.add_nodes_from(holders)
    return holders


class FakeAgent:
    pass


def test_distributes_dividends_with_reserves(space, issuer, holders, monkeypatch):
    # Given
    issuer.agent = FakeAgent()
    graph = space.graph
    graph.add_edge(issuer, holders[0], share=0.6)
    graph.add_edge(issuer, holders[1], share=0.4)
    monkeypatch.setattr("mc_ab_sfc.spaces.BankAgent", FakeAgent)

    # When
    space.distribute_dividends(issuer, 200)

    # Then
    issuer.increase_flow.assert_called_with("dividends", 200)
    issuer.decrease_stock.assert_called_with("reserves", 200)
    holders[0].increase_flow.assert_called_with("dividends", 120)
    holders[0].increase_stock.assert_called_with("cash", 120)
    holders[1].increase_flow.assert_called_with("dividends", 80)
    holders[1].increase_stock.assert_called_with("cash", 80)


def test_distributes_dividends_with_cash(space, issuer, holders):
    # Given
    graph = space.graph
    graph.add_edge(issuer, holders[0], share=0.6)
    graph.add_edge(issuer, holders[1], share=0.4)

    # When
    space.distribute_dividends(issuer, 200)

    # Then
    issuer.increase_flow.assert_called_with("dividends", 200)
    issuer.decrease_stock.assert_called_with("cash", 200)
    holders[0].increase_flow.assert_called_with("dividends", 120)
    holders[0].increase_stock.assert_called_with("cash", 120)
    holders[1].increase_flow.assert_called_with("dividends", 80)
    holders[1].increase_stock.assert_called_with("cash", 80)


def test_update_equity_holdings(space, issuer, holders):
    # Given
    graph = space.graph
    graph.add_edge(issuer, holders[0], share=0.6)
    graph.add_edge(issuer, holders[1], share=0.4)
    issuer.net_worth = 1200

    # When
    space.update_equity_holdings(issuer)

    # Then
    issuer.clear_stock.assert_called_once_with("equity")
    issuer.increase_stock.assert_called_once_with("equity", 1200)
    holders[0].clear_stock.assert_called_once_with("equity")
    holders[0].increase_stock.assert_called_once_with("equity", 720)
    holders[1].clear_stock.assert_called_once_with("equity")
    holders[1].increase_stock.assert_called_once_with("equity", 480)
