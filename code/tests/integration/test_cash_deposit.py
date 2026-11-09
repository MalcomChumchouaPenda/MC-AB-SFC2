import pytest
from model.agents.bank import Bank
from model.agents.firm import Firm
from model.agents.household import Household
from model.spaces.country import Country


@pytest.fixture
def model(fake_model):
    # Given
    model = fake_model
    model.p.initial_wage = 0.0
    model.p.country_number = 1
    model.p.household_number = 0
    model.p.initial_public_transfer = 0.0
    model.p.initial_tax_rate = 0.0
    model.p.initial_discount_rate = 0.0
    model.p.initial_bond_rate = 0.0
    return model


@pytest.fixture
def country(model):
    # Given
    country = Country(model)
    country.create_markets()
    return country


@pytest.fixture
def bank(model, country):
    # Given
    bank = Bank(model)
    bank.country_pos = 0
    country.add_agents([bank])
    return bank


@pytest.fixture
def firm(model, country, bank):
    # Given
    firm = Firm(model)
    firm.country_pos = 0
    country.add_agents([firm])
    firm.account["cash"] = 1000
    depositor = firm.roles["country_0_depositor"]
    deposit_bank = bank.roles["deposit_bank"]
    market = country.spaces["deposit_market"]
    market.join_deposit_bank(depositor, deposit_bank)
    return firm


def test_decreases_firm_cash(firm, bank):
    # Given
    depositor = firm.roles["country_0_depositor"]
    deposit_bank = bank.roles["deposit_bank"]

    # When
    depositor.make_deposits(deposit_bank.id, 200)

    # Then
    assert firm.account["cash"] == 800
    assert bank.account["cash"] == 200


def test_increases_firm_deposits(firm, bank):
    # Given
    depositor = firm.roles["country_0_depositor"]
    deposit_bank = bank.roles["deposit_bank"]

    # When
    depositor.make_deposits(deposit_bank.id, 200)

    # Then
    assert firm.account["deposits"] == 200
    assert bank.account["deposits"] == -200


@pytest.fixture
def household(model, country, bank):
    # Given
    household = Household(model)
    household.country_pos = 0
    country.add_agents([household])
    household.account["cash"] = 1000
    depositor = household.roles["depositor"]
    deposit_bank = bank.roles["deposit_bank"]
    market = country.spaces["deposit_market"]
    market.join_deposit_bank(depositor, deposit_bank)
    return household


def test_decreases_household_cash(household, bank, country):
    # Given
    depositor = household.roles["depositor"]
    deposit_bank = bank.roles["deposit_bank"]

    # When
    depositor.make_deposits(deposit_bank.id, 400)

    # Then
    assert household.account["cash"] == 600
    assert bank.account["cash"] == 400


def test_increases_household_deposits(household, bank):
    # Given
    depositor = household.roles["depositor"]
    deposit_bank = bank.roles["deposit_bank"]

    # When
    depositor.make_deposits(deposit_bank.id, 400)

    # Then
    assert household.account["deposits"] == 400
    assert bank.account["deposits"] == -400
