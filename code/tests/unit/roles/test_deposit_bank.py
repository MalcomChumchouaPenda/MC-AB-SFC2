import pytest
from unittest.mock import Mock
from model.roles.deposit_bank import DepositBank

# ---------------------------------------------------
# ARCHITECTURE TESTS
# ----------------------------------------------------


def test_is_eco_role():
    # Given
    from model.base import EcoRole

    # Assert
    assert issubclass(DepositBank, EcoRole)


@pytest.fixture
def role_before_setup():
    # Given
    model = Mock()
    role = DepositBank(model)
    return role


def test_has_defaulted(role_before_setup):
    # Given
    role = role_before_setup

    # When
    role.setup()

    # Then
    assert role.defaulted is False


# ---------------------------------------------------
# PERCEPTION TESTS
# ----------------------------------------------------


@pytest.fixture
def role_with_env(role_before_setup):
    # Given
    env = Mock()
    role = role_before_setup
    role.env = env
    return role, env


def test_find_deposit_accounts_from_env(role_with_env):
    # Given
    role, env = role_with_env

    # When
    found = role.find_deposit_accounts()

    # Then
    env.find_deposit_accounts.assert_called_with(role)
    assert found == env.find_deposit_accounts.return_value


# ---------------------------------------------------
# ACTION TESTS
# ----------------------------------------------------


def test_pay_interests_into_env(role_with_env):
    # Given
    role, env = role_with_env
    depositor = Mock()

    # When
    role.pay_interests(depositor, 200)

    # Then
    env.pay_interests.assert_called_with(role, depositor, 200)
