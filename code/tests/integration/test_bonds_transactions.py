import pytest
from unittest.mock import Mock, PropertyMock
from mc_ab_sfc.agents import Bank, CentralBank, Government
from mc_ab_sfc.spaces import BondMarket


@pytest.fixture
def model():
    # Given
    model = Mock()
    model.p.mu2 = 0.1
    model.p.iota_b = 0
    model.p.chi = 0.02
    return model


@pytest.fixture
def govt(model):
    # Given
    govt = Government(model)
    govt.gdp = 1000
    govt.budget_deficit = 200
    govt.prev_budget_surplus = 50
    return govt


@pytest.fixture
def bank(model, monkeypatch):
    # Given
    deposits = PropertyMock(return_value=1000)
    monkeypatch.setattr(Bank, "deposits", deposits)
    bank = Bank(model)
    bank.reserves = 300
    return bank


@pytest.fixture
def cb(model):
    # Given
    cb = CentralBank(model)
    cb.reserves = 1000
    cb.discount_rate = 0.04
    return cb


@pytest.fixture
def bond_market_with_participants(model, govt, cb, bank):
    # Given
    cb.government = govt
    govt.central_bank = cb
    bond_market = BondMarket(model)
    bond_market.setup()
    bond_market.add_issuer(govt)
    bond_market.add_buyer(bank)
    bond_market.add_buyer(cb)
    model.bond_market = bond_market
    return bond_market, govt, cb, bank


def test_government_issues_bonds(bond_market_with_participants):
    # Given
    _, govt, *_ = bond_market_with_participants

    # When
    govt.issue_bonds()

    # Then
    assert govt.bond_supply == 150


def test_government_repay_bonds_to_bank(bond_market_with_participants):
    # Given
    bond_market, govt, _, bank = bond_market_with_participants
    bond_market.bonds.add_edge(govt, bank, principal=100)

    # When
    govt.repay_bonds()

    # Then
    assert govt.bonds == 0
    assert govt.reserves == -104.2
    assert govt.bond_interests == 4.2
    assert bank.reserves == 404.2
    assert bank.bonds == 0
    assert bank.bond_interests == 4.2


def test_government_repay_bonds_to_central_bank(bond_market_with_participants):
    # Given
    bond_market, govt, cb, _ = bond_market_with_participants
    bond_market.bonds.add_edge(govt, cb, principal=100)

    # When
    govt.repay_bonds()

    # Then
    assert govt.bonds == 0
    assert govt.reserves == -104.2
    assert govt.bond_interests == 4.2
    assert cb.reserves == 895.8
    assert cb.bonds == 0
    assert cb.bond_interests == 4.2


def test_bank_buy_bonds(bond_market_with_participants):
    # Given
    bond_market, govt, _, bank = bond_market_with_participants
    bonds = bond_market.bonds
    govt.bond_supply = 1000

    # When
    bank.buy_bonds()

    # Then
    assert bank.reserves == 100
    assert bank.bonds == 200
    assert govt.bonds == 200
    assert govt.reserves == 200
    assert bonds[govt][bank]["principal"] == 200


def test_central_bank_buy_remaining_bonds(bond_market_with_participants):
    # Given
    bond_market, govt, cb, _ = bond_market_with_participants
    bonds = bond_market.bonds
    govt.bond_supply = 1000

    # When
    cb.buy_remaining_bonds()

    # Then
    assert cb.reserves == 2000
    assert cb.bonds == 1000
    assert govt.bonds == 1000
    assert govt.reserves == 1000
    assert bonds[govt][cb]["principal"] == 1000
