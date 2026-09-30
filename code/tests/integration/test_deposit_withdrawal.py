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
    market.add_deposit_bank(bank)
    return bank


@pytest.fixture
def firm(fake_model, market):
    # Given
    model = fake_model
    firm = Firm(model)
    market.add_depositor(firm)
    return firm


def test_increases_firm_cash(firm, bank, market):
    # Given
    firm.account["cash"] = 1000
    depositor = firm.roles["depositor"]
    deposit_bank = bank.roles["deposit_bank"]
    market.join_deposit_bank(depositor, deposit_bank, 500)

    # When
    depositor.withdraw_deposits(deposit_bank, 100)

    # Then
    assert firm.account["cash"] == 600
    assert bank.account["cash"] == 400


def test_decreases_firm_deposits(firm, bank, market):
    # Given
    firm.account["cash"] = 1000
    depositor = firm.roles["depositor"]
    deposit_bank = bank.roles["deposit_bank"]
    market.join_deposit_bank(depositor, deposit_bank, 500)

    # When
    depositor.withdraw_deposits(deposit_bank, 100)

    # Then
    assert firm.account["deposits"] == 400
    assert bank.account["deposits"] == -400


@pytest.fixture
def household(fake_model, market):
    # Given
    model = fake_model
    household = Household(model)
    market.add_depositor(household)
    return household


def test_increases_household_cash(household, bank, market):
    # Given
    household.account["cash"] = 1000
    depositor = household.roles["depositor"]
    deposit_bank = bank.roles["deposit_bank"]
    market.join_deposit_bank(depositor, deposit_bank, 500)

    # When
    depositor.withdraw_deposits(deposit_bank, 400)

    # Then
    assert household.account["cash"] == 900
    assert bank.account["cash"] == 100


def test_decreases_household_deposits(household, bank, market):
    # Given
    household.account["cash"] = 1000
    depositor = household.roles["depositor"]
    deposit_bank = bank.roles["deposit_bank"]
    market.join_deposit_bank(depositor, deposit_bank, 500)

    # When
    depositor.withdraw_deposits(deposit_bank, 400)

    # Then
    assert household.account["deposits"] == 100
    assert bank.account["deposits"] == -100
