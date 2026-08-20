import pytest
from unittest.mock import Mock
from mc_ab_sfc.spaces.bond_market import BondMarket

# ---------------------------------------------------
# ARCHITECTURE TESTS
# ----------------------------------------------------


def test_is_eco_space():
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
    monkeypatch.setattr("mc_ab_sfc.spaces.bond_market.BondIssuerRole", FakeRole)

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
    monkeypatch.setattr("mc_ab_sfc.spaces.bond_market.BondBuyerRole", FakeRole)

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
    monkeypatch.setattr("mc_ab_sfc.spaces.bond_market.BondIssuerRole", FakeRole)

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
    assert len(graph.edges) == 1
    assert graph.has_edge(issuer, buyer)
    assert graph[issuer][buyer]["amount"] == 500


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


class FakeBankAgent:
    pass


def test_buy_bonds_modifies_bank_stocks(market, monkeypatch):
    # Given
    issuer = Mock(bond_supply=1000)
    buyer = Mock(agent=FakeBankAgent())
    graph = market.graph
    graph.add_nodes_from([buyer, issuer])
    monkeypatch.setattr("mc_ab_sfc.spaces.bond_market.BankAgent", FakeBankAgent)

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


def test_pay_bond_debt_repays_principal(market):
    # Given
    issuer = Mock(bond_rate=0.05)
    buyer = Mock(agent=object())
    graph = market.graph
    graph.add_nodes_from([buyer, issuer])
    graph.add_edge(buyer, issuer, amount=100)

    # When
    market.pay_bond_debt(issuer)

    # Then
    assert not graph.has_edge(issuer, buyer)


def test_pay_bond_debt_modifies_government_stocks(market):
    # Given
    issuer = Mock(bond_rate=0.05)
    buyer = Mock(agent=object())
    graph = market.graph
    graph.add_nodes_from([buyer, issuer])
    graph.add_edge(buyer, issuer, amount=100)

    # When
    market.pay_bond_debt(issuer)

    # Then
    issuer.decrease_stock.assert_any_call("reserves", 105.0)
    issuer.decrease_stock.assert_any_call("bonds", 100)
    issuer.increase_flow.assert_any_call("bond_interest", 5.0)


def test_pay_bond_debt_modifies_bank_stocks(market, monkeypatch):
    # Given
    issuer = Mock(bond_rate=0.05)
    buyer = Mock(agent=FakeBankAgent())
    graph = market.graph
    graph.add_nodes_from([buyer, issuer])
    graph.add_edge(buyer, issuer, amount=100)
    monkeypatch.setattr("mc_ab_sfc.spaces.bond_market.BankAgent", FakeBankAgent)

    # When
    market.pay_bond_debt(issuer)

    # Then
    buyer.increase_stock.assert_any_call("reserves", 105.0)
    buyer.decrease_stock.assert_any_call("bonds", 100)
    buyer.increase_flow.assert_any_call("bond_interest", 5.0)


def test_pay_bond_debt_modifies_central_bank_stocks(market):
    # Given
    issuer = Mock(bond_rate=0.05)
    buyer = Mock(agent=object())
    graph = market.graph
    graph.add_nodes_from([buyer, issuer])
    graph.add_edge(buyer, issuer, amount=100)

    # When
    market.pay_bond_debt(issuer)

    # Then
    buyer.decrease_stock.assert_any_call("reserves", 105.0)
    buyer.decrease_stock.assert_any_call("bonds", 100)
    buyer.increase_flow.assert_any_call("bond_interest", 5.0)
