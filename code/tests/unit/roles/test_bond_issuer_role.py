import pytest
from unittest.mock import Mock
from mc_ab_sfc.roles import BondIssuerRole

# ---------------------------------------------------
# ARCHITECTURE TESTS
# ----------------------------------------------------


def test_is_eco_role():
    # Given
    from mc_ab_sfc.base import EcoRole

    # Assert
    assert issubclass(BondIssuerRole, EcoRole)


@pytest.fixture
def issuer():
    # Given
    market = Mock()
    agent = Mock(id=1)
    return BondIssuerRole(agent, market)


def test_has_default_bond_supply(issuer):
    # Assert
    assert issuer.bond_supply == 0.0


def test_exposes_interest_rate(issuer):
    # Given
    government = issuer.agent
    government.bond_interest_rate = 0.01

    # Assert
    assert issuer.interest_rate == 0.01


def test_exposes_bonds(issuer):
    # Given
    government = issuer.agent
    government.bonds = 100

    # Assert
    assert issuer.bonds == 100


def test_exposes_gdp(issuer):
    # Given
    government = issuer.agent
    government.gdp = 150
    # Assert
    assert issuer.gdp == 150
