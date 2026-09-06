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


def test_find_issuers(buyer_with_space):
    # Given
    buyer, space = buyer_with_space

    # When
    result = buyer.find_issuers()

    # Then
    space.find_issuers.assert_called_once_with()
    assert result == space.find_issuers.return_value


# ---------------------------------------------------
#  ACTIONS
# ----------------------------------------------------


@pytest.fixture
def buyer_with_space(buyer_before_setup):
    # Given
    space = Mock()
    buyer = buyer_before_setup
    buyer.space = space
    return buyer, space


def test_buy_bonds(buyer_with_space):
    # Given
    issuer = Mock()
    buyer, space = buyer_with_space

    # When
    buyer.buy_bonds(issuer, 2)

    # Then
    space.buy_bonds.assert_called_with(buyer, issuer, 2)
