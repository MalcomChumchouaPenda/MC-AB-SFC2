import pytest
from unittest.mock import Mock, call
from agentpy import AgentDList
from model.base import EcoSpace
from model.spaces.bond_market import BondMarket

# ---------------------------------------------------
# ARCHITECTURE TESTS
# ----------------------------------------------------


def test_inherits_from_agentpy_object():
    # Assert
    assert issubclass(BondMarket, EcoSpace)


@pytest.fixture
def market():
    # Given
    model = Mock()
    market = BondMarket(model)
    return market


# ---------------------------------------------------
# ROLES MANAGEMENT
# ----------------------------------------------------


FakeBuyer = Mock()
FakeIssuer = Mock()


@pytest.fixture
def market_without_roles(monkeypatch, market):
    # Given
    monkeypatch.setattr("model.spaces.bond_market.BondBuyer", FakeBuyer)
    monkeypatch.setattr("model.spaces.bond_market.BondIssuer", FakeIssuer)
    market.add_role = Mock()
    return market


def test_add_buyer_add_appropriate_role(market_without_roles):
    # Given
    agent = Mock()
    market = market_without_roles

    # When
    role = market.add_buyer(agent)

    # Then
    market.add_role.assert_called_with(FakeBuyer, agent, "bond_buyer")
    assert role == market.add_role.return_value


def test_add_issuer_add_appropriate_role(market_without_roles):
    # Given
    agent = Mock()
    market = market_without_roles

    # When
    role = market.add_issuer(agent)

    # Then
    market.add_role.assert_called_with(FakeIssuer, agent, "bond_issuer")
    assert role == market.add_role.return_value


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
