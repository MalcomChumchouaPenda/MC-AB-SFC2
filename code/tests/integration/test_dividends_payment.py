import pytest
from unittest.mock import Mock
from mc_ab_sfc.agents import HouseholdAgent, FirmAgent, BankAgent
from mc_ab_sfc.spaces import EquitySpace


@pytest.fixture
def model():
    # Given
    model = Mock()
    return model


@pytest.fixture
def household(model):
    # Given
    household = HouseholdAgent(model)
    return household


@pytest.fixture
def equity_space(model):
    # Given
    return EquitySpace(model)


def test_firm_pay_dividends(model, household, equity_space):
    # Given
    firm = FirmAgent(model)
    firm.cash = 1000
    firm.dividends_payable = 200
    holder = equity_space.add_equity_holder(household)
    issuer = equity_space.add_equity_issuer(firm)
    equity_space.assign_equity_holder(holder, issuer, 1.0)

    # When
    firm.pay_dividends()

    # Then
    assert firm.dividends_payable == 0
    assert firm.dividends == 200
    assert firm.cash == 800
    assert household.cash == 200
    assert household.dividends == 200


def test_bank_pay_dividends(model, household, equity_space):
    # Given
    bank = BankAgent(model)
    bank.reserves = 500
    bank.dividends_payable = 100
    holder = equity_space.add_equity_holder(household)
    issuer = equity_space.add_equity_issuer(bank)
    equity_space.assign_equity_holder(holder, issuer, 1.0)

    # When
    bank.pay_dividends()

    # Then
    assert bank.dividends_payable == 0
    assert bank.dividends == 100
    assert bank.reserves == 400
    assert household.cash == 100
    assert household.dividends == 100
