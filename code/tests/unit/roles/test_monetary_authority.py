import pytest
from unittest.mock import Mock
from model.base import EcoRole
from model.roles.monetary_authority import MonetaryAuthority

# ---------------------------------------------------
# ARCHITECTURE TESTS
# ----------------------------------------------------


def test_inherits_from_eco_role():
    # Assert
    assert issubclass(MonetaryAuthority, EcoRole)


@pytest.fixture
def role():
    # Given
    agent, env = Mock(), Mock()
    return MonetaryAuthority(agent, env)


def test_has_discount_rate_prop(role):
    # Assert
    assert role.discount_rate == 0.0


# ---------------------------------------------------
# PERCEPTION TESTS
# ----------------------------------------------------


# ---------------------------------------------------
# ACTIONS TESTS
# ----------------------------------------------------


def test_transfer_profits_with_env(role):
    # Given
    env = role.env

    # When
    role.transfer_profit(200)

    # Then
    env.transfer_central_bank_profits.assert_called_with(200)
