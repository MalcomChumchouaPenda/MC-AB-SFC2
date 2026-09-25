import pytest
from unittest.mock import Mock
from model.base import EcoRole
from model.roles.deposit_bank import DepositBank

# ---------------------------------------------------
# ARCHITECTURE TESTS
# ----------------------------------------------------


def test_is_eco_role():
    # Assert
    assert issubclass(DepositBank, EcoRole)


@pytest.fixture
def role():
    # Given
    agent, env = Mock(), Mock()
    return DepositBank(agent, env)


def test_has_defaulted(role):
    # Assert
    assert role.defaulted is False


# ---------------------------------------------------
# PERCEPTION TESTS
# ----------------------------------------------------


def test_find_deposits_from_env(role):
    # Given
    env = role.env

    # When
    found = role.find_deposits()

    # Then
    env.find_links.assert_called_with(role, "depositor")
    assert found == env.find_links.return_value


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
