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


def test_expose_discount_rate_from_agent(role_with_env):
    # Given
    agent = Mock(discount_rate=0.02)
    role, _ = role_with_env
    role.agent = agent

    # When
    perceived = role.discount_rate

    # Then
    assert perceived == 0.02


# ---------------------------------------------------
# PERCEPTION TESTS
# ----------------------------------------------------


# ---------------------------------------------------
# ACTIONS TESTS
# ----------------------------------------------------


def test_transfer_profits_with_env(role_with_env):
    # Given
    role, env = role_with_env

    # When
    role.transfer_profit(200)

    # Then
    env.transfer_central_bank_profits.assert_called_with(200)
