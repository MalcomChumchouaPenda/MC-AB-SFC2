import pytest
from unittest.mock import Mock
from model.roles.monetary_authority import MonetaryAuthority

# ---------------------------------------------------
# ARCHITECTURE
# ----------------------------------------------------


def test_inherits_from_eco_role():
    # Given
    from model.base import EcoRole

    # When
    is_derived = issubclass(MonetaryAuthority, EcoRole)

    # Then
    assert is_derived


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
