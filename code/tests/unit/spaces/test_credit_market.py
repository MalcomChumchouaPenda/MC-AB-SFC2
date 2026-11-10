import pytest
from unittest.mock import Mock, call
from model.spaces.credit_market import CreditMarket

# ---------------------------------------------------
# ARCHITECTURE
# ----------------------------------------------------


def test_inherits_from_eco_space():
    # Given
    from model.extensions import EcoSpace

    # When
    is_derived = issubclass(CreditMarket, EcoSpace)

    # Then
    assert is_derived


@pytest.fixture
def market(fake_model):
    # Given
    return CreditMarket(fake_model)


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


@pytest.fixture
def market_without_roles(market):
    # Given
    market.add_role = Mock()
    return market


def test_add_bank_add_lender_role(market_without_roles, monkeypatch):
    # Given
    bank = Mock()
    role_cls = Mock(name="Lender")
    monkeypatch.setattr("model.spaces.credit_market.Lender", role_cls)
    market = market_without_roles

    # When
    market.add_bank(bank)

    # Then
    market.add_role.assert_called_with(role_cls, bank)


def test_add_firm_add_borrower_role(market_without_roles, monkeypatch):
    # Given
    firm = Mock()
    role_cls = Mock(name="Borrower")
    monkeypatch.setattr("model.spaces.credit_market.Borrower", role_cls)
    market = market_without_roles

    # When
    market.add_firm(firm)

    # Then
    market.add_role.assert_called_with(role_cls, firm)


# ---------------------------------------------------
# CREDIT MATCHING
# ----------------------------------------------------


@pytest.fixture
def lender():
    # Given
    return Mock()


@pytest.fixture
def borrower():
    # Given
    return Mock(loan_demand=0)


@pytest.fixture
def market_without_loan(market):
    # Given
    market.transfer_stock = Mock()
    market.make_transaction = Mock()
    return market


def test_grant_loan_creates_graph_edge(market_without_loan, lender, borrower):
    # Given
    market = market_without_loan
    graph = market.graph

    # When
    market.grant_loan(lender, borrower, 500, 0.05)

    # Then
    assert graph.has_edge(borrower, lender)
    assert graph[borrower][lender]["amount"] == 500
    assert graph[borrower][lender]["rate"] == 0.05


def test_grant_loan_transfers_cash(market_without_loan, lender, borrower):
    # Given
    market = market_without_loan

    # When
    market.grant_loan(lender, borrower, 500, 0.05)

    # Then
    market.transfer_stock.assert_any_call("cash", lender.id, borrower.id, 500)


def test_grant_loan_updates_accounts(market_without_loan, lender, borrower):
    # Given
    market = market_without_loan

    # When
    market.grant_loan(lender, borrower, 500, 0.05)

    # Then
    market.transfer_stock.assert_any_call("loans", borrower.id, lender.id, 500)


def test_grant_loan_reduces_loan_demand(market_without_loan, lender, borrower):
    # Given
    market = market_without_loan
    borrower.loan_demand = 900

    # When
    market.grant_loan(lender, borrower, 500, 0.05)

    # Then
    assert borrower.loan_demand == 400


# ---------------------------------------------------
# LOAN REPAYMENT
# ----------------------------------------------------


@pytest.fixture
def market_with_loan(market_without_loan, lender, borrower):
    # Given
    market = market_without_loan
    market.graph.add_edge(borrower, lender, amount=100, rate=0.1)
    return market


def test_repay_loans_updates_graph_edge(market_with_loan, lender, borrower):
    # Given
    market = market_with_loan
    graph = market.graph
    graph[borrower][lender]["amount"] = 300

    # When
    market.repay_loans(borrower, lender, 100, 10)

    # Then
    assert graph[borrower][lender]["amount"] == 200


def test_repay_loans_transfers_cash(market_with_loan, lender, borrower):
    # Given
    market = market_with_loan

    # When
    market.repay_loans(borrower, lender, 100, 10)

    # Then
    market.transfer_stock.assert_any_call("cash", borrower.id, lender.id, 110)


def test_repay_loans_updates_accounts(market_with_loan, lender, borrower):
    # Given
    market = market_with_loan
    bank_id = lender.id

    # When
    market.repay_loans(borrower, lender, 100, 10)

    # Then
    market.transfer_stock.assert_any_call("loans", bank_id, borrower.id, 100)
    market.make_transaction.assert_any_call("loan_interests", borrower.id, bank_id, 10)


def test_make_defaults_updates_graph_edge(market_with_loan, lender, borrower):
    # Given
    market = market_with_loan
    graph = market.graph
    graph[borrower][lender]["amount"] = 300

    # When
    market.make_defaults(borrower, lender, 100)

    # Then
    assert graph[borrower][lender]["amount"] == 200


def test_make_defaults_updates_accounts(market_with_loan, lender, borrower):
    # Given
    market = market_with_loan
    bank_id = lender.id

    # When
    market.make_defaults(borrower, lender, 100)

    # Then
    market.transfer_stock.assert_any_call("loans", bank_id, borrower.id, 100)
    market.make_transaction.assert_any_call("loan_defaults", bank_id, borrower.id, 100)


# ---------------------------------------------------
# EVOLUTION
# ----------------------------------------------------


@pytest.fixture
def lenders():
    # Given
    lenders = []
    for defaulted in (True, False):
        role = Mock(defaulted=defaulted)
        role.name = "lender"
        lenders.append(role)
    return lenders


@pytest.fixture
def borrowers():
    # Given
    borrowers = []
    for defaulted in (True, False):
        role = Mock(defaulted=defaulted)
        role.name = "borrower"
        borrowers.append(role)
    return borrowers


@pytest.fixture
def market_with_defaults(market_without_roles, lenders, borrowers):
    market = market_without_roles
    for role in lenders + borrowers:
        market.roles[role.id] = role
    market.remove_role = Mock()
    return market


def test_clear_defaults_removes_defaulted_lenders(market_with_defaults, lenders):
    # Given
    market = market_with_defaults

    # When
    market.clear_defaults()

    # Then
    assert call(lenders[0]) in market.remove_role.call_args_list
    assert call(lenders[1]) not in market.remove_role.call_args_list


def test_clear_defaults_removes_defaulted_borrowers(market_with_defaults, borrowers):
    # Given
    market = market_with_defaults

    # When
    market.clear_defaults()

    # Then
    assert call(borrowers[0]) in market.remove_role.call_args_list
    assert call(borrowers[1]) not in market.remove_role.call_args_list
