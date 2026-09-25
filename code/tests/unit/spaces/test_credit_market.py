import pytest
from unittest.mock import Mock
from agentpy import AgentDList
from model.base import EcoSpace
from model.spaces.credit_market import CreditMarket

# ---------------------------------------------------
# ARCHITECTURE TESTS
# ----------------------------------------------------


def test_is_eco_space():
    # Assert
    assert issubclass(CreditMarket, EcoSpace)


@pytest.fixture
def market():
    # Given
    model = Mock()
    market = CreditMarket(model)
    return market


def test_has_lenders_list(market):
    # Assert
    assert isinstance(market.lenders, AgentDList)


def test_has_borrowers_list(market):
    # Assert
    assert isinstance(market.borrowers, AgentDList)


def test_expose_discount_rate(market):
    # Given
    market.env = Mock(discount_rate=0.05)

    # When
    exposed = market.discount_rate

    # Then
    assert exposed == 0.05


# ---------------------------------------------------
# ROLES
# ----------------------------------------------------


FakeLender = Mock()
FakeBorrower = Mock()


@pytest.fixture
def market_without_lenders(monkeypatch, market):
    # Given
    monkeypatch.setattr("model.spaces.credit_market.Lender", FakeLender)
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


@pytest.fixture
def market_without_borrowers(monkeypatch, market):
    # Given
    monkeypatch.setattr("model.spaces.credit_market.Borrower", FakeBorrower)
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


@pytest.fixture
def market_with_participants(market):
    # Given
    lender = Mock()
    borrower = Mock(loan_demand=0)
    market.transfer_stock = Mock()
    market.record_flow = Mock()
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
    transfer_stock = market.transfer_stock

    # When
    market.grant_loan(lender, borrower, 500, 0.05)

    # Then
    transfer_stock.assert_any_call("loans", borrower.id, lender.id, 500)
    transfer_stock.assert_any_call("deposits", borrower.bank_id, borrower.id, 500)
    transfer_stock.assert_any_call("cash", lender.id, borrower.bank_id, 500)


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


@pytest.fixture
def market_with_loan(market_with_participants):
    # Given
    market, borrower, lender = market_with_participants
    market.graph.add_edge(borrower, lender, amount=100, rate=0.1)
    return market, borrower, lender


def test_repay_loans_updates_graph_edge(market_with_loan):
    # Given
    market, borrower, lender = market_with_loan
    graph = market.graph
    graph[borrower][lender]["amount"] = 300

    # When
    market.repay_loans(borrower, lender, 100, 10)

    # Then
    assert graph[borrower][lender]["amount"] == 200


def test_repay_loans_updates_accounts(market_with_loan):
    # Given
    market, borrower, lender = market_with_loan
    transfer_stock = market.transfer_stock
    record_flow = market.record_flow

    # When
    market.repay_loans(borrower, lender, 100, 10)

    # Then
    transfer_stock.assert_any_call("loans", lender.id, borrower.id, 100)
    transfer_stock.assert_any_call("cash", borrower.bank_id, lender.id, 110)
    transfer_stock.assert_any_call("deposits", borrower.id, borrower.bank_id, 110)
    record_flow.assert_any_call("loan_interests", borrower.id, lender.id, 10)


def test_make_defaults_updates_graph_edge(market_with_loan):
    # Given
    market, borrower, lender = market_with_loan
    graph = market.graph
    graph[borrower][lender]["amount"] = 300

    # When
    market.make_defaults(borrower, lender, 100)

    # Then
    assert graph[borrower][lender]["amount"] == 200


def test_make_defaults_updates_accounts(market_with_loan):
    # Given
    market, borrower, lender = market_with_loan
    transfer_stock = market.transfer_stock
    record_flow = market.record_flow

    # When
    market.make_defaults(borrower, lender, 100)

    # Then
    transfer_stock.assert_any_call("loans", lender.id, borrower.id, 100)
    record_flow.assert_any_call("loan_defaults", lender.id, borrower.id, 100)


# ---------------------------------------------------
# CASH ADVANCE REQUEST / REPAYMENT
# ----------------------------------------------------


def test_request_advances_updates_accounts(market):
    # Given
    lender = Mock()
    transfer_stock = market.transfer_stock = Mock()

    # When
    market.request_advances(lender, 100)

    # Then
    transfer_stock.assert_any_call("cash", lender.cb_id, lender.id, 100)
    transfer_stock.assert_any_call("advances", lender.id, lender.cb_id, 100)


def test_repay_advances_updates_accounts(market):
    # Given
    lender = Mock()
    transfer_stock = market.transfer_stock = Mock()
    record_flow = market.record_flow = Mock()

    # When
    market.repay_advances(lender, 100, 10)

    # Then
    transfer_stock.assert_any_call("cash", lender.id, lender.cb_id, 110)
    transfer_stock.assert_any_call("advances", lender.cb_id, lender.id, 100)
    record_flow.assert_any_call("adv_interests", lender.id, lender.cb_id, 10)
