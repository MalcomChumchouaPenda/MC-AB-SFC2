import pytest
from unittest.mock import Mock
from mc_ab_sfc.spaces import BondMarket

# ---------------------------------------------------
# ARCHITECTURAL TESTS
# ----------------------------------------------------


def test_is_ecospace():
    # Given
    from mc_ab_sfc.base import EcoSpace

    # Assert
    assert issubclass(BondMarket, EcoSpace)


# ---------------------------------------------------
# BEHAVIORAL TESTS
# ----------------------------------------------------


class FakeRole:
    pass


@pytest.fixture
def market():
    # Given
    model = Mock()
    market = BondMarket(model)
    return market


def test_add_bond_issuer_creates_issuer_role(market, monkeypatch):
    # Given
    household = Mock()
    market.add_role = Mock()
    monkeypatch.setattr("mc_ab_sfc.spaces.BondIssuerRole", FakeRole)

    # When
    issuer = market.add_bond_issuer(household)

    # Then
    action = market.add_role
    action.assert_called_with(FakeRole, household, "bond_issuer")
    assert issuer is action.return_value


def test_add_bond_buyer_creates_buyer(market, monkeypatch):
    # Given
    bank = Mock()
    market.add_role = Mock()
    monkeypatch.setattr("mc_ab_sfc.spaces.BondBuyerRole", FakeRole)

    # When
    buyer = market.add_bond_buyer(bank)

    # Then
    action = market.add_role
    action.assert_called_with(FakeRole, bank, "bond_buyer")
    assert buyer is action.return_value


def test_get_bond_issuers_returns_all_buyers(market, monkeypatch):
    # Given
    others = [Mock() for _ in range(5)]
    buyers = [FakeRole() for _ in range(5)]
    market.graph.add_nodes_from(others + buyers)
    monkeypatch.setattr("mc_ab_sfc.spaces.BondIssuerRole", FakeRole)

    # When
    result = market.get_bond_issuers()

    # Then
    random = market.model.random
    assert not random.sample.called
    assert result == buyers


def test_buy_bonds_creates_edge(market):
    # Given
    issuer = Mock(bond_supply=1000)
    buyer = Mock(agent=object())
    graph = market.graph
    graph.add_nodes_from([buyer, issuer])

    # When
    market.buy_bonds(buyer, issuer, 500)

    # Then
    edges = list(graph.edges(data=True))
    source, target, data = edges[0]
    assert len(edges) == 1
    assert source is issuer
    assert target is buyer
    assert data["amount"] == 500


def test_buy_bonds_reduces_bond_supply(market):
    # Given
    issuer = Mock(bond_supply=1000)
    buyer = Mock(agent=object())
    graph = market.graph
    graph.add_nodes_from([buyer, issuer])

    # When
    market.buy_bonds(buyer, issuer, 500)

    # Then
    assert issuer.bond_supply == 500


def test_buy_bonds_modifies_government_stocks(market):
    # Given
    issuer = Mock(bond_supply=1000)
    buyer = Mock(agent=object())
    graph = market.graph
    graph.add_nodes_from([buyer, issuer])

    # When
    market.buy_bonds(buyer, issuer, 500)

    # Then
    issuer.increase_stock.assert_any_call("reserves", 500)
    issuer.increase_stock.assert_any_call("bonds", 500)


class FakeAgent:
    pass


def test_buy_bonds_modifies_bank_stocks(market, monkeypatch):
    # Given
    issuer = Mock(bond_supply=1000)
    buyer = Mock(agent=FakeAgent())
    graph = market.graph
    graph.add_nodes_from([buyer, issuer])
    monkeypatch.setattr("mc_ab_sfc.spaces.BankAgent", FakeAgent)

    # When
    market.buy_bonds(buyer, issuer, 500)

    # Then
    buyer.decrease_stock.assert_any_call("reserves", 500)
    buyer.increase_stock.assert_any_call("bonds", 500)


def test_buy_bonds_modifies_central_bank_stocks(market):
    # Given
    issuer = Mock(bond_supply=1000)
    buyer = Mock(agent=object())
    graph = market.graph
    graph.add_nodes_from([buyer, issuer])

    # When
    market.buy_bonds(buyer, issuer, 500)

    # Then
    buyer.increase_stock.assert_any_call("reserves", 500)
    buyer.increase_stock.assert_any_call("bonds", 500)
