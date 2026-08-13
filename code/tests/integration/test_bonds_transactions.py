import pytest
from unittest.mock import Mock
from mc_ab_sfc.agents import BankAgent, CentralBankAgent, GovernmentAgent
from mc_ab_sfc.spaces import BondMarket, CountrySpace


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
    govt = GovernmentAgent(model)
    govt.bonds = 500
    govt.gdp = 1000
    govt.budget_deficit = 200
    govt.prev_budget_surplus = 50
    return govt


@pytest.fixture
def bank(model):
    # Given
    bank = BankAgent(model)
    bank.deposits = 1000
    bank.reserves = 300
    bank.bonds = 0
    return bank


@pytest.fixture
def central_bank(model):
    # Given
    central_bank = CentralBankAgent(model)
    central_bank.reserves = 1000
    return central_bank


@pytest.fixture
def bond_market(model):
    # Given
    return BondMarket(model)


@pytest.fixture
def country(model):
    # Given
    country = CountrySpace(model)
    country.discount_rate = 0.04
    return country

def test_government_issues_bonds(govt, bond_market):
    # Given
    issuer = bond_market.add_bond_issuer(govt)

    # When
    govt.issue_bonds()

    # Then
    assert issuer.bond_supply == 150


def test_government_pays_bond_debt_to_bank(govt, bank, country, bond_market):
    # Given
    country.add_government(govt)
    issuer = bond_market.add_bond_issuer(govt)
    buyer = bond_market.add_bond_buyer(bank)
    graph = bond_market.graph
    graph.add_edge(issuer, buyer, amount=100)

    # When
    govt.pay_bond_debt()

    # Then
    assert govt.bonds == 400
    assert govt.reserves == -105.0
    assert govt.bond_interest == 5.0
    assert bank.reserves == 405.0
    assert bank.bonds == -100
    assert bank.bond_interest == 5.0


def test_government_pays_bond_debt_to_central_bank(govt, central_bank, country, bond_market):
    # Given
    country.add_government(govt)
    issuer = bond_market.add_bond_issuer(govt)
    buyer = bond_market.add_bond_buyer(central_bank)
    graph = bond_market.graph
    graph.add_edge(issuer, buyer, amount=100)

    # When
    govt.pay_bond_debt()

    # Then
    assert govt.bonds == 400
    assert govt.reserves == -105.0
    assert govt.bond_interest == 5.0
    assert central_bank.reserves == 895.0
    assert central_bank.bonds == -100
    assert central_bank.bond_interest == 5.0


def test_bank_invests_excess_reserves(govt, bank, bond_market):
    # Given
    graph = bond_market.graph
    buyer = bond_market.add_bond_buyer(bank)
    issuer = bond_market.add_bond_issuer(govt)
    issuer.bond_supply = 1000

    # When
    bank.invest_excess_reserves()

    # Then
    assert bank.reserves == 100
    assert bank.bonds == 200
    assert govt.bonds == 700
    assert govt.reserves == 200
    assert graph[issuer][buyer]["amount"] == 200


def test_central_bank_buy_remaining_bonds(govt, central_bank, bond_market):
    # Given
    graph = bond_market.graph
    buyer = bond_market.add_bond_buyer(central_bank)
    issuer = bond_market.add_bond_issuer(govt)
    issuer.bond_supply = 1000

    # When
    central_bank.buy_remaining_bonds()

    # Then
    assert central_bank.reserves == 2000
    assert central_bank.bonds == 1000
    assert govt.bonds == 1500
    assert govt.reserves == 1000
    assert graph[issuer][buyer]["amount"] == 1000
