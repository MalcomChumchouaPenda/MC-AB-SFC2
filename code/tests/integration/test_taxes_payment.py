import pytest
from unittest.mock import Mock, PropertyMock
from mc_ab_sfc.spaces import CountrySpace
from mc_ab_sfc.agents import Household, Firm, Bank, Government


@pytest.fixture
def model():
    # Given
    model = Mock()
    return model


@pytest.fixture
def govt(model):
    # Given
    govt = Government(model)
    govt.tax_rate = 0.10
    model.governments = {"any": govt}
    return govt


@pytest.fixture
def household(model, monkeypatch):
    monkeypatch.setattr(Household, "dep_interests", PropertyMock(return_value=20))
    household = Household(model)
    household.country = "any"
    household.cash = 1000
    household.labor_income = 540
    household.dividends = 30
    household.rd_income = 10
    household.public_transfers = 50
    return household


def test_household_pay_taxes(household, govt):

    # When
    household.pay_taxes()

    # Then
    assert household.taxes == 60
    assert household.cash == 940
    assert govt.taxes == 60
    assert govt.reserves == 60


@pytest.fixture
def firm(model):
    # Given
    firm = Firm(model)
    firm.country = "any"
    firm.cash = 1000
    firm.taxes_payable = 100
    return firm


def test_firm_pay_taxes(firm, govt):
    # When
    firm.pay_taxes()

    # Then
    assert firm.taxes_payable == 0
    assert firm.taxes == 100
    assert firm.cash == 900
    assert govt.taxes == 100
    assert govt.reserves == 100


@pytest.fixture
def bank(model):
    # Given
    bank = Bank(model)
    bank.country = "any"
    bank.reserves = 1000
    bank.taxes_payable = 100
    return bank


def test_bank_pay_taxes(bank, govt):
    # When
    bank.pay_taxes()

    # Then
    assert bank.taxes_payable == 0
    assert bank.taxes == 100
    assert bank.reserves == 900
    assert govt.taxes == 100
    assert govt.reserves == 100
