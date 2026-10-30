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
    model.p.initial_tax_rate = 0.0
    model.p.initial_discount_rate = 0.02
    return model


@pytest.fixture
def country(model):
    # Given
    country = Country(model)
    country.create_markets()
    return country


@pytest.fixture
def market(country):
    # Given
    market = country.spaces["deposit_market"]
    return market


@pytest.fixture
def bank(model, country):
    # Given
    bank = Bank(model)
    bank.country_pos = 0
    country.add_agents([bank])
    return bank


@pytest.fixture
def firm(model, country):
    # Given
    firm = Firm(model)
    firm.country_pos = country.pos
    country.add_agents([firm])
    return firm


@pytest.fixture
def before_firm_withdrawal(firm, bank, country):
    # Given
    country.cash[firm.id].amount = 1000
    depositor = firm.roles["country_0_depositor"]
    deposit_bank = bank.roles["deposit_bank"]
    market = country.spaces["deposit_market"]
    market.join_deposit_bank(depositor, deposit_bank, 500)


@pytest.mark.usefixtures("before_firm_withdrawal")
def test_increases_firm_cash(firm, bank, country):
    # Given
    firm_cash = country.cash[firm.id]
    bank_cash = country.cash[bank.id]
    depositor = firm.roles["country_0_depositor"]
    deposit_bank = bank.roles["deposit_bank"]

    # When
    depositor.withdraw_deposits(deposit_bank.id, 100)

    # Then
    assert firm_cash.amount == 600
    assert bank_cash.amount == 400


@pytest.mark.usefixtures("before_firm_withdrawal")
def test_decreases_firm_deposits(firm, bank):
    # Given
    depositor = firm.roles["country_0_depositor"]
    deposit_bank = bank.roles["deposit_bank"]

    # When
    depositor.withdraw_deposits(deposit_bank.id, 100)

    # Then
    assert firm.account["deposits"] == 400
    assert bank.account["deposits"] == -400


@pytest.fixture
def household(model, country):
    # Given
    household = Household(model)
    household.country_pos = country.pos
    country.add_agents([household])
    return household


@pytest.fixture
def before_household_withdrawal(household, bank, country):
    # Given
    country.cash[household.id].amount = 1000
    depositor = household.roles["depositor"]
    deposit_bank = bank.roles["deposit_bank"]
    market = country.spaces["deposit_market"]
    market.join_deposit_bank(depositor, deposit_bank, 500)


@pytest.mark.usefixtures("before_household_withdrawal")
def test_increases_household_cash(household, bank, country):
    # Given
    household_cash = country.cash[household.id]
    bank_cash = country.cash[bank.id]
    depositor = household.roles["depositor"]
    deposit_bank = bank.roles["deposit_bank"]

    # When
    depositor.withdraw_deposits(deposit_bank.id, 400)

    # Then
    assert household_cash.amount == 900
    assert bank_cash.amount == 100


@pytest.mark.usefixtures("before_household_withdrawal")
def test_decreases_household_deposits(household, bank):
    # Given
    depositor = household.roles["depositor"]
    deposit_bank = bank.roles["deposit_bank"]

    # When
    depositor.withdraw_deposits(deposit_bank.id, 400)

    # Then
    assert household.account["deposits"] == 100
    assert bank.account["deposits"] == -100
