import pytest
from unittest.mock import Mock
from mc_ab_sfc.spaces import CreditMarket

# ---------------------------------------------------
# ARCHITECTURAL TESTS
# ----------------------------------------------------


def test_is_ecospace():
    # Given
    from mc_ab_sfc.base import EcoSpace

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
    monkeypatch.setattr("mc_ab_sfc.spaces.BorrowerRole", FakeRole)

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
    monkeypatch.setattr("mc_ab_sfc.spaces.LenderRole", FakeRole)

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
    monkeypatch.setattr("mc_ab_sfc.spaces.LenderRole", FakeRole)

    # When
    result = market.search_lenders()

    # Then
    random = market.model.random
    assert not random.sample.called
    assert result == lenders
