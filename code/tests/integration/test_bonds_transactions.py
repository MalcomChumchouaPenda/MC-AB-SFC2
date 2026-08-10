import pytest
from unittest.mock import Mock
from mc_ab_sfc.agents import BankAgent, CentralBankAgent, GovernmentAgent
from mc_ab_sfc.spaces import BondMarket


@pytest.fixture
def model():
    # Given
    model = Mock()
    model.p.mu2 = 0.1
    model.p.iota_b = 0
    return model


@pytest.fixture
def govt(model):
    # Given
    gov = GovernmentAgent(model)
    gov.bonds = 500
    gov.gdp = 1000
    return gov


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
