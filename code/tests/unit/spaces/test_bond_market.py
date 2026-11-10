import pytest
from unittest.mock import Mock, call
from model.spaces.bond_market import BondMarket

# ---------------------------------------------------
# ARCHITECTURE
# ----------------------------------------------------


def test_inherits_from_eco_space():
    # Given
    from model.extensions import EcoSpace

    # When
    is_derived = issubclass(BondMarket, EcoSpace)

    # Then
    assert is_derived


# ---------------------------------------------------
# ROLES MANAGEMENT
# ----------------------------------------------------


@pytest.fixture
def market(fake_model):
    # Given
    return BondMarket(fake_model)


@pytest.fixture
def market_without_roles(market):
    # Given
    market.add_role = Mock()
    return market


def test_add_bank_add_buyer_role(market_without_roles, monkeypatch):
    # Given
    bank = Mock()
    role_cls = Mock(name="BondBuyer")
    monkeypatch.setattr("model.spaces.bond_market.BondBuyer", role_cls)
    market = market_without_roles

    # When
    market.add_bank(bank)

    # Then
    market.add_role.assert_called_with(role_cls, bank)


def test_add_central_bank_add_buyer_role(market_without_roles, monkeypatch):
    # Given
    cb = Mock()
    role_cls = Mock(name="BondBuyer")
    monkeypatch.setattr("model.spaces.bond_market.BondBuyer", role_cls)
    market = market_without_roles

    # When
    market.add_central_bank(cb)

    # Then
    market.add_role.assert_called_with(role_cls, cb)


def test_add_government_add_issuer_role(market_without_roles, monkeypatch):
    # Given
    govt = Mock()
    role_cls = Mock(name="BondIssuer")
    monkeypatch.setattr("model.spaces.bond_market.BondIssuer", role_cls)
    market = market_without_roles

    # When
    market.add_government(govt)

    # Then
    market.add_role.assert_called_with(role_cls, govt)


# ---------------------------------------------------
# BONDS TRANSACTION
# ----------------------------------------------------


@pytest.fixture
def buyer():
    # Given
    return Mock()


@pytest.fixture
def issuer():
    # Given
    return Mock(bond_value=100, bond_number=1, debt_ratio=0)


@pytest.fixture
def market_without_purchase(market):
    # Given
    market.transfer_stock = Mock()
    market.make_transaction = Mock()
    return market


def test_buy_bonds_creates_graph_edge(market_without_purchase, buyer, issuer):
    # Given
    market = market_without_purchase
    graph = market.graph

    # When
    market.buy_bonds(buyer, issuer, 2)

    # Then
    assert graph.has_edge(buyer, issuer)
    assert graph[buyer][issuer]["amount"] == 200


def test_buy_bonds_transfers_cash(market_without_purchase, buyer, issuer):
    # Given
    market = market_without_purchase

    # When
    market.buy_bonds(buyer, issuer, 2)

    # Then
    market.transfer_stock.assert_any_call("cash", buyer.id, issuer.id, 200)


def test_buy_bonds_updates_accounts(market_without_purchase, buyer, issuer):
    # Given
    market = market_without_purchase

    # When
    market.buy_bonds(buyer, issuer, 2)

    # Then
    market.transfer_stock.assert_any_call("bonds", issuer.id, buyer.id, 200)


def test_buy_bonds_reduces_bond_supply(market_without_purchase, buyer, issuer):
    # Given
    issuer.bond_number = 2
    market = market_without_purchase

    # When
    market.buy_bonds(buyer, issuer, 2)

    # Then
    assert issuer.bond_number == 0


@pytest.fixture
def market_with_purchase(market_without_purchase, buyer, issuer):
    # Given
    market = market_without_purchase
    market.graph.add_edge(buyer, issuer, amount=0)
    return market


def test_repay_bond_creates_graph_edge(market_with_purchase, buyer, issuer):
    # Given
    market = market_with_purchase
    graph = market.graph

    # When
    market.repay_bonds(buyer, issuer, 100, 10)

    # Then
    assert graph.has_edge(buyer, issuer)
    assert graph[buyer][issuer]["amount"] == -100


def test_repay_bond_transfers_cash(market_with_purchase, buyer, issuer):
    # Given
    market = market_with_purchase

    # When
    market.repay_bonds(buyer, issuer, 100, 10)

    # Then
    market.transfer_stock.assert_any_call("cash", issuer.id, buyer.id, 110)


def test_repay_bond_updates_accounts(market_with_purchase, buyer, issuer):
    # Given
    market = market_with_purchase

    # When
    market.repay_bonds(buyer, issuer, 100, 10)

    # Then
    market.transfer_stock.assert_any_call("bonds", buyer.id, issuer.id, 100)
    market.make_transaction.assert_any_call("bond_interests", issuer.id, buyer.id, 10)


# ---------------------------------------------------
# EVOLUTION
# ----------------------------------------------------


@pytest.fixture
def buyers():
    # Given
    buyers = []
    for defaulted in (True, False):
        role = Mock(defaulted=defaulted)
        role.name = "bond_buyer"
        buyers.append(role)
    return buyers


@pytest.fixture
def market_with_defaults(market, buyers):
    # Given
    for role in buyers:
        market.roles[role.agent.id] = role
    market.remove_role = Mock()
    return market


def test_clear_defaults_removes_defaulted_buyers(market_with_defaults, buyers):
    # Given
    market = market_with_defaults

    # When
    market.clear_defaults()

    # Then
    assert call(buyers[0]) in market.remove_role.call_args_list
    assert call(buyers[1]) not in market.remove_role.call_args_list
    assert market.remove_role.call_count == 1
