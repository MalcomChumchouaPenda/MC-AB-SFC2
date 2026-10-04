from unittest.mock import Mock
import pytest
from agentpy import Model
from model.spaces.country import Country
from model.agents.firm import Firm
from model.agents.bank import Bank
from model.agents.household import Household
from model.agents.government import Government


@pytest.fixture
def model(monkeypatch):
    # Given
    model = Model()
    model.p.K = 1
    model.p.dmax = 0.05
    model.p.tax_min = 0.10
    model.p.tax_max = 0.50
    model.p.g_min = 0.05
    model.p.g_max = 0.20
    model.p.delta = 0.10
    uniform = Mock(return_value=0.05)
    monkeypatch.setattr(model.random, "uniform", uniform)
    return model


@pytest.fixture
def country(fake_model):
    # Given
    country = Country(fake_model)
    country.monetary_authority = Mock()
    country.create_markets()
    return country


@pytest.fixture
def govt(model, country):
    # Given
    govt = Government(model)
    country.place_government(govt)
    return govt


def test_government_updates_fiscal_policy(govt, country):
    # Given
    country.spaces["goods_market"].average_price = 2
    country.spaces["goods_market"].average_prod = 3
    country.gdp = 1000
    govt.prev_public_spending = 10
    govt.public_spending = 100
    govt.budget_deficit = 100
    govt.tax_rate = 0.20

    # When
    govt.update_fiscal_policy()

    # Then
    assert govt.desired_public_spending == pytest.approx(60)
    assert govt.public_spending == pytest.approx(95)
    assert govt.tax_rate == pytest.approx(0.21)


@pytest.fixture
def household(model, country):
    # Given
    household = Household(model)
    country.place_household(household)
    return household


@pytest.fixture
def firm(model, country):
    # Given
    firm = Firm(model)
    country.place_firm(firm)
    return firm


@pytest.fixture
def bank(model, country):
    # Given
    bank = Bank(model)
    country.place_bank(bank)
    return bank


def test_household_pay_taxes(household, govt):
    # Given
    govt.tax_rate = 0.10
    household.account["cash"] = 1000
    household.account["wages"] = 550
    household.account["dividends"] = 50
    household.account["public_transfers"] = 50

    # When
    household.pay_taxes()

    # Then
    assert household.account["taxes"] == -60
    assert household.account["cash"] == 940
    assert govt.account["taxes"] == 60
    assert govt.account["cash"] == 60


def test_firm_pay_taxes(firm, govt):
    # Given
    govt.tax_rate = 0.10
    firm.taxes_payable = 100
    firm.account["cash"] = 1000

    # When
    firm.pay_taxes()

    # Then
    assert firm.taxes_payable == 0
    assert firm.account["taxes"] == -100
    assert firm.account["cash"] == 900
    assert govt.account["taxes"] == 100
    assert govt.account["cash"] == 100


def test_bank_pay_taxes(bank, govt):
    # Given
    govt.tax_rate = 0.10
    bank.taxes_payable = 100
    bank.account["cash"] = 1000

    # When
    bank.pay_taxes()

    # Then
    assert bank.taxes_payable == 0
    assert bank.account["taxes"] == -100
    assert bank.account["cash"] == 900
    assert govt.account["taxes"] == 100
    assert govt.account["cash"] == 100
