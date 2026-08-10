import pytest
from unittest.mock import Mock
from mc_ab_sfc.agents import HouseholdAgent, GovernmentAgent
from mc_ab_sfc.spaces import CountrySpace


@pytest.fixture
def model():
    # Given
    return Mock()


@pytest.fixture
def household(model):
    # Given
    household = HouseholdAgent(model)
    household.labor_income = 100
    household.deposit_interest = 20
    household.dividends = 30
    household.rd_income = 10
    household.public_transfer = 40
    household.net_worth = 1000
    household.expected_consumption = 50
    return household


@pytest.fixture
def govt(model):
    govt = GovernmentAgent(model)
    govt.tax_rate = 0.25
    return govt


@pytest.fixture
def country(model):
    # Given
    return CountrySpace(model)


def test_household_computes_incomes_and_wealth(household, govt, country):
    # Given
    govt_role = country.add_government(govt)
    payer_role = country.add_tax_payer(household)
    country.assign_government(payer_role, govt_role)

    # When
    household.calc_gross_income()
    household.calc_disposable_income()
    expected_wealth = household.calc_expected_net_worth()

    # Then
    assert household.gross_income == pytest.approx(160)
    assert household.disposable_income == pytest.approx(160)
    assert expected_wealth == pytest.approx(1110)
