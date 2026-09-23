import pytest
from unittest.mock import Mock
from model.roles.bond_buyer import BondBuyer

# ---------------------------------------------------
# ARCHITECTURE TESTS
# ----------------------------------------------------


def test_is_eco_role():
    # Given
    from model.base import EcoRole

    # Assert
    assert issubclass(BondBuyer, EcoRole)


@pytest.fixture
def role_with_env():
    # Given
    agent, env = Mock(), Mock()
    role = BondBuyer(agent, env)
    return role, env


# ---------------------------------------------------
#  PERCEPTIONS
# ----------------------------------------------------


def test_find_issuers(role_with_env):
    # Given
    role, env = role_with_env

    # When
    result = role.find_issuers()

    # Then
    env.find_issuers.assert_called_once_with()
    assert result == env.find_issuers.return_value


# ---------------------------------------------------
#  ACTIONS
# ----------------------------------------------------


def test_buy_bonds(role_with_env):
    # Given
    issuer = Mock()
    role, env = role_with_env

    # When
    role.buy_bonds(issuer, 2)

    # Then
    env.buy_bonds.assert_called_with(role, issuer, 2)
