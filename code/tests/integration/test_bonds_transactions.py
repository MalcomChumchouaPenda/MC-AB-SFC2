import pytest
from unittest.mock import Mock
from mc_ab_sfc.agents import BankAgent, GovernmentAgent
from mc_ab_sfc.spaces import BondMarket


@pytest.fixture
def model():
    # Given
    model = Mock()
    model.p.mu2 = 0.1
    model.p.iota_b = 0
    return model


@pytest.fixture
def bond_market(model):
    # Given
    return BondMarket(model)


@pytest.fixture
def government(model, bond_market):
    # Given
    gov = GovernmentAgent(model)
    gov.bonds = 500
    gov.gdp = 1000
    issuer = bond_market.add_bond_issuer(gov)
    issuer.bond_supply = 1000
    return gov


@pytest.fixture
def bank(model, bond_market):
    # Given
    bank = BankAgent(model)
    bank.deposits = 1000
    bank.reserves = 300
    bank.bonds = 0
    bond_market.add_bond_buyer(bank)
    return bank


def test_bank_invests_excess_reserves(government, bank, bond_market):
    # Given
    graph = bond_market.graph
    buyer = bank.roles["bond_buyer"]
    issuer = government.roles["bond_issuer"]

    # When
    bank.invest_excess_reserves()

    # Then
    assert bank.reserves == 100
    assert bank.bonds == 200
    assert government.bonds == 700
    assert graph[issuer][buyer]["amount"] == 200
