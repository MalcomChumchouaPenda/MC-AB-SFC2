import math
import pytest
from unittest.mock import Mock, PropertyMock
from agentpy import Model
from model.base import EcoAccount
from model.agents.bank import Bank
from model.agents.firm import Firm
from model.spaces.credit_market import CreditMarket


@pytest.fixture
def model():
    # Given
    model = Model()
    model.p.iota_l = 0
    model.p.chi = 0.0
    model.p.mu1 = 1.0
    return model


@pytest.fixture
def bank(model):
    # Given
    bank = Bank(model)
    bank.setup()
    bank.roles["company"] = Mock()
    bank.account = EcoAccount(model)
    bank.account.setup()
    bank.cb_account = EcoAccount(model)
    bank.cb_account.setup()
    return bank


@pytest.fixture
def firm(model):
    # Given
    firm = Firm(model)
    firm.setup()
    firm.roles["depositor"] = Mock()
    firm.account = EcoAccount(model)
    firm.account.setup()
    firm.cb_account = EcoAccount(model)
    firm.cb_account.setup()
    firm.bank_account = EcoAccount(model)
    firm.bank_account.setup()
    return firm


@pytest.fixture
def market(model, firm, bank):
    # Given
    market = CreditMarket(model)
    market.setup()
    market.add_lender(bank)
    market.add_borrower(firm)
    return market


@pytest.mark.usefixtures("market")
def test_firm_request_loans(firm, bank):
    # Given
    firm.wage_offer = 4
    firm.desired_rd = 100
    firm.desired_labor = 100
    lender = bank.roles["lender"]
    borrower = firm.roles["borrower"]

    # When
    firm.request_loans()

    # Then
    assert firm.desired_loans == 500
    assert borrower.loan_demand == 500
    assert lender.loan_applicants == [borrower]


def test_bank_grant_loans(market, firm, bank):
    # Given
    bank.account.stocks["equities"] = 100
    bank.roles["company"].get_discount_rate.return_value = 0.05
    borrower, lender = firm.roles["borrower"], bank.roles["lender"]
    borrower.loan_demand = 50
    borrower.net_worth = 100
    lender.loan_applicants = [borrower]

    # When
    bank.grant_loans()

    # Then
    assert bank.account.stocks["loans"] == 50
    assert bank.account.stocks["cash"] == -50
    assert firm.account.stocks["loans"] == -50
    assert firm.account.stocks["deposits"] == 50
    assert firm.bank_account.stocks["deposits"] == -50
    assert firm.bank_account.stocks["cash"] == 50
    assert market.graph[lender][borrower]["amount"] == 50
    assert market.graph[lender][borrower]["rate"] == 0.05


def test_firm_repays_loans(market, firm, bank):
    # Given
    bank.account.stocks["loans"] = 50
    firm.account.stocks["loans"] = -50
    firm.account.stocks["deposits"] = 55
    firm.bank_account.stocks["deposits"] = -55
    borrower, lender = firm.roles["borrower"], bank.roles["lender"]
    market.graph.add_edge(lender, borrower, amount=50, rate=0.1)

    # When
    firm.repay_loans()

    # Then
    assert bank.account.stocks["loans"] == 0
    assert bank.account.stocks["cash"] == 55
    assert bank.account.flows["loan_interests"] == 5
    assert firm.account.stocks["loans"] == 0
    assert firm.account.stocks["deposits"] == 0
    assert firm.account.flows["loan_interests"] == -5
    assert firm.bank_account.stocks["deposits"] == 0
    assert firm.bank_account.stocks["cash"] == -55
    assert market.graph[lender][borrower]["amount"] == 0
