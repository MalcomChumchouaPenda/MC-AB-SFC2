import pytest
from unittest.mock import Mock
from model.base import EcoRole
from model.roles.deposit_supplier import DepositSupplier

# ---------------------------------------------------
# ARCHITECTURE
# ----------------------------------------------------


def test_inherits_from_eco_role():
    # Given
    from model.base import EcoRole

    # When
    is_derived = issubclass(DepositSupplier, EcoRole)

    # Then
    assert is_derived


@pytest.fixture
def role():
    # Given
    agent, env = Mock(), Mock()
    return DepositSupplier(agent, env)


# ---------------------------------------------------
# PERCEPTION TESTS
# ----------------------------------------------------


def test_find_deposit_demanders_from_env(role):
    # Given
    env = role.env

    # When
    found = role.find_deposit_demanders()

    # Then
    env.find_all_roles.assert_called_with("deposit_demander")
    assert found == env.find_all_roles.return_value


def test_get_deposit_rate_from_deposit_demander(role):
    # Given
    role.deposit_demander = Mock(deposit_rate=0.01)

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
    role.deposit_demander = None
    deposit_demander = Mock()

    # When
    role.choose_bank(deposit_demander)

    # Then
    env.join_bank.assert_called_with(role, deposit_demander, 0)


def test_choose_bank_with_initial_amount(role):
    # Given
    env = role.env
    role.deposit_demander = None
    deposit_demander = Mock()

    # When
    role.choose_bank(deposit_demander, amount=100)

    # Then
    env.join_bank.assert_called_with(role, deposit_demander, 100)


def test_choose_bank_to_switch_bank(role):
    # Given
    old_deposit_demander = Mock()
    new_deposit_demander = Mock()
    role.deposit_demander = old_deposit_demander
    env = role.env

    # When
    role.choose_bank(new_deposit_demander)

    # Then
    env.leave_bank.assert_called_with(role)
    env.join_bank.assert_called_with(role, new_deposit_demander, 0)
