import pytest
from unittest.mock import Mock
from model.roles.monetary_authority import MonetaryAuthority

# ---------------------------------------------------
# ARCHITECTURE TESTS
# ----------------------------------------------------


def test_is_eco_role():
    # Given
    from model.base import EcoRole

    # Assert
    assert issubclass(MonetaryAuthority, EcoRole)


@pytest.fixture
def role_with_env():
    # Given
    agent, env = Mock(), Mock()
    role = MonetaryAuthority(agent, env)
    return role, env


def test_has_discount_rate_prop(role_with_env):
    # Given
    role, _ = role_with_env

    # Assert
    assert role.discount_rate == 0.0


# ---------------------------------------------------
# PERCEPTION TESTS
# ----------------------------------------------------


# ---------------------------------------------------
# ACTIONS TESTS
# ----------------------------------------------------


@pytest.fixture
def role_with_env():
    # Given
    agent, env = Mock(), Mock()
    role = MonetaryAuthority(agent, env)
    return role, env


def test_transfer_profits_with_env(role_with_env):
    # Given
    role, env = role_with_env

    # When
    role.transfer_profit(200)

    # Then
    env.transfer_central_bank_profits.assert_called_with(200)
