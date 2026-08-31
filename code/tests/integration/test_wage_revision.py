import pytest
from unittest.mock import Mock
from model.agents.private import Household
from model.spaces.real import LaborMarket


@pytest.fixture
def model():
    model = Mock()
    model.p.delta = 0.1
    model.p.upsilon = 1.0
    model.p.upsilon_h = 1.0
    return model


@pytest.fixture
def market(model):
    return LaborMarket(model)


@pytest.fixture
def household(model):
    household = Household(model)
    household.labor_supply = 1.0
    household.reservation_wage = 100
    return household


def test_household_revises_reservation_wage_when_fully_employed(household, market):
    # Given
    household.employed_labor = 1.0
    household.model.nprandom.choice.return_value = 1
    household.model.nprandom.uniform.return_value = 0.05
    market.unemployment_rate = 0.05
    market.add_worker(household)

    # When
    household.revise_reservation_wage()

    # Then
    assert household.reservation_wage == pytest.approx(105)


def test_household_revises_reservation_wage_when_not_fully_employed(household, market):
    # Given
    household.employed_labor = 0.0
    household.model.nprandom.choice.return_value = 1
    household.model.nprandom.uniform.return_value = 0.05
    market.unemployment_rate = 0.30
    market.add_worker(household)

    # When
    household.revise_reservation_wage()

    # Then
    assert household.reservation_wage == pytest.approx(95)


def test_household_dont_revises_reservation_wage(household, market):
    # Given
    household.employed_labor = 0.0
    household.model.nprandom.choice.return_value = 0
    household.model.nprandom.uniform.return_value = 0.05
    market.unemployment_rate = 0.30
    market.add_worker(household)

    # When
    household.revise_reservation_wage()

    # Then
    assert household.reservation_wage == pytest.approx(100)
