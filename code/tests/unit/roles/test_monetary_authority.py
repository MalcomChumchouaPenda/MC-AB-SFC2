import pytest
from unittest.mock import Mock
from model.roles.monetary_authority import MonetaryAuthority

# ---------------------------------------------------
# ARCHITECTURE
# ----------------------------------------------------


def test_inherits_from_eco_role():
    # Given
    from model.extensions import EcoRole

    # Then
    assert issubclass(MonetaryAuthority, EcoRole)


# ---------------------------------------------------
#  PERCEPTIONS
# ----------------------------------------------------


# ---------------------------------------------------
# ACTIONS TESTS
# ----------------------------------------------------


@pytest.fixture
def agent():
    # Given
    return Mock()


@pytest.fixture
def env():
    # Given
    return Mock()


@pytest.fixture
def role(agent, env):
    # Given
    return MonetaryAuthority(agent, env)


def test_transfer_profits_with_env(role, env):
    # Given

    # When
    role.transfer_profit(200)

    # Then
    env.transfer_central_bank_profits.assert_called_with(200)


def test_set_discount_rate_into_env(role, env):
    # Given
    env.discount_rate = 0.0

    # When
    role.set_discount_rate(0.05)

    # Then
    assert env.discount_rate == 0.05
