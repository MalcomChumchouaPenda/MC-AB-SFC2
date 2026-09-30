import pytest
from model.agents.bank import Bank
from model.agents.firm import Firm
from model.agents.household import Household
from model.agents.government import Government
from model.spaces.monetary_union import MonetaryUnion


@pytest.fixture
def union(fake_model):
    # Given
    model = fake_model
    model.p.K = 1
    union = MonetaryUnion(model)
    return union


@pytest.fixture
def bond_market(union):
    # Given
    return union.spaces["bond_market"]


@pytest.fixture
def deposit_market(union):
    # Given
    country = union.spaces["country_0"]
    return country.spaces["deposit_market"]


@pytest.fixture
def govt(fake_model, bond_market, deposit_market):
    # Given
    model = fake_model
    govt = Government(model)
    bond_market.add_issuer(govt)
    deposit_market.add_guarantee(govt)
    return govt


@pytest.fixture
def bank(fake_model, deposit_market):
    # Given
    model = fake_model
    bank = Bank(model)
    deposit_bank = deposit_market.add_deposit_bank(bank)
    deposit_bank.defaulted = True
    return bank


@pytest.fixture
def firm(fake_model, deposit_market):
    # Given
    model = fake_model
    firm = Firm(model)
    deposit_market.add_depositor(firm)
    return firm


def test_issues_bonds_for_reimbursement(firm, bank, govt, deposit_market):
    # Given
    firm.account["cash"] = 1000
    depositor = firm.roles["depositor"]
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
    depositor = firm.roles["depositor"]
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
    depositor = firm.roles["depositor"]
    deposit_bank = bank.roles["deposit_bank"]
    deposit_market.join_deposit_bank(depositor, deposit_bank, 500)

    # When
    govt.issue_deposit_guarantee_bonds()
    govt.reimburse_deposits()

    # Then
    assert firm.account["deposits"] == 0
    assert bank.account["deposits"] == 0


@pytest.fixture
def household(fake_model, deposit_market):
    # Given
    model = fake_model
    household = Household(model)
    deposit_market.add_depositor(household)
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
