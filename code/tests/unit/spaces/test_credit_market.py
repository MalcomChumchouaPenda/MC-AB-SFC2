import pytest
from unittest.mock import Mock
from model.spaces.credit_market import CreditMarket

# ---------------------------------------------------
# ARCHITECTURE
# ----------------------------------------------------


def test_inherits_from_eco_space():
    # Given
    from model.base import EcoSpace

    # When
    is_derived = issubclass(CreditMarket, EcoSpace)

    # Then
    assert is_derived


def test_expose_discount_rate(fake_model):
    # Given
    market = CreditMarket(fake_model)
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
def market_without_roles(monkeypatch, fake_model):
    # Given
    monkeypatch.setattr("model.spaces.credit_market.Borrower", FakeBorrower)
    monkeypatch.setattr("model.spaces.credit_market.Lender", FakeLender)
    market = CreditMarket(fake_model)
    market.add_role = Mock()
    return market


def test_add_lender_creates_proper_role(market_without_roles):
    # Given
    agent = Mock()
    market = market_without_roles

    # When
    market.add_lender(agent)

    # Then
    market.add_role.assert_called_with(FakeLender, agent, "lender")


def test_add_lender_returns_created_role(market_without_roles):
    # Given
    agent = Mock()
    market = market_without_roles

    # When
    role = market.add_lender(agent)

    # Then
    assert role == market.add_role.return_value


def test_add_borrower_creates_proper_role(market_without_roles):
    # Given
    agent = Mock()
    market = market_without_roles

    # When
    market.add_borrower(agent)

    # Then
    market.add_role.assert_called_with(FakeBorrower, agent, "borrower")


def test_add_borrower_returns_created_role(market_without_roles):
    # Given
    agent = Mock()
    market = market_without_roles

    # When
    role = market.add_borrower(agent)

    # Then
    assert role == market.add_role.return_value


# ---------------------------------------------------
# CREDIT MATCHING
# ----------------------------------------------------


@pytest.fixture
def market_with_participants(market_without_roles):
    # Given
    lender = Mock()
    borrower = Mock(loan_demand=0)
    market = market_without_roles
    market.transfer_stock = Mock()
    market.make_transaction = Mock()
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
    market.transfer_stock.assert_any_call("loans", borrower.id, lender.id, 500)
    market.transfer_stock.assert_any_call(
        "deposits", borrower.bank_id, borrower.id, 500
    )
    market.transfer_stock.assert_any_call("cash", lender.id, borrower.bank_id, 500)


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
    bank_id = borrower.bank_id

    # When
    market.repay_loans(borrower, lender, 100, 10)

    # Then
    market.transfer_stock.assert_any_call("loans", lender.id, borrower.id, 100)
    market.transfer_stock.assert_any_call("cash", bank_id, lender.id, 110)
    market.transfer_stock.assert_any_call("deposits", borrower.id, bank_id, 110)
    market.make_transaction.assert_any_call("loan_interests", borrower.id, lender.id, 10)


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

    # When
    market.make_defaults(borrower, lender, 100)

    # Then
    market.transfer_stock.assert_any_call("loans", lender.id, borrower.id, 100)
    market.make_transaction.assert_any_call("loan_defaults", lender.id, borrower.id, 100)


# ---------------------------------------------------
# CASH ADVANCE REQUEST / REPAYMENT
# ----------------------------------------------------


def test_request_advances_updates_accounts(market_with_participants):
    # Given
    market, _, lender = market_with_participants

    # When
    market.request_advances(lender, 100)

    # Then
    market.transfer_stock.assert_any_call("cash", lender.cb_id, lender.id, 100)
    market.transfer_stock.assert_any_call("advances", lender.id, lender.cb_id, 100)


def test_repay_advances_updates_accounts(market_with_participants):
    # Given
    market, _, lender = market_with_participants

    # When
    market.repay_advances(lender, 100, 10)

    # Then
    market.transfer_stock.assert_any_call("cash", lender.id, lender.cb_id, 110)
    market.transfer_stock.assert_any_call("advances", lender.cb_id, lender.id, 100)
    market.make_transaction.assert_any_call("adv_interests", lender.id, lender.cb_id, 10)
