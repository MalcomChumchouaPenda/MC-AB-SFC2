import pytest
from unittest.mock import Mock
from agentpy import AgentDList
from model.spaces.bond_market import BondMarket

# ---------------------------------------------------
# ARCHITECTURE TESTS
# ----------------------------------------------------


def test_is_agentpy_object():
    # Given
    from model.base import EcoSpace

    # Assert
    assert issubclass(BondMarket, EcoSpace)


@pytest.fixture
def market_before_setup():
    # Given
    model = Mock()
    market = BondMarket(model)
    return market


# ---------------------------------------------------
# ROLES
# ----------------------------------------------------


def test_has_buyers_list(market_before_setup):
    # Given
    market = market_before_setup

    # When
    market.setup()

    # Then
    assert isinstance(market.buyers, AgentDList)


def test_has_issuers_list(market_before_setup):
    # Given
    market = market_before_setup

    # When
    market.setup()

    # Then
    assert isinstance(market.issuers, AgentDList)


class FakeBuyer(Mock):
    pass


@pytest.fixture
def market_without_buyers(monkeypatch, market_before_setup):
    # Given
    monkeypatch.setattr("model.spaces.bond_market.BondBuyer", FakeBuyer)
    market = market_before_setup
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
    market.add_role.assert_called_with(FakeBuyer, agent,"bond_buyer")
    assert role == market.add_role.return_value


def test_add_buyer_registers_buyer(market_without_buyers):
    # Given
    agent = Mock()
    market = market_without_buyers

    # When
    role = market.add_buyer(agent)

    # Then
    assert market.buyers == [role]


class FakeIssuer(Mock):
    pass


@pytest.fixture
def market_without_issuers(monkeypatch, market_before_setup):
    # Given
    monkeypatch.setattr("model.spaces.bond_market.BondIssuer", FakeIssuer)
    market = market_before_setup
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
def market_with_issuers(market_before_setup, make_dlist):
    # Given
    issuers = make_dlist()
    market = market_before_setup
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


def test_find_bonds_returns_bonds_edge(market_before_setup):
    # Given
    issuer, buyer, other = Mock(), Mock(), Mock()
    market = market_before_setup
    graph = market.graph
    graph.add_edge(issuer, buyer, amount=100)
    graph.add_edge(other, buyer, amount=200)

    # When
    result = market.find_bonds(issuer)

    # Then
    assert result == [{"buyer":buyer, "amount":100}]



# ---------------------------------------------------
# BONDS TRANSACTION
# ----------------------------------------------------

@pytest.fixture
def market_with_participants(market_before_setup):
    # Given
    buyer = Mock()
    issuer = Mock(debt_ratio=0, bond_value=100, bond_number=1)
    market = market_before_setup
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
    issuer.bond_value = 100

    # When
    market.buy_bonds(buyer, issuer, 2)

    # Then
    issuer.debit_stock.assert_called_with("bonds", 200)
    issuer.credit_stock.assert_called_with("cash", 200)
    buyer.credit_stock.assert_called_with("bonds", 200)
    buyer.debit_stock.assert_called_with("cash", 200)


def test_buy_bonds_reduces_bond_supply(market_with_participants):
    # Given
    market, issuer, buyer = market_with_participants
    issuer.bond_number = 2

    # When
    market.buy_bonds(buyer, issuer, 2)

    # Then
    assert issuer.bond_number == 0


@pytest.fixture
def market_with_purchase(market_before_setup):
    # Given
    buyer = Mock()
    issuer = Mock()
    market = market_before_setup
    market.graph.add_edge(buyer, issuer, amount=0)
    return market, issuer, buyer


def test_repay_bonds_creates_graph_edge(market_with_purchase):
    # Given
    market, issuer, buyer = market_with_purchase
    graph = market.graph

    # When
    market.repay_bonds(buyer, issuer, 100, 10)

    # Then
    assert graph.has_edge(buyer, issuer)
    assert graph[buyer][issuer]["amount"] == -100


def test_repay_bonds_updates_accounts(market_with_purchase):
    # Given
    market, issuer, buyer = market_with_purchase

    # When
    market.repay_bonds(buyer, issuer, 100, 10)

    # Then
    issuer.debit_flow.assert_called_with("bond_interests", 10)
    issuer.credit_stock.assert_called_with("bonds", 100)
    issuer.debit_stock.assert_called_with("cash", 110)
    buyer.credit_flow.assert_called_with("bond_interests", 10)
    buyer.debit_stock.assert_called_with("bonds", 100)
    buyer.credit_stock.assert_called_with("cash", 110)

