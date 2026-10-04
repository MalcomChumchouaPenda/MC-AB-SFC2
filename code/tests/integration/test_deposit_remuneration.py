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


def test_increases_firm_deposits(firm, bank, market):
    # Given
    bank.deposit_rate = 0.02
    depositor = firm.roles["depositor_0"]
    deposit_bank = bank.roles["deposit_bank"]
    market.join_deposit_bank(depositor, deposit_bank, 2000)

    # When
    bank.pay_deposit_interests()

    # Then
    assert firm.account["deposits"] == 2040
    assert bank.account["deposits"] == -2040


def test_increases_firm_deposit_interests(firm, bank, market):
    # Given
    bank.deposit_rate = 0.02
    depositor = firm.roles["depositor_0"]
    deposit_bank = bank.roles["deposit_bank"]
    market.join_deposit_bank(depositor, deposit_bank, 2000)

    # When
    bank.pay_deposit_interests()

    # Then
    assert firm.account["dep_interests"] == 40
    assert bank.account["dep_interests"] == -40


@pytest.fixture
def household(fake_model, market):
    # Given
    model = fake_model
    household = Household(model)
    market.place_household(household)
    return household


def test_increases_household_deposits(household, bank, market):
    # Given
    bank.deposit_rate = 0.02
    depositor = household.roles["depositor"]
    deposit_bank = bank.roles["deposit_bank"]
    market.join_deposit_bank(depositor, deposit_bank, 1000)

    # When
    bank.pay_deposit_interests()

    # Then
    assert household.account["deposits"] == 1020
    assert bank.account["deposits"] == -1020


def test_increases_household_deposit_interests(household, bank, market):
    # Given
    bank.deposit_rate = 0.02
    depositor = household.roles["depositor"]
    deposit_bank = bank.roles["deposit_bank"]
    market.join_deposit_bank(depositor, deposit_bank, 1000)

    # When
    bank.pay_deposit_interests()

    # Then
    assert household.account["dep_interests"] == 20
    assert bank.account["dep_interests"] == -20
