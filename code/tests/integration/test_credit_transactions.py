from unittest.mock import Mock
import pytest
from agentpy import Model
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
def banks(model):
    # Given
    banks = []
    for _ in range(2):
        bank = Bank(model)
        bank.roles["company"] = Mock()
        banks.append(bank)
    return banks


@pytest.fixture
def firm(model):
    # Given
    firm = Firm(model)
    firm.setup()
    firm.roles["depositor"] = Mock()
    return firm


@pytest.fixture
def market(model):
    # Given
    market = CreditMarket(model)
    return market


@pytest.fixture
def before_transactions(market, firm, banks):
    # Given
    market.add_lender(banks[0])
    market.add_borrower(firm)
    market.add_account(firm)
    market.add_account(banks[0])
    market.add_account(banks[1])
    firm.bank_id = banks[1].id
    return market


@pytest.mark.usefixtures("before_transactions")
def test_firm_request_loans(firm, banks):
    # Given
    firm.wage_offer = 4
    firm.desired_rd = 100
    firm.desired_labor = 100
    lender = banks[0].roles["lender"]
    borrower = firm.roles["borrower"]

    # When
    firm.request_loans()

    # Then
    assert firm.desired_loans == 500
    assert borrower.loan_demand == 500
    assert lender.loan_applicants == [borrower]


@pytest.mark.usefixtures("before_transactions")
def test_bank_grant_loans(market, firm, banks):
    # Given
    banks[0].account.stocks["equities"] = 100
    banks[0].roles["company"].get_discount_rate.return_value = 0.05
    borrower = firm.roles["borrower"]
    borrower.loan_demand = 50
    borrower.net_worth = 100
    lender = banks[0].roles["lender"]
    lender.loan_applicants = [borrower]

    # When
    banks[0].grant_loans()

    # Then
    assert banks[0].account.stocks["loans"] == 50
    assert banks[0].account.stocks["cash"] == -50
    assert firm.account.stocks["loans"] == -50
    assert firm.account.stocks["deposits"] == 50
    assert banks[1].account.stocks["deposits"] == -50
    assert banks[1].account.stocks["cash"] == 50
    assert market.graph[lender][borrower]["amount"] == 50
    assert market.graph[lender][borrower]["rate"] == 0.05


@pytest.mark.usefixtures("before_transactions")
def test_firm_repays_loans(market, firm, banks):
    # Given
    firm.account.stocks["loans"] = -50
    firm.account.stocks["deposits"] = 55
    banks[0].account.stocks["loans"] = 50
    banks[1].account.stocks["deposits"] = -55
    borrower, lender = firm.roles["borrower"], banks[0].roles["lender"]
    market.graph.add_edge(lender, borrower, amount=50, rate=0.1)

    # When
    firm.repay_loans()

    # Then
    assert banks[0].account.stocks["loans"] == 0
    assert banks[0].account.stocks["cash"] == 55
    assert banks[0].account.flows["loan_interests"] == 5
    assert firm.account.stocks["loans"] == 0
    assert firm.account.stocks["deposits"] == 0
    assert firm.account.flows["loan_interests"] == -5
    assert banks[1].account.stocks["deposits"] == 0
    assert banks[1].account.stocks["cash"] == -55
    assert market.graph[lender][borrower]["amount"] == 0
