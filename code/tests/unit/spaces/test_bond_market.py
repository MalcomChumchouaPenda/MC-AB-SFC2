import pytest
from unittest.mock import Mock, call
from agentpy import AgentDList
from model.base import EcoSpace
from model.spaces.bond_market import BondMarket

# ---------------------------------------------------
# ARCHITECTURE TESTS
# ----------------------------------------------------


def test_is_agentpy_object():
    # Assert
    assert issubclass(BondMarket, EcoSpace)


@pytest.fixture
def market():
    # Given
    model = Mock()
    market = BondMarket(model)
    return market


def test_has_buyers_list(market):
    # Assert
    assert isinstance(market.buyers, AgentDList)


def test_has_issuers_list(market):
    # Assert
    assert isinstance(market.issuers, AgentDList)


# ---------------------------------------------------
# ROLES MANAGEMENT
# ----------------------------------------------------


FakeBuyer = Mock()
FakeIssuer = Mock()


@pytest.fixture
def market_without_buyers(monkeypatch, market):
    # Given
    monkeypatch.setattr("model.spaces.bond_market.BondBuyer", FakeBuyer)
    market.add_role = Mock()
    market.buyers = []
    return market


def test_add_buyer_add_appropriate_role(market_without_buyers):
    # Given
    agent = Mock()
    market = market_without_buyers

    # When
    role = market.add_buyer(agent)

    # Then
    market.add_role.assert_called_with(FakeBuyer, agent, "bond_buyer")
    assert role == market.add_role.return_value


def test_add_buyer_registers_buyer(market_without_buyers):
    # Given
    agent = Mock()
    market = market_without_buyers

    # When
    role = market.add_buyer(agent)

    # Then
    assert market.buyers == [role]


@pytest.fixture
def market_without_issuers(monkeypatch, market):
    # Given
    monkeypatch.setattr("model.spaces.bond_market.BondIssuer", FakeIssuer)
    market.add_role = Mock()
    market.issuers = []
    return market


def test_add_issuer_add_appropriate_role(market_without_issuers):
    # Given
    agent = Mock()
    market = market_without_issuers

    # When
    role = market.add_issuer(agent)

    # Then
    market.add_role.assert_called_with(FakeIssuer, agent, "bond_issuer")
    assert role == market.add_role.return_value


def test_add_issuer_registers_issuer(market_without_issuers):
    # Given
    agent = Mock()
    market = market_without_issuers

    # When
    role = market.add_issuer(agent)

    # Then
    assert market.issuers == [role]


# ---------------------------------------------------
# BONDS MATCHING
# ----------------------------------------------------


@pytest.fixture
def market_with_issuers(market, make_dlist):
    # Given
    issuers = make_dlist()
    market.issuers = issuers
    return market, issuers


def test_find_issuers_return_issuer_with_bonds(market_with_issuers):
    # Given
    eligible = Mock(bond_number=1)
    ineligible = Mock(bond_number=0)
    market, issuers = market_with_issuers
    issuers.extend([eligible, ineligible])

    # When
    found = market.find_issuers()

    # Then
    assert found == [eligible]


def test_find_bonds_returns_bonds_edge(market):
    # Given
    issuer, buyer, other = Mock(), Mock(), Mock()
    graph = market.graph
    graph.add_edge(issuer, buyer, amount=100)
    graph.add_edge(other, buyer, amount=200)

    # When
    result = market.find_bonds(issuer)

    # Then
    assert result == [{"buyer": buyer, "amount": 100}]


# ---------------------------------------------------
# BONDS TRANSACTION
# ----------------------------------------------------


@pytest.fixture
def market_with_participants(market):
    # Given
    buyer = Mock()
    issuer = Mock(debt_ratio=0, bond_value=100, bond_number=1)
    market.transfer_stock = Mock()
    market.record_flow = Mock()
    return market, issuer, buyer


def test_buy_bonds_creates_graph_edge(market_with_participants):
    # Given
    market, issuer, buyer = market_with_participants
    issuer.bond_value = 100
    graph = market.graph

    # When
    market.buy_bonds(buyer, issuer, 2)

    # Then
    assert graph.has_edge(buyer, issuer)
    assert graph[buyer][issuer]["amount"] == 200


def test_buy_bonds_updates_accounts(market_with_participants):
    # Given
    market, issuer, buyer = market_with_participants
    transfer_stock = market.transfer_stock
    issuer.bond_value = 100

    # When
    market.buy_bonds(buyer, issuer, 2)

    # Then
    transfer_stock.assert_any_call("bonds", issuer.id, buyer.id, 200)
    transfer_stock.assert_any_call("cash", buyer.id, issuer.id, 200)


def test_buy_bonds_reduces_bond_supply(market_with_participants):
    # Given
    market, issuer, buyer = market_with_participants
    issuer.bond_number = 2

    # When
    market.buy_bonds(buyer, issuer, 2)

    # Then
    assert issuer.bond_number == 0


@pytest.fixture
def market_with_purchase(market):
    # Given
    buyer = Mock()
    issuer = Mock()
    market.graph.add_edge(buyer, issuer, amount=0)
    market.transfer_stock = Mock()
    market.record_flow = Mock()
    return market, issuer, buyer


def test_repay_bond_creates_graph_edge(market_with_purchase):
    # Given
    market, issuer, buyer = market_with_purchase
    graph = market.graph

    # When
    market.repay_bonds(buyer, issuer, 100, 10)

    # Then
    assert graph.has_edge(buyer, issuer)
    assert graph[buyer][issuer]["amount"] == -100


def test_repay_bond_updates_accounts(market_with_purchase):
    # Given
    market, issuer, buyer = market_with_purchase
    transfer_stock = market.transfer_stock
    record_flow = market.record_flow

    # When
    market.repay_bonds(buyer, issuer, 100, 10)

    # Then
    transfer_stock.assert_any_call("bonds", buyer.id, issuer.id, 100)
    transfer_stock.assert_any_call("cash", issuer.id, buyer.id, 110)
    record_flow.assert_any_call("bond_interests", issuer.id, buyer.id, 10)
