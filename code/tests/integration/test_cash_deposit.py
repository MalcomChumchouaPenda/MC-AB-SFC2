import pytest
from model.agents.bank import Bank
from model.agents.firm import Firm
from model.agents.household import Household
from model.spaces.deposit_market import DepositMarket


@pytest.fixture
def model(fake_model):
    # Given
    model = fake_model
    model.p.initial_wage = 0.0
    return model


@pytest.fixture
def market(model):
    # Given
    market = DepositMarket(model)
    return market


@pytest.fixture
def bank(model, market):
    # Given
    bank = Bank(model)
    market.add_bank(bank)
    return bank


@pytest.fixture
def firm(model, market):
    # Given
    firm = Firm(model)
    market.add_firm(firm)
    return firm


def test_decreases_firm_cash(firm, bank, market):
    # Given
    firm.account["cash"] = 1000
    depositor = firm.roles["country_0_depositor"]
    deposit_bank = bank.roles["deposit_bank"]
    market.join_deposit_bank(depositor, deposit_bank)

    # When
    depositor.make_deposits(deposit_bank.id, 200)

    # Then
    assert firm.account["cash"] == 800
    assert bank.account["cash"] == 200


def test_increases_firm_deposits(firm, bank, market):
    # Given
    firm.account["cash"] = 1000
    depositor = firm.roles["country_0_depositor"]
    deposit_bank = bank.roles["deposit_bank"]
    market.join_deposit_bank(depositor, deposit_bank)

    # When
    depositor.make_deposits(deposit_bank.id, 200)

    # Then
    assert firm.account["deposits"] == 200
    assert bank.account["deposits"] == -200


@pytest.fixture
def household(model, market):
    # Given
    household = Household(model)
    market.add_household(household)
    return household


def test_decreases_household_cash(household, bank, market):
    # Given
    household.account["cash"] = 1000
    depositor = household.roles["depositor"]
    deposit_bank = bank.roles["deposit_bank"]
    market.join_deposit_bank(depositor, deposit_bank)

    # When
    depositor.make_deposits(deposit_bank.id, 400)

    # Then
    assert household.account["cash"] == 600
    assert bank.account["cash"] == 400


def test_increases_household_deposits(household, bank, market):
    # Given
    household.account["cash"] = 1000
    depositor = household.roles["depositor"]
    deposit_bank = bank.roles["deposit_bank"]
    market.join_deposit_bank(depositor, deposit_bank)

    # When
    depositor.make_deposits(deposit_bank.id, 400)

    # Then
    assert household.account["deposits"] == 400
    assert bank.account["deposits"] == -400
