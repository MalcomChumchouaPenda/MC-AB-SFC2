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
def role_with_env():
    # Given
    agent, env = Mock(), Mock()
    role = Lender(agent, env)
    return role, env


def test_has_loan_applicants_list(role_with_env):
    # Given
    role, _ = role_with_env

    # Assert
    assert role.loan_applicants == []


# ---------------------------------------------------
#  ACTIONS
# ----------------------------------------------------


def test_receive_request(role_with_env):
    # Given
    borrower = Mock()
    role, _ = role_with_env
    role.loan_applicants = []

    # When
    role.receive_request(borrower)

    # Then
    assert role.loan_applicants == [borrower]


def test_grant_loan(role_with_env):
    # Given
    borrower = Mock()
    role, env = role_with_env

    # When
    role.grant_loan(borrower, 100, 0.04)

    # Then
    env.grant_loan.assert_called_with(role, borrower, 100, 0.04)


def test_request_advances(role_with_env):
    # Given
    role, env = role_with_env

    # When
    role.request_advances(100)

    # Then
    env.request_advances.assert_called_with(role, 100)


def test_repay_advances(role_with_env):
    # Given
    role, env = role_with_env

    # When
    role.repay_advances(100, 10)

    # Then
    env.repay_advances.assert_called_with(role, 100, 10)
