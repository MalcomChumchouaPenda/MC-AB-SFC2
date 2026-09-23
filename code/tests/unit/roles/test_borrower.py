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
def role_with_env():
    # Given
    agent, env = Mock(), Mock()
    role = Borrower(agent, env)
    return role, env


def test_has_default_loan_demand(role_with_env):
    # Given
    role, _ = role_with_env

    # Assert
    assert role.loan_demand == 0.0


def test_has_default_net_worth(role_with_env):
    # Given
    role, _ = role_with_env

    # Assert
    assert role.net_worth == 0.0


# ---------------------------------------------------
# PERCEPTIONS
# ----------------------------------------------------


def test_find_lenders(role_with_env):
    # Given
    role, env = role_with_env

    # When
    result = role.find_lenders()

    # Then
    env.find_lenders.assert_called_once_with()
    assert result == env.find_lenders.return_value


def test_find_loans(role_with_env):
    # Given
    role, env = role_with_env

    # When
    result = role.find_loans()

    # Then
    env.find_loans.assert_called_once_with(role)
    assert result == env.find_loans.return_value


# ---------------------------------------------------
# ACTIONS
# ----------------------------------------------------


def test_request_loans_use_lender_method(role_with_env):
    # Given
    lender = Mock()
    role, _ = role_with_env

    # When
    role.request_loans(lender)

    # Then
    lender.receive_request.assert_called_with(role)


def test_repay_loans_use_env_method(role_with_env):
    # Given
    lender = Mock()
    role, env = role_with_env

    # When
    role.repay_loans(lender, 100, 10)

    # Then
    env.repay_loans.assert_called_with(role, lender, 100, 10)


def test_make_defaults_use_env_method(role_with_env):
    # Given
    lender = Mock()
    role, env = role_with_env

    # When
    role.make_defaults(lender, 100)

    # Then
    env.make_defaults.assert_called_with(role, lender, 100)
