from unittest.mock import Mock
import pytest
from model.spaces.country import Country
from model.agents.household import Household
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
def bank(model, country):
    # Given
    bank = Bank(model)
    country.add_bank(bank)
    return bank


@pytest.fixture
def household(model, country, bank):
    # Given
    household = Household(model)
    household.deposit_bank_id = bank.id
    country.add_household(household)
    role = household.roles["depositor"]
    role.join_deposit_bank(bank.id)
    return household


def test_household_portfolio_allocation(country, household, bank):
    # Given
    country.p.zeta = 1.0  # for deposit rate computaion
    country.discount_rate = 0.05
    country.prob_failure = 0.0
    household.p.lambda_ = 0.4
    household.disposable_income = 100
    household.expected_consumption = 50
    household.account["dividends"] = 2.5
    household.account["equities"] = 50
    household.account["deposits"] = 0
    household.account["cash"] = 0

    # When
    household.choose_portfolio_allocation()

    # Then
    assert household.desired_equity == pytest.approx(60.0)
    assert household.desired_deposits == pytest.approx(90.0)
