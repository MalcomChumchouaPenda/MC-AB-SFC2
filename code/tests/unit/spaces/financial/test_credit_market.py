import pytest
from unittest.mock import Mock
from model.spaces.financial import CreditMarket

# ---------------------------------------------------
# ARCHITECTURE TESTS
# ----------------------------------------------------


def test_is_eco_space():
    # Given
    from model.base import EcoSpace

    # Assert
    assert issubclass(CreditMarket, EcoSpace)


# ---------------------------------------------------
# BEHAVIORAL TESTS
# ----------------------------------------------------


class FakeRole:
    pass


@pytest.fixture
def market():
    # Given
    model = Mock()
    market = CreditMarket(model)
    return market


def test_add_borrower_creates_borrower_role(market, monkeypatch):
    # Given
    household = Mock()
    market.add_role = Mock()
    monkeypatch.setattr("model.spaces.financial.BorrowerRole", FakeRole)

    # When
    borrower = market.add_borrower(household)

    # Then
    action = market.add_role
    action.assert_called_with(FakeRole, household, "borrower")
    assert borrower is action.return_value


def test_add_lender_creates_lender(market, monkeypatch):
    # Given
    bank = Mock()
    market.add_role = Mock()
    monkeypatch.setattr("model.spaces.financial.LenderRole", FakeRole)

    # When
    lender = market.add_lender(bank)

    # Then
    action = market.add_role
    action.assert_called_with(FakeRole, bank, "lender")
    assert lender is action.return_value


def test_search_lenders_returns_all_lenders(market, monkeypatch):
    # Given
    others = [Mock() for _ in range(5)]
    lenders = [FakeRole() for _ in range(5)]
    market.graph.add_nodes_from(others + lenders)
    monkeypatch.setattr("model.spaces.financial.LenderRole", FakeRole)

    # When
    result = market.search_lenders()

    # Then
    random = market.model.random
    assert not random.sample.called
    assert result == lenders


def test_grant_loan_creates_credit_edge(market):
    # Given
    borrower = Mock(loan_demand=1000)
    lender = Mock()
    graph = market.graph
    graph.add_nodes_from([lender, borrower])

    # When
    market.grant_loan(lender, borrower, 500, 0.05)

    # Then
    assert len(graph.edges) == 1
    assert graph.has_edge(borrower, lender)
    assert graph[borrower][lender]["amount"] == 500
    assert graph[borrower][lender]["rate"] == 0.05


def test_grant_loan_reduces_loan_demand(market):
    # Given
    borrower = Mock(loan_demand=1000)
    lender = Mock()
    graph = market.graph
    graph.add_nodes_from([lender, borrower])

    # When
    market.grant_loan(lender, borrower, 500, 0.05)

    # Then
    assert borrower.loan_demand == 500


def test_grant_loan_modifies_stocks_and_flows(market):
    # Given
    borrower = Mock(loan_demand=1000)
    lender = Mock()
    graph = market.graph
    graph.add_nodes_from([lender, borrower])

    # When
    market.grant_loan(lender, borrower, 500, 0.05)

    # Then
    lender.increase_stock.assert_any_call("loans", 500)
    lender.increase_stock.assert_any_call("deposits", 500)
    borrower.increase_stock.assert_any_call("loans", 500)
    borrower.increase_stock.assert_any_call("deposits", 500)
