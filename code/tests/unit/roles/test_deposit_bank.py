import pytest
from unittest.mock import Mock
from model.roles.deposit_bank import DepositDemander

# ---------------------------------------------------
# ARCHITECTURE
# ----------------------------------------------------


def test_inherits_from_eco_role():
    # Given
    from model.base import EcoRole

    # When
    is_derived = issubclass(DepositDemander, EcoRole)

    # Then
    assert is_derived


def test_initializes_defaulted():
    # Given
    agent, env = Mock(), Mock()

    # When
    role = DepositDemander(agent, env)

    # Then
    assert role.defaulted is False


# ---------------------------------------------------
# PERCEPTION TESTS
# ----------------------------------------------------


@pytest.fixture
def role():
    # Given
    agent, env = Mock(), Mock()
    return DepositDemander(agent, env)


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
