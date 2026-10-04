import pytest
from model.agents.bank import Bank
from model.agents.firm import Firm
from model.agents.household import Household
from model.agents.government import Government
from model.spaces.monetary_union import MonetaryUnion


@pytest.fixture
def union(fake_model):
    # Given
    union = MonetaryUnion(fake_model)
    union.create_markets()
    union.create_countries(1)
    return union


@pytest.fixture
def deposit_market(union):
    # Given
    country = union.spaces["country_0"]
    return country.spaces["deposit_market"]


@pytest.fixture
def govt(fake_model, union):
    # Given
    govt = Government(fake_model)
    union.add_government(govt)
    return govt


@pytest.fixture
def bank(fake_model, union):
    # Given
    bank = Bank(fake_model)
    union.add_bank(bank)
    deposit_bank = bank.roles["deposit_bank"]
    deposit_bank.defaulted = True
    return bank


@pytest.fixture
def firm(fake_model, union):
    # Given
    firm = Firm(fake_model)
    union.add_firm(firm)
    return firm


def test_issues_bonds_for_reimbursement(firm, bank, govt, deposit_market):
    # Given
    firm.account["cash"] = 1000
    depositor = firm.roles["depositor_0"]
    deposit_bank = bank.roles["deposit_bank"]
    deposit_market.join_deposit_bank(depositor, deposit_bank, 500)

    # When
    govt.issue_deposit_guarantee_bonds()
    govt.reimburse_deposits()

    # Then
    assert govt.roles["bond_issuer"].bond_value == 5
    assert govt.roles["bond_issuer"].bond_number == 100


def test_increases_firm_cash(firm, bank, govt, deposit_market):
    # Given
    firm.account["cash"] = 1000
    depositor = firm.roles["depositor_0"]
    deposit_bank = bank.roles["deposit_bank"]
    deposit_market.join_deposit_bank(depositor, deposit_bank, 500)

    # When
    govt.issue_deposit_guarantee_bonds()
    govt.reimburse_deposits()

    # Then
    assert govt.account["cash"] == -500
    assert firm.account["cash"] == 1000


def test_clears_firm_deposits(firm, bank, govt, deposit_market):
    # Given
    firm.account["cash"] = 1000
    depositor = firm.roles["depositor_0"]
    deposit_bank = bank.roles["deposit_bank"]
    deposit_market.join_deposit_bank(depositor, deposit_bank, 500)

    # When
    govt.issue_deposit_guarantee_bonds()
    govt.reimburse_deposits()

    # Then
    assert firm.account["deposits"] == 0
    assert bank.account["deposits"] == 0


@pytest.fixture
def household(fake_model, union):
    # Given
    model = fake_model
    household = Household(model)
    union.add_household(household)
    return household


def test_increases_household_cash(household, bank, govt, deposit_market):
    # Given
    household.account["cash"] = 1000
    depositor = household.roles["depositor"]
    deposit_bank = bank.roles["deposit_bank"]
    deposit_market.join_deposit_bank(depositor, deposit_bank, 500)

    # When
    govt.issue_deposit_guarantee_bonds()
    govt.reimburse_deposits()

    # Then
    assert household.account["cash"] == 1000
    assert govt.account["cash"] == -500


def test_clears_household_deposits(household, bank, govt, deposit_market):
    # Given
    household.account["cash"] = 1000
    depositor = household.roles["depositor"]
    deposit_bank = bank.roles["deposit_bank"]
    deposit_market.join_deposit_bank(depositor, deposit_bank, 500)

    # When
    govt.issue_deposit_guarantee_bonds()
    govt.reimburse_deposits()

    # Then
    assert household.account["deposits"] == 0
    assert bank.account["deposits"] == 0
