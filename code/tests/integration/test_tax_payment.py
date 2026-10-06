import pytest
from model.spaces.country import Country
from model.agents.firm import Firm
from model.agents.bank import Bank
from model.agents.household import Household
from model.agents.government import Government


@pytest.fixture
def model(fake_model):
    # Given
    model = fake_model
    model.p.initial_tax_rate = 0.10
    model.p.initial_discount_rate = 0.0
    model.p.initial_bond_rate = 0.0
    model.p.initial_wage = 0.0
    return model


@pytest.fixture
def country(model):
    # Given
    country = Country(model)
    country.create_markets()
    return country


@pytest.fixture
def govt(model, country):
    # Given
    govt = Government(model)
    country.add_government(govt)
    return govt


@pytest.fixture
def household(model, country):
    # Given
    household = Household(model)
    country.add_household(household)
    household.account["cash"] = 1000
    household.account["wages"] = 550
    household.account["dividends"] = 50
    household.account["public_transfers"] = 50
    return household


def test_increases_taxes_from_household(household, govt):
    # When
    household.pay_taxes()

    # Then
    assert household.account["taxes"] == -60
    assert govt.account["taxes"] == 60


def test_transfers_cash_from_household_to_govt(household, govt):
    # When
    household.pay_taxes()

    # Then
    assert household.account["cash"] == 940
    assert govt.account["cash"] == 60


@pytest.fixture
def firm(model, country):
    # Given
    firm = Firm(model)
    country.add_firm(firm)
    firm.taxes_payable = 100
    firm.account["cash"] = 1000
    return firm


def test_increases_taxes_from_firm(firm, govt):
    # When
    firm.pay_taxes()

    # Then
    assert firm.taxes_payable == 0
    assert firm.account["taxes"] == -100
    assert govt.account["taxes"] == 100


def test_tansfers_cash_from_firm_to_govt(firm, govt):
    # When
    firm.pay_taxes()

    # Then
    assert firm.account["cash"] == 900
    assert govt.account["cash"] == 100


@pytest.fixture
def bank(model, country):
    # Given
    bank = Bank(model)
    country.add_bank(bank)
    bank.taxes_payable = 100
    bank.account["cash"] = 1000
    return bank


def test_increases_taxes_from_bank(bank, govt):
    # When
    bank.pay_taxes()

    # Then
    assert bank.taxes_payable == 0
    assert bank.account["taxes"] == -100
    assert govt.account["taxes"] == 100


def test_transfers_cash_from_bank_govt(bank, govt):
    # When
    bank.pay_taxes()

    # Then
    assert bank.account["cash"] == 900
    assert govt.account["cash"] == 100
