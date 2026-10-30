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
    model.p.household_number = 0
    model.p.initial_public_transfer = 0.0
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
    govt.country_pos = country.pos
    country.add_agents([govt])
    return govt


@pytest.fixture
def household(model, country):
    # Given
    household = Household(model)
    household.country_pos = country.pos
    country.add_agents([household])
    country.cash[household.id].amount = 1000
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


def test_transfers_cash_from_household_to_govt(household, govt, country):
    # Given
    cash = country.cash

    # When
    household.pay_taxes()

    # Then
    assert cash[household.id].amount == 940
    assert cash[govt.id].amount == 60


@pytest.fixture
def firm(model, country):
    # Given
    firm = Firm(model)
    firm.taxes_payable = 100
    firm.country_pos = country.pos
    country.add_agents([firm])
    country.cash[firm.id].amount = 1000
    return firm


def test_increases_taxes_from_firm(firm, govt):
    # When
    firm.pay_taxes()

    # Then
    assert firm.taxes_payable == 0
    assert firm.account["taxes"] == -100
    assert govt.account["taxes"] == 100


def test_tansfers_cash_from_firm_to_govt(firm, govt, country):
    # Given
    cash = country.cash

    # When
    firm.pay_taxes()

    # Then
    assert cash[firm.id].amount == 900
    assert cash[govt.id].amount == 100


@pytest.fixture
def bank(model, country):
    # Given
    bank = Bank(model)
    bank.country_pos = country.pos
    bank.taxes_payable = 100
    country.add_agents([bank])
    country.cash[bank.id].amount = 1000
    return bank


def test_increases_taxes_from_bank(bank, govt):
    # When
    bank.pay_taxes()

    # Then
    assert bank.taxes_payable == 0
    assert bank.account["taxes"] == -100
    assert govt.account["taxes"] == 100


def test_transfers_cash_from_bank_govt(bank, govt, country):
    # Given
    cash = country.cash

    # When
    bank.pay_taxes()

    # Then
    assert cash[bank.id].amount == 900
    assert cash[govt.id].amount == 100
