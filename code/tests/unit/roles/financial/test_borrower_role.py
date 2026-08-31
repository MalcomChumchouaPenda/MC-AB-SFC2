import pytest
from unittest.mock import Mock
from model.roles.financial import BorrowerRole

# ---------------------------------------------------
# ARCHITECTURE TESTS
# ----------------------------------------------------


def test_is_eco_role():
    # Given
    from model.base import EcoRole

    # Assert
    assert issubclass(BorrowerRole, EcoRole)


@pytest.fixture
def borrower():
    # Given
    market = Mock()
    agent = Mock(id=1)
    return BorrowerRole(agent, market)


def test_has_default_loan_demand(borrower):
    # Assert
    assert borrower.loan_demand == 0.0


def test_exposes_target_leverage(borrower):
    # Given
    firm = borrower.agent
    firm.desired_loans = 50
    firm.equity = 100

    # Assert
    assert borrower.target_leverage == pytest.approx(0.50)


# ---------------------------------------------------
# BEHAVIORAL TESTS
# ----------------------------------------------------


def test_search_lenders(borrower):
    # Given
    lenders = [Mock() for _ in range(2)]
    market = borrower.space
    market.search_lenders.return_value = lenders

    # When
    result = borrower.search_lenders()

    # Then
    market.search_lenders.assert_called_once_with()
    assert result == lenders


def test_request_loan(borrower):
    # Given
    lender = Mock()

    # When
    borrower.request_loan(lender)

    # Then
    lender.receive_request.assert_called_with(borrower)
