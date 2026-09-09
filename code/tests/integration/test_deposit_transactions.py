import pytest
from unittest.mock import Mock
from model.base import EcoAccount
from model.agents.bank import Bank
from model.agents.firm import Firm
from model.agents.government import Government
from model.spaces.deposit_market import DepositMarket


@pytest.fixture
def model():
    # Given
    model = Mock()
    model.p.zeta = 0.8
    return model


@pytest.fixture
def bank(model):
    # Given
    bank = Bank(model)
    bank.setup()
    bank.account = EcoAccount(model)
    bank.account.setup()
    return bank


@pytest.fixture
def firm(model):
    # Given
    firm = Firm(model)
    firm.setup()
    firm.account = EcoAccount(model)
    firm.account.setup()
    return firm


@pytest.fixture
def market_with_participants(model, firm, bank):
    # Given
    market = DepositMarket(model)
    market.setup()
    deposit_bank = market.add_deposit_bank(bank)
    depositor = market.add_depositor(firm)
    market.link_depositor_to_bank(depositor, deposit_bank, 2000)
    return market, firm, bank


@pytest.mark.usefixtures("market_with_participants")
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
    govt.setup()
    govt.account = EcoAccount(model)
    govt.account.setup()
    return govt


@pytest.fixture
def market_with_guarantee(model, firm, bank, govt):
    # Given
    market = DepositMarket(model)
    market.setup()
    deposit_bank = market.add_deposit_bank(bank)
    depositor = market.add_depositor(firm)
    market.link_depositor_to_bank(depositor, deposit_bank, 2000)
    market.add_deposit_guarantee(govt)
    return market, firm, bank


@pytest.mark.usefixtures("market_with_guarantee")
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
