import pytest
from unittest.mock import Mock
from model.roles.lender import Lender

# ---------------------------------------------------
# ARCHITECTURE TESTS
# ----------------------------------------------------


def test_is_eco_role():
    # Given
    from model.base import EcoRole

    # Assert
    assert issubclass(Lender, EcoRole)


@pytest.fixture
def lender_before_setup():
    # Given
    model = Mock()
    lender = Lender(model)
    return lender


def test_has_loan_applicants_list(lender_before_setup):
    # Given
    lender = lender_before_setup

    # When
    lender.setup()

    # Then
    assert lender.loan_applicants == []


# ---------------------------------------------------
#  ACTIONS
# ----------------------------------------------------


def test_receive_request(lender_before_setup):
    # Given
    borrower = Mock()
    lender = lender_before_setup
    lender.loan_applicants = []

    # When
    lender.receive_request(borrower)

    # Then
    assert lender.loan_applicants == [borrower]


@pytest.fixture
def lender_with_env(lender_before_setup):
    # Given
    env = Mock()
    lender = lender_before_setup
    lender.env = env
    return lender, env


def test_grant_loan(lender_with_env):
    # Given
    borrower = Mock()
    lender, env = lender_with_env

    # When
    lender.grant_loan(borrower, 100, 0.04)

    # Then
    env.grant_loan.assert_called_with(lender, borrower, 100, 0.04)


def test_request_advances(lender_with_env):
    # Given
    lender, env = lender_with_env

    # When
    lender.request_advances(100)

    # Then
    env.request_advances.assert_called_with(lender, 100)


def test_repay_advances(lender_with_env):
    # Given
    lender, env = lender_with_env

    # When
    lender.repay_advances(100, 10)

    # Then
    env.repay_advances.assert_called_with(lender, 100, 10)
