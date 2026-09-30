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
def firm(fake_model, market, bank):
    # Given
    model = fake_model
    firm = Firm(model)
    depositor = market.add_depositor(firm)
    deposit_bank = bank.roles["deposit_bank"]
    market.join_deposit_bank(depositor, deposit_bank)
    return firm


def test_decreases_firm_cash(firm, bank):
    # Given
    firm.account["cash"] = 1000
    depositor = firm.roles["depositor"]

    # When
    depositor.make_deposits(200)

    # Then
    assert firm.account["cash"] == 800
    assert bank.account["cash"] == 200


def test_increases_firm_deposits(firm, bank):
    # Given
    firm.account["cash"] = 1000
    depositor = firm.roles["depositor"]

    # When
    depositor.make_deposits(200)

    # Then
    assert firm.account["deposits"] == 200
    assert bank.account["deposits"] == -200


@pytest.fixture
def household(fake_model, market, bank):
    # Given
    model = fake_model
    household = Household(model)
    deposit_bank = bank.roles["deposit_bank"]
    depositor = market.add_depositor(household)
    market.join_deposit_bank(depositor, deposit_bank)
    return household


def test_decreases_household_cash(household, bank):
    # Given
    household.account["cash"] = 1000
    depositor = household.roles["depositor"]

    # When
    depositor.make_deposits(400)

    # Then
    assert household.account["cash"] == 600
    assert bank.account["cash"] == 400


def test_increases_household_deposits(household, bank):
    # Given
    household.account["cash"] = 1000
    depositor = household.roles["depositor"]

    # When
    depositor.make_deposits(400)

    # Then
    assert household.account["deposits"] == 400
    assert bank.account["deposits"] == -400
