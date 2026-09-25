from unittest.mock import Mock
import pytest
from agentpy import Model
from model.spaces.monetary_union import MonetaryUnion
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
def govt(model):
    # Given
    govt = Government(model)
    govt.setup()
    return govt


@pytest.fixture
def union(model):
    # Given
    union = MonetaryUnion(model)
    union.setup()
    return union


@pytest.fixture
def country(union):
    # Given
    country = union.spaces["country_0"]
    country.monetary_authority = Mock()
    country.spaces["good_market"] = Mock()
    return country


@pytest.fixture
def country_before_fiscal_policy(country, govt):
    # Given
    country.add_fiscal_authority(govt)
    return country


def test_government_updates_fiscal_policy(govt, country_before_fiscal_policy):
    # Given
    country = country_before_fiscal_policy
    country.spaces["good_market"].average_price = 2
    country.spaces["good_market"].average_prod = 3
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
def household(model):
    # Given
    household = Household(model)
    household.setup()
    return household


@pytest.fixture
def firm(model):
    # Given
    firm = Firm(model)
    firm.setup()
    return firm


@pytest.fixture
def bank(model):
    # Given
    bank = Bank(model)
    bank.setup()
    return bank


@pytest.fixture
def country_before_tax_payment(country, govt, household, firm, bank):
    # Given
    country.add_fiscal_authority(govt)
    country.add_citizen(household)
    country.add_company(firm, "FT")
    country.add_company(bank, "B")
    return country


@pytest.mark.usefixtures("country_before_tax_payment")
def test_household_pay_taxes(household, govt):
    # Given
    govt.tax_rate = 0.10
    household.account.stocks["cash"] = 1000
    household.account.flows["wages"] = 550
    household.account.flows["dividends"] = 50
    household.account.flows["public_transfers"] = 50

    # When
    household.pay_taxes()

    # Then
    assert household.account.flows["taxes"] == -60
    assert household.account.stocks["cash"] == 940
    assert govt.account.flows["taxes"] == 60
    assert govt.account.stocks["cash"] == 60


@pytest.mark.usefixtures("country_before_tax_payment")
def test_firm_pay_taxes(firm, govt):
    # Given
    govt.tax_rate = 0.10
    firm.taxes_payable = 100
    firm.account.stocks["cash"] = 1000

    # When
    firm.pay_taxes()

    # Then
    assert firm.taxes_payable == 0
    assert firm.account.flows["taxes"] == -100
    assert firm.account.stocks["cash"] == 900
    assert govt.account.flows["taxes"] == 100
    assert govt.account.stocks["cash"] == 100


@pytest.mark.usefixtures("country_before_tax_payment")
def test_bank_pay_taxes(bank, govt):
    # Given
    govt.tax_rate = 0.10
    bank.taxes_payable = 100
    bank.account.stocks["cash"] = 1000

    # When
    bank.pay_taxes()

    # Then
    assert bank.taxes_payable == 0
    assert bank.account.flows["taxes"] == -100
    assert bank.account.stocks["cash"] == 900
    assert govt.account.flows["taxes"] == 100
    assert govt.account.stocks["cash"] == 100
