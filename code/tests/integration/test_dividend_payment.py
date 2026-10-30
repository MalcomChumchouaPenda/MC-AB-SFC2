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
    household.country_pos = country.pos
    country.add_agents([household])
    return household


@pytest.fixture
def firm(model, country):
    # Given
    firm = Firm(model)
    firm.country_pos = country.pos
    country.add_agents([firm])
    return firm


@pytest.fixture
def before_firm_payment(firm, household, country):
    # Given
    citizen = household.roles["citizen"]
    citizen.fund_company(firm.id, 500)
    country.cash[household.id].amount = 0
    country.cash[firm.id].amount = 1000
    firm.dividends_payable = 200


@pytest.mark.usefixtures("before_firm_payment")
def test_increases_household_dividends_from_firm(firm, household):
    # When
    firm.pay_dividends()

    # Then
    assert firm.dividends_payable == 0
    assert firm.account["dividends"] == -200
    assert household.account["dividends"] == 200


@pytest.mark.usefixtures("before_firm_payment")
def test_decreases_firm_cash(firm, household, country):
    # Given
    firm_cash = country.cash[firm.id]
    household_cash = country.cash[household.id]

    # When
    firm.pay_dividends()

    # Then
    assert firm_cash.amount == 800
    assert household_cash.amount == 200


@pytest.fixture
def bank(model, country):
    # Given
    bank = Bank(model)
    bank.country_pos = country.pos
    country.add_agents([bank])
    return bank


@pytest.fixture
def before_bank_payment(bank, household, country):
    # Given
    citizen = household.roles["citizen"]
    citizen.fund_company(bank.id, 500)
    country.cash[household.id].amount = 0
    country.cash[bank.id].amount = 500
    bank.dividends_payable = 100


@pytest.mark.usefixtures("before_bank_payment")
def test_increases_household_dividends_from_bank(bank, household):
    # When
    bank.pay_dividends()

    # Then
    assert bank.dividends_payable == 0
    assert bank.account["dividends"] == -100
    assert household.account["dividends"] == 100


@pytest.mark.usefixtures("before_bank_payment")
def test_decreases_bank_cash(bank, household, country):
    # Given
    bank_cash = country.cash[bank.id]
    household_cash = country.cash[household.id]

    # When
    bank.pay_dividends()

    # Then
    assert bank_cash.amount == 400
    assert household_cash.amount == 100
