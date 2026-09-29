from unittest.mock import Mock
import pytest
from agentpy import Model
from model.agents.bank import Bank
from model.agents.firm import Firm
from model.agents.government import Government
from model.spaces.deposit_market import DepositMarket


@pytest.fixture
def model():
    # Given
    model = Model()
    model.p.zeta = 0.8
    return model


@pytest.fixture
def bank(model):
    # Given
    bank = Bank(model)
    return bank


@pytest.fixture
def firm(model):
    # Given
    firm = Firm(model)
    return firm


@pytest.fixture
def market(model):
    # Given
    market = DepositMarket(model)
    return market


@pytest.fixture
def before_transactions(market, firm, bank):
    # Given
    deposit_demander = market.add_demander(bank)
    deposit_supplier = market.add_supplier(firm)
    market.join_bank(deposit_supplier, deposit_demander, 2000)


@pytest.mark.usefixtures("before_transactions")
def test_bank_pays_deposit_interest_to_firm(firm, bank):
    # Given
    bank.deposit_rate = 0.02

    # When
    bank.pay_deposit_interests()

    # Then
    assert firm.account["deposits"] == 2040
    assert bank.account["deposits"] == -2040
    assert firm.account["dep_interests"] == 40
    assert bank.account["dep_interests"] == -40


@pytest.fixture
def govt(model):
    # Given
    govt = Government(model)
    return govt


@pytest.fixture
def before_reimbursement(market, firm, bank, govt):
    # Given
    deposit_demander = market.add_demander(bank)
    deposit_supplier = market.add_supplier(firm)
    market.add_guarantee(govt)
    market.join_bank(deposit_supplier, deposit_demander, 2000)


@pytest.mark.usefixtures("before_reimbursement")
def test_government_reimburse_deposits(govt, firm, bank):
    # Given
    firm.account["cash"] = 0
    bank.account["cash"] = 0
    bank.roles["deposit_demander"].defaulted = True
    govt.roles["bond_issuer"] = Mock()

    # When
    govt.issue_deposit_guarantee_bonds()
    govt.reimburse_deposits()

    # Then
    assert govt.roles["bond_issuer"].bond_value == 20
    assert govt.roles["bond_issuer"].bond_number == 100
    assert govt.account["cash"] == -2000
    assert firm.account["deposits"] == 0
    assert firm.account["cash"] == 2000
    assert bank.account["deposits"] == 0
    assert bank.account["cash"] == 0
