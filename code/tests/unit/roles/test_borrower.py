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
def borrower_with_env(borrower_before_setup):
    # Given
    env = Mock()
    borrower = borrower_before_setup
    borrower.env = env
    return borrower, env


def test_find_lenders(borrower_with_env):
    # Given
    borrower, env = borrower_with_env

    # When
    result = borrower.find_lenders()

    # Then
    env.find_lenders.assert_called_once_with()
    assert result == env.find_lenders.return_value


def test_find_loans(borrower_with_env):
    # Given
    borrower, env = borrower_with_env

    # When
    result = borrower.find_loans()

    # Then
    env.find_loans.assert_called_once_with(borrower)
    assert result == env.find_loans.return_value


# ---------------------------------------------------
# ACTIONS
# ----------------------------------------------------


def test_request_loans_use_lender_method(borrower_before_setup):
    # Given
    lender = Mock()
    borrower = borrower_before_setup

    # When
    borrower.request_loans(lender)

    # Then
    lender.receive_request.assert_called_with(borrower)


def test_repay_loans_use_env_method(borrower_with_env):
    # Given
    lender = Mock()
    borrower, env = borrower_with_env

    # When
    borrower.repay_loans(lender, 100, 10)

    # Then
    env.repay_loans.assert_called_with(borrower, lender, 100, 10)


def test_make_defaults_use_env_method(borrower_with_env):
    # Given
    lender = Mock()
    borrower, env = borrower_with_env

    # When
    borrower.make_defaults(lender, 100)

    # Then
    env.make_defaults.assert_called_with(borrower, lender, 100)
