import math
import pytest
from agentpy import Model
from mc_ab_sfc.agents import HouseholdAgent
from mc_ab_sfc.spaces import EquitySpace, DepositMarket


@pytest.fixture
def model():
    # Given
    return Model({"lambda_": 0.8})


@pytest.fixture
def household(model):
    # Given
    household = HouseholdAgent(model)
    household.dividends = 10
    household.equity = 20
    household.net_worth = 110
    household.disposable_income = 40
    household.expected_consumption = 50
    return household


def test_household_portfolio_allocation(household, model):
    # Given
    equity_space = EquitySpace(model)
    equity_space.default_probability = 0.10
    equity_space.add_equity_holder(household)
    deposit_market = DepositMarket(model)
    deposit_market.deposit_rate = 0.05
    deposit_market.add_depositor(household)

    # When
    household.calc_portfolio_allocation()

    # Then
    lp = 0.8 * math.exp(-((10 * (1 - 0.10)) / 20 ) - 0.05)
    expected_equity = max(20, (1 - lp) * 100)
    expected_deposits = 100 - (expected_equity - 20)
    assert household.desired_equity == pytest.approx(expected_equity)
    assert household.desired_deposits == pytest.approx(expected_deposits)
