from unittest.mock import Mock
import pytest
from model.spaces.country import Country
from model.agents.household import Household
from model.agents.firm import Firm
from model.agents.bank import Bank


@pytest.fixture
def country(fake_model):
    # Given
    country = Country(fake_model)
    country.create_markets()
    country.monetary_authority = Mock()
    return country


@pytest.fixture
def household(fake_model, country):
    # Given
    household = Household(fake_model)
    country.place_household(household)
    return household


@pytest.fixture
def firm(fake_model, country, household):
    # Given
    firm = Firm(fake_model)
    country.place_firm(firm)
    citizen = household.roles["citizen"]
    citizen.fund_company(firm.id, 500)
    return firm


def test_increases_household_dividends_from_firm(firm, household):
    # Given
    household.account["cash"] = 0
    firm.account["cash"] = 1000
    firm.dividends_payable = 200

    # When
    firm.pay_dividends()

    # Then
    assert firm.dividends_payable == 0
    assert firm.account["dividends"] == -200
    assert household.account["dividends"] == 200


def test_decreases_firm_cash(firm, household):
    # Given
    household.account["cash"] = 0
    firm.account["cash"] = 1000
    firm.dividends_payable = 200

    # When
    firm.pay_dividends()

    # Then
    assert firm.account["cash"] == 800
    assert household.account["cash"] == 200


@pytest.fixture
def bank(fake_model, country, household):
    # Given
    bank = Bank(fake_model)
    country.place_bank(bank)
    citizen = household.roles["citizen"]
    citizen.fund_company(bank.id, 500)
    return bank


def test_increases_household_dividends_from_bank(bank, household):
    # Given
    household.account["cash"] = 0
    bank.account["cash"] = 500
    bank.dividends_payable = 100

    # When
    bank.pay_dividends()

    # Then
    assert bank.dividends_payable == 0
    assert bank.account["dividends"] == -100
    assert household.account["dividends"] == 100


def test_decreases_bank_cash(bank, household):
    # Given
    household.account["cash"] = 0
    bank.account["cash"] = 500
    bank.dividends_payable = 100

    # When
    bank.pay_dividends()

    # Then
    assert bank.account["cash"] == 400
    assert household.account["cash"] == 100
