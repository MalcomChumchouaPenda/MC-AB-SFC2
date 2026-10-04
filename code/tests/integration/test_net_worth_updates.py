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


def test_firm_update_net_worth(firm, household):
    # Given
    firm.net_worth = 1000
    firm.net_cash_flow = 500
    firm.taxes_payable = 100
    firm.dividends_payable = 200
    firm.account["equities"] = -1000
    household.account["equities"] = 1000

    # When
    firm.update_net_worth()

    # Then
    assert firm.net_worth == 1200
    assert firm.account["equities"] == -1200
    assert household.account["equities"] == 1200


@pytest.fixture
def bank(fake_model, country, household):
    # Given
    bank = Bank(fake_model)
    country.place_bank(bank)
    citizen = household.roles["citizen"]
    citizen.fund_company(bank.id, 500)
    return bank


def test_bank_update_net_worth(bank, household):
    # Given
    bank.net_worth = 800
    bank.profit = 200
    bank.taxes_payable = 50
    bank.dividends_payable = 50
    bank.account["equities"] = -800
    household.account["equities"] = 800

    # When
    bank.update_net_worth()

    # Then
    assert bank.net_worth == 900
    assert bank.account["equities"] == -900
    assert household.account["equities"] == 900
