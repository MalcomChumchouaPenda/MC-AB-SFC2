import pytest
from unittest.mock import Mock, PropertyMock
from mc_ab_sfc.agents import Bank, Firm, Government
from mc_ab_sfc.spaces import DepositMarket


@pytest.fixture
def model():
    # Given
    model = Mock()
    model.p.zeta = 0.8
    return model


@pytest.fixture
def bank(model):
    # Given
    bank = Bank(model)
    bank.setup()
    bank.country = "any"
    bank.deposit_rate = 0.02
    return bank


@pytest.fixture
def firm(model):
    # Given
    firm = Firm(model)
    firm.setup()
    return firm


@pytest.fixture
def deposit_market_with_participants(model, firm, bank):
    # Given
    market = DepositMarket(model)
    market.setup()
    deposits = market.deposits
    deposits.add_node(bank, role="bank")
    deposits.add_edge(firm, bank, amount=2000)
    model.deposit_markets = {"any": market}
    return market, firm, bank


def test_bank_pays_deposit_interest_to_firm(deposit_market_with_participants):
    # Given
    _, firm, bank = deposit_market_with_participants

    # When
    bank.pay_deposit_interests()
    # bank.update_deposit_rate() # TODO

    # Then
    assert firm.deposits == pytest.approx(2040)
    assert bank.deposits == pytest.approx(2040)
    assert firm.dep_interests == pytest.approx(40)
    assert bank.dep_interests == pytest.approx(40)


@pytest.fixture
def govt(model):
    # Given
    govt = Government(model)
    govt.setup()
    govt.country = "any"
    return govt


def test_government_activate_deposit_guarantee(govt, deposit_market_with_participants):
    # Given
    _, firm, bank = deposit_market_with_participants
    bank.defaulted = True

    # When
    govt.issue_deposit_guarantee_bonds()
    govt.reimburse_deposits()

    # Then
    assert govt.bond_supply == 2000
    assert govt.reserves == -2000
    assert firm.deposits == 0
    assert firm.cash == 2000
    assert bank.deposits == 0
    assert bank.reserves == 0
