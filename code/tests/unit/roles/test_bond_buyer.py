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
def buyer_before_setup():
    # Given
    model = Mock()
    buyer = BondBuyer(model)
    return buyer


# ---------------------------------------------------
#  PERCEPTIONS
# ----------------------------------------------------


def test_find_issuers(buyer_with_env):
    # Given
    buyer, env = buyer_with_env

    # When
    result = buyer.find_issuers()

    # Then
    env.find_issuers.assert_called_once_with()
    assert result == env.find_issuers.return_value


# ---------------------------------------------------
#  ACTIONS
# ----------------------------------------------------


@pytest.fixture
def buyer_with_env(buyer_before_setup):
    # Given
    env = Mock()
    buyer = buyer_before_setup
    buyer.env = env
    return buyer, env


def test_buy_bonds(buyer_with_env):
    # Given
    issuer = Mock()
    buyer, env = buyer_with_env

    # When
    buyer.buy_bonds(issuer, 2)

    # Then
    env.buy_bonds.assert_called_with(buyer, issuer, 2)
