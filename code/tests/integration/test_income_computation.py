import pytest
from unittest.mock import Mock
from mc_ab_sfc.agents import HouseholdAgent, FirmAgent
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
def country(model):
    # Given
    country = CountrySpace(model)
    country.tax_rate = 0.25
    return country


def test_household_computes_incomes_and_wealth(household, country):
    # Given
    country.add_tax_payer(household)

    # When
    household.calc_gross_income()
    household.calc_disposable_income()
    expected_wealth = household.calc_expected_net_worth()

    # Then
    assert household.gross_income == pytest.approx(160)
    assert household.disposable_income == pytest.approx(160)
    assert expected_wealth == pytest.approx(1110)


@pytest.fixture
def firm(model):
    # Given
    firm = FirmAgent(model)
    firm.sales = 1000
    firm.productivity = 2
    firm.wage_offer = 20
    firm.inventories = 60
    firm.prev_inventories = 50
    firm.deposit_interest = 30
    firm.loan_interest = 30
    firm.wage_bill = 300
    firm.rd = 100
    return firm


def test_firm_calc_profits_and_taxes(firm, country):
    # Given
    country.add_tax_payer(firm)
    firm.p.rho = 0.10

    # When
    firm.calc_profit()
    firm.calc_taxes()
    firm.calc_dividends()

    # Then
    assert firm.profits == pytest.approx(700)
    assert firm.net_cash_flow == pytest.approx(600)
    assert firm.taxes_payable == pytest.approx(150.0)
    assert firm.dividends_payable == pytest.approx(45.0)
