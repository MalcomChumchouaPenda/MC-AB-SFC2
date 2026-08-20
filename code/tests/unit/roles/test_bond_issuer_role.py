import pytest
from unittest.mock import Mock
from mc_ab_sfc.roles.bond_issuer import BondIssuerRole

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


def test_exposes_bond_rate(issuer):
    # Given
    government = issuer.agent
    government.bond_rate = 0.01

    # Assert
    assert issuer.bond_rate == 0.01


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


def test_issue_bonds(issuer):
    # Given
    issuer.bond_supply = 0

    # When
    issuer.issue_bonds(400)

    # Then
    assert issuer.bond_supply == 400


def test_pay_bond_debt(issuer):
    # Given
    market = issuer.space

    # When
    issuer.pay_bond_debt()

    # Then
    market.pay_bond_debt.assert_called_with(issuer)
