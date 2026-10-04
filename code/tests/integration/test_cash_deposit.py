import pytest
from model.agents.bank import Bank
from model.agents.firm import Firm
from model.agents.household import Household
from model.spaces.deposit_market import DepositMarket


@pytest.fixture
def market(fake_model):
    # Given
    model = fake_model
    market = DepositMarket(model)
    return market


@pytest.fixture
def bank(fake_model, market):
    # Given
    model = fake_model
    bank = Bank(model)
    market.place_bank(bank)
    return bank


@pytest.fixture
def firm(fake_model, market):
    # Given
    model = fake_model
    firm = Firm(model)
    market.place_firm(firm)
    return firm


def test_decreases_firm_cash(firm, bank, market):
    # Given
    firm.account["cash"] = 1000
    depositor = firm.roles["depositor_0"]
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
    depositor = firm.roles["depositor_0"]
    deposit_bank = bank.roles["deposit_bank"]
    market.join_deposit_bank(depositor, deposit_bank)

    # When
    depositor.make_deposits(deposit_bank.id, 200)

    # Then
    assert firm.account["deposits"] == 200
    assert bank.account["deposits"] == -200


@pytest.fixture
def household(fake_model, market):
    # Given
    model = fake_model
    household = Household(model)
    market.place_household(household)
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
