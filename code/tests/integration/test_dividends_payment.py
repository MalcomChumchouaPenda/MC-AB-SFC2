import pytest
from unittest.mock import Mock
from mc_ab_sfc.agents import HouseholdAgent, FirmAgent, BankAgent, GovernmentAgent
from mc_ab_sfc.spaces import CountrySpace


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
def govt(model):
    # Given
    return GovernmentAgent(model)


@pytest.fixture
def country(model, govt):
    # Given
    return CountrySpace(model, govt)


def test_firm_pay_dividends(model, household, country):
    # Given
    firm = FirmAgent(model)
    firm.cash = 1000
    firm.dividends_payable = 200
    holder = country.add_equity_holder(household)
    issuer = country.add_equity_issuer(firm)
    country.assign_equity_holder(holder, issuer, 1.0)

    # When
    firm.pay_dividends()

    # Then
    assert firm.dividends_payable == 0
    assert firm.dividends == 200
    assert firm.cash == 800
    assert household.cash == 200
    assert household.dividends == 200


def test_bank_pay_dividends(model, household, country):
    # Given
    bank = BankAgent(model)
    bank.reserves = 500
    bank.dividends_payable = 100
    holder = country.add_equity_holder(household)
    issuer = country.add_equity_issuer(bank)
    country.assign_equity_holder(holder, issuer, 1.0)

    # When
    bank.pay_dividends()

    # Then
    assert bank.dividends_payable == 0
    assert bank.dividends == 100
    assert bank.reserves == 400
    assert household.cash == 100
    assert household.dividends == 100
