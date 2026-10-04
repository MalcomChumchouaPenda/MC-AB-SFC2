import pytest
from unittest.mock import Mock
from model.roles.deposit_bank import DepositBank

# ---------------------------------------------------
# ARCHITECTURE
# ----------------------------------------------------


def test_inherits_from_eco_role():
    # Given
    from model.extensions import EcoRole

    # When
    is_derived = issubclass(DepositBank, EcoRole)

    # Then
    assert is_derived


def test_initializes_defaulted():
    # Given
    agent, env = Mock(), Mock()

    # When
    role = DepositBank(agent, env)

    # Then
    assert role.defaulted is False


# ---------------------------------------------------
# PERCEPTION TESTS
# ----------------------------------------------------


@pytest.fixture
def role():
    # Given
    agent, env = Mock(), Mock()
    return DepositBank(agent, env)


def test_find_deposits_from_env(role):
    # Given
    env = role.env

    # When
    found = role.find_deposits()

    # Then
    env.find_links.assert_called_with(role, "depositor")
    assert found == env.find_links.return_value


def test_find_depositor_returns_roles_from_env(role):
    # Given
    roles = {i: Mock() for i in range(5)}
    env = role.env
    env.roles = roles

    # When
    found = role.find_depositor(1)

    # Then
    assert found == roles[1]


# ---------------------------------------------------
# ACTION TESTS
# ----------------------------------------------------


def test_pay_interests_into_env(role):
    # Given
    env = role.env
    depositor = Mock()

    # When
    role.pay_interests(depositor, 200)

    # Then
    env.pay_interests.assert_called_with(role, depositor, 200)


def test_make_deposits_call_join_deposit_bank_from_env(role):
    # Given
    env = role.env
    depositor = Mock()

    # When
    role.make_deposits(depositor, 200)

    # Then
    env.join_deposit_bank.assert_called_with(depositor, role, 200)
