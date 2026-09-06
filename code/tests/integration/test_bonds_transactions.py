import pytest
from unittest.mock import Mock
from model.base import EcoAccount
from model.agents.bank import Bank
from model.agents.central_bank import CentralBank
from model.agents.government import Government
from model.spaces.bond_market import BondMarket


@pytest.fixture
def model():
    # Given
    model = Mock()
    model.p.iota_b = 0
    return model


@pytest.fixture
def cb(model):
    # Given
    cb = CentralBank(model)
    cb.setup()
    cb.discount_rate = 0.04
    cb.account = EcoAccount(model)
    cb.account.setup()
    # cb.account.stocks["cash"] = 1000
    return cb


@pytest.fixture
def govt(model, cb):
    # Given
    govt = Government(model)
    govt.setup()
    govt.roles["fiscal_authority"] = Mock()
    govt.account = EcoAccount(model)
    govt.account.setup()
    govt.cb_account = cb.account
    return govt


@pytest.fixture
def bank(model, cb):
    # Given
    bank = Bank(model)
    bank.setup()
    bank.account = EcoAccount(model)
    bank.account.setup()
    bank.cb_account = cb.account
    return bank


@pytest.fixture
def market(model, govt, bank, cb):
    # Given
    market = BondMarket(model)
    market.setup()
    market.add_issuer(govt)
    market.add_buyer(bank)
    market.add_buyer(cb)
    return market


@pytest.mark.usefixtures("market")
def test_government_issues_bonds(govt):
    # Given
    govt.budget_deficit = 200
    govt.prev_budget_surplus = 50
    govt.roles["fiscal_authority"].get_gdp.return_value = 1000

    # When
    govt.issue_bonds()

    # Then
    assert govt.roles["bond_issuer"].bond_value == 1.5
    assert govt.roles["bond_issuer"].bond_number == 100
    assert govt.roles["bond_issuer"].debt_ratio == 0.15


def test_government_update_bond_rate(govt):
    # Given
    govt.roles["fiscal_authority"].get_gdp.return_value = 1000
    govt.roles["fiscal_authority"].get_discount_rate.return_value = 0.04
    govt.account.stocks["bonds"] = 100
    govt.p.chi = 0.02

    # When
    govt.update_bond_rate()

    # Then
    assert govt.bond_rate == 0.042


def test_government_repay_bonds_to_bank(market, govt, bank):
    # Given
    bank.account.stocks["bonds"] = 100
    govt.account.stocks["bonds"] = -100
    govt.bond_rate = 0.042
    issuer_role = govt.roles["bond_issuer"]
    buyer_role = bank.roles["bond_buyer"]
    market.graph.add_edge(issuer_role, buyer_role, amount=100)

    # When
    govt.repay_bonds()

    # Then
    assert govt.account.stocks["bonds"] == 0
    assert govt.account.stocks["cash"] == -104.2
    assert govt.account.flows["bond_interests"] == -4.2
    assert bank.account.stocks["cash"] == 104.2
    assert bank.account.stocks["bonds"] == 0
    assert bank.account.flows["bond_interests"] == 4.2
    assert market.graph[issuer_role][buyer_role]["amount"] == 0


def test_government_repay_bonds_to_central_bank(market, govt, cb):
    # Given
    cb.account.stocks["bonds"] = 100
    govt.account.stocks["bonds"] = -100
    govt.bond_rate = 0.042
    issuer_role = govt.roles["bond_issuer"]
    buyer_role = cb.roles["bond_buyer"]
    market.graph.add_edge(issuer_role, buyer_role, amount=100)

    # When
    govt.repay_bonds()

    # Then
    assert govt.account.stocks["bonds"] == 0
    assert govt.account.stocks["cash"] == -104.2
    assert govt.account.flows["bond_interests"] == -4.2
    assert cb.account.stocks["cash"] == 104.2
    assert cb.account.stocks["bonds"] == 0
    assert cb.account.flows["bond_interests"] == 4.2
    assert market.graph[issuer_role][buyer_role]["amount"] == 0


def test_bank_buy_bonds(market, govt, bank):
    # Given
    govt.p.mu2 = 0.1
    govt.p.iota_b = 0
    bank.account.stocks["cash"] = 150
    bank.account.stocks["deposits"] = 1000
    buyer_role = bank.roles["bond_buyer"]
    issuer_role = govt.roles["bond_issuer"]
    issuer_role.bond_value = 5.0
    issuer_role.bond_number = 100

    # When
    bank.buy_bonds()

    # Then
    assert issuer_role.bond_number == 90
    assert govt.account.stocks["cash"] == 50
    assert govt.account.stocks["bonds"] == -50
    assert bank.account.stocks["cash"] == 100
    assert bank.account.stocks["bonds"] == 50
    assert market.graph[issuer_role][buyer_role]["amount"] == 50


def test_central_bank_buy_remaining_bonds(market, govt, cb):
    # Given
    govt.country = cb.country = 1
    buyer_role = cb.roles["bond_buyer"]
    issuer_role = govt.roles["bond_issuer"]
    issuer_role.bond_value = 5.0
    issuer_role.bond_number = 100

    # When
    cb.buy_remaining_bonds()

    # Then
    assert issuer_role.bond_number == 0
    assert govt.account.stocks["cash"] == 500
    assert govt.account.stocks["bonds"] == -500
    assert cb.account.stocks["cash"] == -500
    assert cb.account.stocks["bonds"] == 500
    assert market.graph[issuer_role][buyer_role]["amount"] == 500