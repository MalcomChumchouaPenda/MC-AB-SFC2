from unittest.mock import Mock
import pytest
from model.agents.household import Household
from model.spaces.country import Country


@pytest.fixture
def model(fake_model, monkeypatch):
    model = fake_model
    model.p.initial_tax_rate = 0.0
    model.p.initial_discount_rate = 0.0
    model.p.initial_wage = 0.0
    model.p.delta = 0.1
    model.p.upsilon = 1.0
    monkeypatch.setattr(model, "nprandom", Mock())
    return model


@pytest.fixture
def country(model):
    # Given
    country = Country(model)
    country.create_markets()
    return country


@pytest.fixture
def market(country):
    # Given
    market = country.spaces["labor_market"]
    return market


@pytest.fixture
def household(model, country):
    # Given
    household = Household(model)
    household.country_pos = country.pos
    household.reservation_wage = 100
    country.add_agents([household])
    return household


def test_household_revises_reservation_wage_when_fully_employed(household, market):
    # Given
    market.unemployment_rate = 0.05
    household.prev_labor_sold = 1.0
    household.model.nprandom.choice.return_value = 1
    household.model.nprandom.uniform.return_value = 0.05

    # When
    household.revise_reservation_wage()

    # Then
    assert household.reservation_wage == pytest.approx(105)


def test_household_revises_reservation_wage_when_not_fully_employed(household, market):
    # Given
    market.unemployment_rate = 0.30
    household.prev_labor_sold = 0.0
    household.model.nprandom.choice.return_value = 1
    household.model.nprandom.uniform.return_value = 0.05

    # When
    household.revise_reservation_wage()

    # Then
    assert household.reservation_wage == pytest.approx(95)


def test_household_dont_revises_reservation_wage(household, market):
    # Given
    market.unemployment_rate = 0.30
    household.prev_labor_sold = 0.0
    household.model.nprandom.choice.return_value = 0
    household.model.nprandom.uniform.return_value = 0.05

    # When
    household.revise_reservation_wage()

    # Then
    assert household.reservation_wage == pytest.approx(100)
