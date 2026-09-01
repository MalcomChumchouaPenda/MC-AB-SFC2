import pytest
from unittest.mock import Mock
from model.spaces.country import Country
from model.agents.household import Household
from model.agents.firm import Firm
from model.agents.bank import Bank


@pytest.fixture
def model():
    # Given
    model = Mock()
    return model


@pytest.fixture
def household(model):
    # Given
    household = Household(model)
    return household


@pytest.fixture
def firm(model):
    # Given
    firm = Firm(model)
    firm.cash = 1000
    firm.dividends_payable = 200
    return firm


@pytest.fixture
def country(model):
    # Given
    return Country(model)


def test_firm_pay_dividends(firm, household, country):
    # Given
    holder = country.add_equity_holder(household)
    holder.share = 1.0
    issuer = country.add_equity_issuer(firm)
    country.assign_equity_holder(issuer, holder)

    # When
    firm.pay_dividends()

    # Then
    assert firm.dividends_payable == 0
    assert firm.dividends == 200
    assert firm.cash == 800
    assert household.cash == 200
    assert household.dividends == 200


@pytest.fixture
def bank(model):
    # Given
    bank = Bank(model)
    bank.reserves = 500
    bank.dividends_payable = 100
    return bank


def test_bank_pay_dividends(bank, household, country):
    # Given
    holder = country.add_equity_holder(household)
    holder.share = 1.0
    issuer = country.add_equity_issuer(bank)
    country.assign_equity_holder(issuer, holder)

    # When
    bank.pay_dividends()

    # Then
    assert bank.dividends_payable == 0
    assert bank.dividends == 100
    assert bank.reserves == 400
    assert household.cash == 100
    assert household.dividends == 100
