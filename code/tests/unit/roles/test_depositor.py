import pytest
from unittest.mock import Mock
from model.extensions import EcoRole
from model.roles.depositor import Depositor

# ---------------------------------------------------
# ARCHITECTURE
# ----------------------------------------------------


def test_inherits_from_eco_role():
    # Given
    from model.extensions import EcoRole

    # When
    is_derived = issubclass(Depositor, EcoRole)

    # Then
    assert is_derived


@pytest.fixture
def role():
    # Given
    env = Mock()
    agent_id = 1
    return Depositor(agent_id, env)


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
    deposit_bank = Mock(deposit_rate=0.01)
    role.env.roles = {1: deposit_bank, 0: Mock()}

    # When
    perceived = role.get_deposit_rate(1)

    # Then
    assert perceived == 0.01


# ---------------------------------------------------
# ACTION TESTS
# ----------------------------------------------------


@pytest.fixture
def banks(role):
    # Given
    banks = {i: Mock() for i in range(4)}
    role.env.roles = banks
    return banks


def test_make_deposits_uses_env_method(role, banks):
    # Given
    env = role.env

    # When
    role.make_deposits(2, 200)

    # Then
    env.make_deposits.assert_called_with(role, banks[2], 200)


def test_withdraw_deposits_uses_env_method(role, banks):
    # Given
    env = role.env

    # When
    role.withdraw_deposits(2, 200)

    # Then
    env.withdraw_deposits.assert_called_with(role, banks[2], 200)


def test_join_deposit_bank_uses_env_method(role, banks):
    # Given
    env = role.env

    # When
    role.join_deposit_bank(1)

    # Then
    env.join_deposit_bank.assert_called_with(role, banks[1], 0)


def test_leave_deposit_bank_uses_env_method(role, banks):
    # Given
    env = role.env

    # When
    role.leave_deposit_bank(1)

    # Then
    env.leave_deposit_bank.assert_called_with(role, banks[1])
