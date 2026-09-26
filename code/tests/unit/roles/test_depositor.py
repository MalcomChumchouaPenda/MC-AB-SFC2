import pytest
from unittest.mock import Mock
from model.base import EcoRole
from model.roles.depositor import Depositor

# ---------------------------------------------------
# ARCHITECTURE TESTS
# ----------------------------------------------------


def test_inherits_from_eco_role():
    # Given
    from model.base import EcoRole

    # When
    is_derived = issubclass(Depositor, EcoRole)

    # Then
    assert is_derived


@pytest.fixture
def role():
    # Given
    agent, env = Mock(), Mock()
    return Depositor(agent, env)


# ---------------------------------------------------
# PERCEPTION TESTS
# ----------------------------------------------------


def test_find_deposit_banks_from_env(role):
    # Given
    env = role.env

    # When
    found = role.find_deposit_banks()

    # Then
    env.find_all_roles.assert_called_with("deposit_bank")
    assert found == env.find_all_roles.return_value


def test_get_deposit_rate_from_deposit_bank(role):
    # Given
    role.deposit_bank = Mock(deposit_rate=0.01)

    # When
    perceived = role.get_deposit_rate()

    # Then
    assert perceived == 0.01


# ---------------------------------------------------
# ACTION TESTS
# ----------------------------------------------------


def test_make_deposits_into_env(role):
    # Given
    env = role.env

    # When
    role.make_deposits(200)

    # Then
    env.make_deposits.assert_called_with(role, 200)


def test_withdraw_deposits_into_env(role):
    # Given
    env = role.env

    # When
    role.withdraw_deposits(200)

    # Then
    env.withdraw_deposits.assert_called_with(role, 200)


def test_choose_bank_into_env(role):
    # Given
    env = role.env
    role.deposit_bank = None
    deposit_bank = Mock()

    # When
    role.choose_bank(deposit_bank)

    # Then
    env.join_deposit_bank.assert_called_with(role, deposit_bank, 0)


def test_choose_bank_with_initial_amount(role):
    # Given
    env = role.env
    role.deposit_bank = None
    deposit_bank = Mock()

    # When
    role.choose_bank(deposit_bank, amount=100)

    # Then
    env.join_deposit_bank.assert_called_with(role, deposit_bank, 100)


def test_choose_bank_to_switch_bank(role):
    # Given
    old_deposit_bank = Mock()
    new_deposit_bank = Mock()
    role.deposit_bank = old_deposit_bank
    env = role.env

    # When
    role.choose_bank(new_deposit_bank)

    # Then
    env.leave_deposit_bank.assert_called_with(role)
    env.join_deposit_bank.assert_called_with(role, new_deposit_bank, 0)
