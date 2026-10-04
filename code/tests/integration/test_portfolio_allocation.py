from unittest.mock import Mock
import pytest
from model.spaces.country import Country
from model.agents.household import Household
from model.agents.bank import Bank


@pytest.fixture
def country(fake_model):
    # Given
    country = Country(fake_model)
    country.create_markets()
    return country


@pytest.fixture
def bank(fake_model, country):
    # Given
    bank = Bank(fake_model)
    country.place_bank(bank)
    return bank


@pytest.fixture
def household(fake_model, country, bank):
    # Given
    household = Household(fake_model)
    household.deposit_bank_id = bank.id
    country.place_household(household)
    role = household.roles["depositor"]
    role.join_deposit_bank(bank.id)
    return household


def test_household_portfolio_allocation(country, household, bank):
    # Given
    country.prob_failure = 0.0
    household.p.lambda_ = 0.4
    household.disposable_income = 100
    household.expected_consumption = 50
    household.account["dividends"] = 2.5
    household.account["equities"] = 50
    household.account["deposits"] = 0
    household.account["cash"] = 0
    bank.roles["deposit_bank"].deposit_rate = 0.05

    # When
    household.choose_portfolio_allocation()

    # Then
    assert household.desired_equity == pytest.approx(60.0)
    assert household.desired_deposits == pytest.approx(90.0)
