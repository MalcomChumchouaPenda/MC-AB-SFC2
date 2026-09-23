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
def depositor_before_setup():
    # Given
    model = Mock()
    depositor = Depositor(model)
    return depositor


# ---------------------------------------------------
# PERCEPTION TESTS
# ----------------------------------------------------


@pytest.fixture
def depositor_with_env(depositor_before_setup):
    # Given
    env = Mock()
    depositor = depositor_before_setup
    depositor.env = env
    return depositor, env


def test_find_deposit_banks_from_env(depositor_with_env):
    # Given
    depositor, env = depositor_with_env

    # When
    found = depositor.find_deposit_banks()

    # Then
    env.find_deposit_banks.assert_called_with()
    assert found == env.find_deposit_banks.return_value


def test_get_deposit_rate_from_deposit_bank(depositor_before_setup):
    # Given
    depositor = depositor_before_setup
    depositor.deposit_bank = Mock(deposit_rate=0.01)

    # When
    perceived = depositor.get_deposit_rate()

    # Then
    assert perceived == 0.01


# ---------------------------------------------------
# ACTION TESTS
# ----------------------------------------------------


def test_make_deposits_into_env(depositor_with_env):
    # Given
    depositor, env = depositor_with_env

    # When
    depositor.make_deposits(200)

    # Then
    env.make_deposits.assert_called_with(depositor, 200)


def test_withdraw_deposits_into_env(depositor_with_env):
    # Given
    depositor, env = depositor_with_env

    # When
    depositor.withdraw_deposits(200)

    # Then
    env.withdraw_deposits.assert_called_with(depositor, 200)


def test_choose_bank_into_env(depositor_with_env):
    # Given
    depositor, env = depositor_with_env
    depositor.deposit_bank = None
    deposit_bank = Mock()

    # When
    depositor.choose_bank(deposit_bank)

    # Then
    env.link_depositor_to_bank.assert_called_with(depositor, deposit_bank, 0)


def test_choose_bank_with_initial_amount(depositor_with_env):
    # Given
    depositor, env = depositor_with_env
    depositor.deposit_bank = None
    deposit_bank = Mock()

    # When
    depositor.choose_bank(deposit_bank, amount=100)

    # Then
    env.link_depositor_to_bank.assert_called_with(depositor, deposit_bank, 100)


def test_choose_bank_to_switch_bank(depositor_with_env):
    # Given
    old_deposit_bank = Mock()
    new_deposit_bank = Mock()
    depositor, env = depositor_with_env
    depositor.deposit_bank = old_deposit_bank

    # When
    depositor.choose_bank(new_deposit_bank)

    # Then
    env.unlink_depositor_with_bank.assert_called_with(depositor)
    env.link_depositor_to_bank.assert_called_with(depositor, new_deposit_bank, 0)
