from unittest.mock import Mock
import pytest
from model.spaces.country import Country
from model.agents.household import Household
from model.agents.firm import Firm
from model.agents.bank import Bank


@pytest.fixture
def model(fake_model):
    # Given
    model = fake_model
    model.p.initial_tax_rate = 0.0
    model.p.initial_discount_rate = 0.0
    model.p.initial_wage = 0.0
    model.p.xi = 0.5
    model.p.xi_deltap = 1.5
    model.p.long_run_rate = 0.02
    model.p.inflation_target = 0.02
    return model


@pytest.fixture
def country(model):
    # Given
    country = Country(model)
    country.create_markets()
    return country


@pytest.fixture
def household(model, country):
    # Given
    household = Household(model)
    country.add_household(household)
    return household


@pytest.fixture
def firm(model, country, household):
    # Given
    firm = Firm(model)
    country.add_firm(firm)
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
def bank(model, country, household):
    # Given
    bank = Bank(model)
    country.add_bank(bank)
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
