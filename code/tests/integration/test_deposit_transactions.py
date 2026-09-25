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
    deposit_bank = market.add_deposit_bank(bank)
    depositor = market.add_depositor(firm)
    market.join_deposit_bank(depositor, deposit_bank, 2000)


@pytest.mark.usefixtures("before_transactions")
def test_bank_pays_deposit_interest_to_firm(firm, bank):
    # Given
    bank.deposit_rate = 0.02

    # When
    bank.pay_deposit_interests()

    # Then
    assert firm.account.stocks["deposits"] == 2040
    assert bank.account.stocks["deposits"] == -2040
    assert firm.account.flows["dep_interests"] == 40
    assert bank.account.flows["dep_interests"] == -40


@pytest.fixture
def govt(model):
    # Given
    govt = Government(model)
    return govt


@pytest.fixture
def before_reimbursement(market, firm, bank, govt):
    # Given
    deposit_bank = market.add_deposit_bank(bank)
    depositor = market.add_depositor(firm)
    market.add_deposit_guarantee(govt)
    market.join_deposit_bank(depositor, deposit_bank, 2000)


@pytest.mark.usefixtures("before_reimbursement")
def test_government_reimburse_deposits(govt, firm, bank):
    # Given
    firm.account.stocks["cash"] = 0
    bank.account.stocks["cash"] = 0
    bank.roles["deposit_bank"].defaulted = True
    govt.roles["bond_issuer"] = Mock()

    # When
    govt.issue_deposit_guarantee_bonds()
    govt.reimburse_deposits()

    # Then
    assert govt.roles["bond_issuer"].bond_value == 20
    assert govt.roles["bond_issuer"].bond_number == 100
    assert govt.account.stocks["cash"] == -2000
    assert firm.account.stocks["deposits"] == 0
    assert firm.account.stocks["cash"] == 2000
    assert bank.account.stocks["deposits"] == 0
    assert bank.account.stocks["cash"] == 0
