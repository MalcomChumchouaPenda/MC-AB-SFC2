import math
import pytest
from unittest.mock import Mock
from mc_ab_sfc.spaces import CountrySpace, DepositMarket
from mc_ab_sfc.agents import Household, Bank


@pytest.fixture
def model():
    # Given
    model = Mock()
    model.p.lambda_ = 0.8
    return model


@pytest.fixture
def household(model):
    # Given
    household = Household(model)
    household.dividends = 10
    household.equity = 20
    household.net_worth = 110
    household.disposable_income = 40
    household.expected_consumption = 50
    return household


@pytest.fixture
def bank(model):
    # Given
    bank = Bank(model)
    bank.deposit_rate = 0.05
    return bank


@pytest.fixture
def country(model):
    # Given
    country = CountrySpace(model)
    country.default_probability = 0.10
    return country


def test_household_portfolio_allocation(household, bank, country):
    # Given
    country.add_equity_holder(household)
    household.deposit_bank = bank

    # When
    household.calc_portfolio_allocation()

    # Then
    lp = 0.8 * math.exp(-((10 * (1 - 0.10)) / 20) - 0.05)
    expected_equity = max(20, (1 - lp) * 100)
    expected_deposits = 100 - (expected_equity - 20)
    assert household.desired_equity == pytest.approx(expected_equity)
    assert household.desired_deposits == pytest.approx(expected_deposits)
