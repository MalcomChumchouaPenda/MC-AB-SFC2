import pytest
from unittest.mock import Mock
from model.roles.borrower import Borrower

# ---------------------------------------------------
# ARCHITECTURE TESTS
# ----------------------------------------------------


def test_is_eco_role():
    # Given
    from model.base import EcoRole

    # Assert
    assert issubclass(Borrower, EcoRole)


@pytest.fixture
def borrower_before_setup():
    # Given
    model = Mock()
    borrower = Borrower(model)
    return borrower


def test_has_default_loan_demand(borrower_before_setup):
    # Given
    borrower = borrower_before_setup

    # When
    borrower.setup()

    # Then
    assert borrower.loan_demand == 0.0


def test_has_default_net_worth(borrower_before_setup):
    # Given
    borrower = borrower_before_setup

    # When
    borrower.setup()

    # Then
    assert borrower.net_worth == 0.0


# ---------------------------------------------------
# PERCEPTIONS
# ----------------------------------------------------


@pytest.fixture
def borrower_with_space(borrower_before_setup):
    # Given
    space = Mock()
    borrower = borrower_before_setup
    borrower.space = space
    return borrower, space


def test_find_lenders(borrower_with_space):
    # Given
    borrower, space = borrower_with_space

    # When
    result = borrower.find_lenders()

    # Then
    space.find_lenders.assert_called_once_with()
    assert result == space.find_lenders.return_value


def test_find_loans(borrower_with_space):
    # Given
    borrower, space = borrower_with_space

    # When
    result = borrower.find_loans()

    # Then
    space.find_loans.assert_called_once_with(borrower)
    assert result == space.find_loans.return_value


# ---------------------------------------------------
# ACTIONS
# ----------------------------------------------------


def test_request_loan_use_lender_method(borrower_before_setup):
    # Given
    lender = Mock()
    borrower = borrower_before_setup

    # When
    borrower.request_loan(lender)

    # Then
    lender.receive_request.assert_called_with(borrower)


def test_repay_loan_use_space_method(borrower_with_space):
    # Given
    lender = Mock()
    borrower, space = borrower_with_space

    # When
    borrower.repay_loan(lender, 100, 10)

    # Then
    space.repay_loan.assert_called_with(borrower, lender, 100, 10)
