import pytest
from unittest.mock import Mock
from model.roles.lender import Lender

# ---------------------------------------------------
# ARCHITECTURE
# ----------------------------------------------------


def test_inherits_from_eco_role():
    # Given
    from model.base import EcoRole

    # When
    is_derived = issubclass(Lender, EcoRole)

    # Then
    assert is_derived


@pytest.fixture
def role():
    # Given
    agent, env = Mock(), Mock()
    return Lender(agent, env)


def test_has_loan_applicants_list(role):
    # Assert
    assert role.loan_applicants == []


# ---------------------------------------------------
#  ACTIONS
# ----------------------------------------------------


def test_receive_request(role):
    # Given
    borrower = Mock()
    role.loan_applicants = []

    # When
    role.receive_request(borrower)

    # Then
    assert role.loan_applicants == [borrower]


def test_grant_loan(role):
    # Given
    borrower = Mock()
    env = role.env

    # When
    role.grant_loan(borrower, 100, 0.04)

    # Then
    env.grant_loan.assert_called_with(role, borrower, 100, 0.04)


def test_request_advances(role):
    # Given
    env = role.env

    # When
    role.request_advances(100)

    # Then
    env.request_advances.assert_called_with(role, 100)


def test_repay_advances(role):
    # Given
    env = role.env

    # When
    role.repay_advances(100, 10)

    # Then
    env.repay_advances.assert_called_with(role, 100, 10)
