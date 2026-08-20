import pytest
from unittest.mock import Mock
from mc_ab_sfc.roles.bond_buyer import BondBuyerRole

# ---------------------------------------------------
# ARCHITECTURE TESTS
# ----------------------------------------------------


def test_is_eco_role():
    # Given
    from mc_ab_sfc.base import EcoRole

    # Assert
    assert issubclass(BondBuyerRole, EcoRole)


# ---------------------------------------------------
# BEHAVIORAL TESTS
# ----------------------------------------------------


@pytest.fixture
def buyer():
    # Given
    market = Mock()
    agent = Mock(id=1)
    return BondBuyerRole(agent, market)


def test_get_bond_issuers(buyer):
    # Given
    issuers = [Mock() for _ in range(2)]
    market = buyer.space
    market.get_bond_issuers.return_value = issuers

    # When
    result = buyer.get_bond_issuers()

    # Then
    market.get_bond_issuers.assert_called_once_with()
    assert result == issuers


def test_buy_bonds(buyer):
    # Given
    market = buyer.space
    bond_issuer = Mock()

    # When
    buyer.buy_bonds(bond_issuer, 100)

    # Then
    market.buy_bonds.assert_called_with(buyer, bond_issuer, 100)
