import pytest
from unittest.mock import Mock
from model.roles.deposit_guarantee import DepositGuarantee

# ---------------------------------------------------
# ARCHITECTURE TESTS
# ----------------------------------------------------


def test_is_eco_role():
    # Given
    from model.base import EcoRole

    # Assert
    assert issubclass(DepositGuarantee, EcoRole)


@pytest.fixture
def role_with_env():
    # Given
    agent, env = Mock(), Mock()
    role = DepositGuarantee(agent, env)
    return role, env


# ---------------------------------------------------
# PERCEPTION TESTS
# ----------------------------------------------------


def test_find_defaults_from_env(role_with_env):
    # Given
    role, env = role_with_env

    # When
    found = role.find_defaults()

    # Then
    env.find_defaults.assert_called_with()
    assert found == env.find_defaults.return_value


def test_find_deposits_from_env(role_with_env):
    # Given
    role, env = role_with_env
    bank = Mock()

    # When
    found = role.find_deposits(bank)

    # Then
    env.find_deposits.assert_called_with(bank)
    assert found == env.find_deposits.return_value


# ---------------------------------------------------
# ACTION TESTS
# ----------------------------------------------------


def test_reimburse_deposits_into_env(role_with_env):
    # Given
    role, env = role_with_env
    depositor = Mock()

    # When
    role.reimburse_deposits(depositor, 200)

    # Then
    env.reimburse_deposits.assert_called_with(role, depositor, 200)
