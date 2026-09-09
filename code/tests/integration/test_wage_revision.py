import pytest
from unittest.mock import Mock
from model.agents.household import Household
from model.spaces.labor_market import LaborMarket


@pytest.fixture
def model():
    model = Mock()
    model.p.delta = 0.1
    model.p.upsilon = 1.0
    model.p.upsilon_h = 1.0
    return model


@pytest.fixture
def market(model):
    market = LaborMarket(model)
    market.setup()
    return market


@pytest.fixture
def household(model):
    household = Household(model)
    household.setup()
    household.reservation_wage = 100
    return household


def test_household_revises_reservation_wage_when_fully_employed(household, market):
    # Given
    market.unemployment_rate = 0.05
    worker = market.add_worker(household)
    worker.labor_supply = 0.0
    household.model.nprandom.choice.return_value = 1
    household.model.nprandom.uniform.return_value = 0.05

    # When
    household.revise_reservation_wage()

    # Then
    assert household.reservation_wage == pytest.approx(105)


def test_household_revises_reservation_wage_when_not_fully_employed(household, market):
    # Given
    market.unemployment_rate = 0.30
    worker = market.add_worker(household)
    worker.labor_supply = 1.0
    household.model.nprandom.choice.return_value = 1
    household.model.nprandom.uniform.return_value = 0.05

    # When
    household.revise_reservation_wage()

    # Then
    assert household.reservation_wage == pytest.approx(95)


def test_household_dont_revises_reservation_wage(household, market):
    # Given
    market.unemployment_rate = 0.30
    worker = market.add_worker(household)
    worker.labor_supply = 1.0
    household.model.nprandom.choice.return_value = 0
    household.model.nprandom.uniform.return_value = 0.05

    # When
    household.revise_reservation_wage()

    # Then
    assert household.reservation_wage == pytest.approx(100)
