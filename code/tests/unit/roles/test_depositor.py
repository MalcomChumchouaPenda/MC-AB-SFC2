import pytest
from unittest.mock import Mock
from model.roles.depositor import Depositor

# ---------------------------------------------------
# ARCHITECTURE TESTS
# ----------------------------------------------------


def test_is_eco_role():
    # Given
    from model.base import EcoRole

    # Assert
    assert issubclass(Depositor, EcoRole)


@pytest.fixture
def role_with_env():
    # Given
    agent, env = Mock(), Mock()
    role = Depositor(agent, env)
    return role, env


# ---------------------------------------------------
# PERCEPTION TESTS
# ----------------------------------------------------


def test_find_deposit_banks_from_env(role_with_env, make_dlist):
    # Given
    deposit_bank = Mock()
    role, env = role_with_env
    env.find_all_roles.return_value = make_dlist([deposit_bank])

    # When
    found = role.find_deposit_banks()

    # Then
    env.find_all_roles.assert_called_with("deposit_bank")
    assert list(found) == [deposit_bank]


def test_get_deposit_rate_from_deposit_bank(role_with_env):
    # Given
    role, _ = role_with_env
    role.deposit_bank = Mock(deposit_rate=0.01)

    # When
    perceived = role.get_deposit_rate()

    # Then
    assert perceived == 0.01


# ---------------------------------------------------
# ACTION TESTS
# ----------------------------------------------------


def test_make_deposits_into_env(role_with_env):
    # Given
    role, env = role_with_env

    # When
    role.make_deposits(200)

    # Then
    env.make_deposits.assert_called_with(role, 200)


def test_withdraw_deposits_into_env(role_with_env):
    # Given
    role, env = role_with_env

    # When
    role.withdraw_deposits(200)

    # Then
    env.withdraw_deposits.assert_called_with(role, 200)


def test_choose_bank_into_env(role_with_env):
    # Given
    role, env = role_with_env
    role.deposit_bank = None
    deposit_bank = Mock()

    # When
    role.choose_bank(deposit_bank)

    # Then
    env.join_deposit_bank.assert_called_with(role, deposit_bank, 0)


def test_choose_bank_with_initial_amount(role_with_env):
    # Given
    role, env = role_with_env
    role.deposit_bank = None
    deposit_bank = Mock()

    # When
    role.choose_bank(deposit_bank, amount=100)

    # Then
    env.join_deposit_bank.assert_called_with(role, deposit_bank, 100)


def test_choose_bank_to_switch_bank(role_with_env):
    # Given
    old_deposit_bank = Mock()
    new_deposit_bank = Mock()
    role, env = role_with_env
    role.deposit_bank = old_deposit_bank

    # When
    role.choose_bank(new_deposit_bank)

    # Then
    env.leave_deposit_bank.assert_called_with(role)
    env.join_deposit_bank.assert_called_with(role, new_deposit_bank, 0)
