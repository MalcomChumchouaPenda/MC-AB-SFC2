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
def guarantee_before_setup():
    # Given
    model = Mock()
    guarantee = DepositGuarantee(model)
    return guarantee


# ---------------------------------------------------
# PERCEPTION TESTS
# ----------------------------------------------------


@pytest.fixture
def guarantee_with_env(guarantee_before_setup):
    # Given
    env = Mock()
    guarantee = guarantee_before_setup
    guarantee.env = env
    return guarantee, env


def test_find_defaulted_banks_from_env(guarantee_with_env):
    # Given
    guarantee, env = guarantee_with_env

    # When
    found = guarantee.find_defaulted_banks()

    # Then
    env.find_defaulted_banks.assert_called_with()
    assert found == env.find_defaulted_banks.return_value


def test_find_deposit_accounts_from_env(guarantee_with_env):
    # Given
    guarantee, env = guarantee_with_env
    bank = Mock()

    # When
    found = guarantee.find_deposit_accounts(bank)

    # Then
    env.find_deposit_accounts.assert_called_with(bank)
    assert found == env.find_deposit_accounts.return_value


# ---------------------------------------------------
# ACTION TESTS
# ----------------------------------------------------


def test_reimburse_deposits_into_env(guarantee_with_env):
    # Given
    guarantee, env = guarantee_with_env
    depositor = Mock()

    # When
    guarantee.reimburse_deposits(depositor, 200)

    # Then
    env.reimburse_deposits.assert_called_with(guarantee, depositor, 200)
