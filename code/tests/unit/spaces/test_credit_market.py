import pytest
from unittest.mock import Mock
from agentpy import AgentDList
from model.spaces.credit_market import CreditMarket

# ---------------------------------------------------
# ARCHITECTURE TESTS
# ----------------------------------------------------


def test_is_eco_space():
    # Given
    from model.base import EcoSpace

    # Assert
    assert issubclass(CreditMarket, EcoSpace)


@pytest.fixture
def market_before_setup():
    # Given
    model = Mock()
    market = CreditMarket(model)
    return market


def test_has_monetary_union_ref(market_before_setup):
    # Given
    market = market_before_setup

    # When
    market.setup()

    # Then
    assert market.monetary_union is None


def test_expose_discount_rate(market_before_setup):
    # Given
    market = market_before_setup

    # When
    market.monetary_union = Mock(discount_rate=0.05)

    # Then
    assert market.discount_rate == 0.05


# ---------------------------------------------------
# ROLES
# ----------------------------------------------------


def test_has_lenders_list(market_before_setup):
    # Given
    market = market_before_setup

    # When
    market.setup()

    # Then
    assert isinstance(market.lenders, AgentDList)


def test_has_borrowers_list(market_before_setup):
    # Given
    market = market_before_setup

    # When
    market.setup()

    # Then
    assert isinstance(market.borrowers, AgentDList)


class FakeLender(Mock):
    pass


@pytest.fixture
def market_without_lenders(monkeypatch, market_before_setup):
    # Given
    monkeypatch.setattr("model.spaces.credit_market.Lender", FakeLender)
    market = market_before_setup
    market.add_role = Mock()
    market.lenders = []
    return market


def test_add_lender_add_appropriate_role(market_without_lenders):
    # Given
    agent = Mock()
    market = market_without_lenders

    # When
    role = market.add_lender(agent)

    # Then
    market.add_role.assert_called_with(FakeLender, agent, "lender")
    assert role == market.add_role.return_value


def test_add_lender_registers_lender(market_without_lenders):
    # Given
    agent = Mock()
    market = market_without_lenders

    # When
    role = market.add_lender(agent)

    # Then
    assert market.lenders == [role]


class FakeBorrower(Mock):
    pass


@pytest.fixture
def market_without_borrowers(monkeypatch, market_before_setup):
    # Given
    monkeypatch.setattr("model.spaces.credit_market.Borrower", FakeBorrower)
    market = market_before_setup
    market.add_role = Mock()
    market.borrowers = []
    return market


def test_add_borrower_add_appropriate_role(market_without_borrowers):
    # Given
    agent = Mock()
    market = market_without_borrowers

    # When
    role = market.add_borrower(agent)

    # Then
    market.add_role.assert_called_with(FakeBorrower, agent, "borrower")
    assert role == market.add_role.return_value


def test_add_borrower_registers_borrower(market_without_borrowers):
    # Given
    agent = Mock()
    market = market_without_borrowers

    # When
    role = market.add_borrower(agent)

    # Then
    assert market.borrowers == [role]


# ---------------------------------------------------
# CREDIT MATCHING
# ----------------------------------------------------


def test_find_lenders(market_before_setup, make_dlist):
    # Given
    lender = Mock()
    market = market_before_setup
    market.lenders = make_dlist([lender])

    # When
    sample = market.find_lenders()

    # Then
    assert sample == [lender]


@pytest.fixture
def market_with_participants(market_before_setup):
    # Given
    lender = Mock()
    borrower = Mock(loan_demand=0)
    market = market_before_setup
    market.graph.add_nodes_from([borrower, lender])
    return market, borrower, lender


def test_grant_loan_creates_graph_edge(market_with_participants):
    # Given
    market, borrower, lender = market_with_participants
    graph = market.graph

    # When
    market.grant_loan(lender, borrower, 500, 0.05)

    # Then
    assert graph.has_edge(borrower, lender)
    assert graph[borrower][lender]["amount"] == 500
    assert graph[borrower][lender]["rate"] == 0.05


def test_grant_loan_updates_accounts(market_with_participants):
    # Given
    market, borrower, lender = market_with_participants

    # When
    market.grant_loan(lender, borrower, 500, 0.05)

    # Then
    borrower.account.debit_stock.assert_any_call("loans", 500)
    borrower.account.credit_stock.assert_any_call("deposits", 500)
    borrower.bank_account.debit_stock.assert_any_call("deposits", 500)
    borrower.bank_account.credit_stock.assert_any_call("cash", 500)
    lender.account.debit_stock.assert_any_call("cash", 500)
    lender.account.credit_stock.assert_any_call("loans", 500)


def test_grant_loan_reduces_loan_demand(market_with_participants):
    # Given
    market, borrower, lender = market_with_participants
    borrower.loan_demand = 900

    # When
    market.grant_loan(lender, borrower, 500, 0.05)

    # Then
    assert borrower.loan_demand == 400


# ---------------------------------------------------
# LOAN REPAYMENT
# ----------------------------------------------------


def test_find_loans(market_with_participants):
    # Given
    other = Mock()
    market, borrower, lender = market_with_participants
    market.graph.add_edge(lender, borrower, amount=100, rate=0.01)
    market.graph.add_edge(lender, other, amount=200, rate=0.05)

    # When
    loans = market.find_loans(borrower)

    # Then
    assert loans == [{"lender": lender, "amount": 100, "rate": 0.01}]


@pytest.fixture
def market_with_loan(market_with_participants):
    # Given
    market, borrower, lender = market_with_participants
    market.graph.add_edge(borrower, lender, amount=100, rate=0.1)
    return market, borrower, lender


def test_repay_loan_updates_graph_edge(market_with_loan):
    # Given
    market, borrower, lender = market_with_loan
    graph = market.graph
    graph[borrower][lender]["amount"] = 300

    # When
    market.repay_loan(borrower, lender, 100, 10)

    # Then
    assert graph[borrower][lender]["amount"] == 200


def test_repay_loan_updates_accounts(market_with_loan):
    # Given
    market, borrower, lender = market_with_loan

    # When
    market.repay_loan(borrower, lender, 100, 10)

    # Then
    borrower.account.credit_stock.assert_any_call("loans", 100)
    borrower.account.debit_flow.assert_any_call("loan_interests", 10)
    borrower.account.debit_stock.assert_any_call("deposits", 110)
    borrower.bank_account.credit_stock.assert_any_call("deposits", 110)
    borrower.bank_account.debit_stock.assert_any_call("cash", 110)
    lender.account.credit_stock.assert_any_call("cash", 110)
    lender.account.debit_stock.assert_any_call("loans", 100)
    lender.account.credit_flow.assert_any_call("loans_interests", 10)


# ---------------------------------------------------
# CASH ADVANCE REQUEST / REPAYMENT
# ----------------------------------------------------


@pytest.fixture
def market_with_union(market_before_setup):
    # Given
    union = Mock()
    market = market_before_setup
    market.monetary_union = union
    return market, union


def test_request_advances_updates_accounts(market_with_union):
    # Given
    lender = Mock()
    market, union = market_with_union

    # When
    market.request_advances(lender, 100)

    # Then
    union.request_advances.assert_any_call(lender, 100)


def test_repay_advances_updates_accounts(market_with_union):
    # Given
    lender = Mock()
    market, union = market_with_union

    # When
    market.repay_advances(lender, 100, 10)

    # Then
    union.repay_advances.assert_any_call(lender, 100, 10)
