import pytest
from unittest.mock import Mock
from model.roles.bond_issuer import BondIssuer

# ---------------------------------------------------
# ARCHITECTURE TESTS
# ----------------------------------------------------


def test_is_eco_role():
    # Given
    from model.base import EcoRole

    # Assert
    assert issubclass(BondIssuer, EcoRole)


@pytest.fixture
def issuer_before_setup():
    # Given
    model = Mock()
    issuer = BondIssuer(model)
    return issuer


def test_has_default_debt_ratio(issuer_before_setup):
    # Given
    issuer = issuer_before_setup

    # When
    issuer.setup()

    # Then
    assert issuer.debt_ratio == 0.0


def test_has_default_bond_number(issuer_before_setup):
    # Given
    issuer = issuer_before_setup

    # When
    issuer.setup()

    # Then
    assert issuer.bond_number == 0.0


def test_has_default_bond_value(issuer_before_setup):
    # Given
    issuer = issuer_before_setup

    # When
    issuer.setup()

    # Then
    assert issuer.bond_value == 0.0



# ---------------------------------------------------
# PERCEPTIONS
# ----------------------------------------------------


@pytest.fixture
def issuer_with_space(issuer_before_setup):
    # Given
    space = Mock()
    issuer = issuer_before_setup
    issuer.space = space
    return issuer, space




def test_find_bonds(issuer_with_space):
    # Given
    issuer, space = issuer_with_space

    # When
    result = issuer.find_bonds()

    # Then
    space.find_bonds.assert_called_once_with(issuer)
    assert result == space.find_bonds.return_value


# ---------------------------------------------------
# ACTIONS
# ----------------------------------------------------


def test_repay_bond_use_space_method(issuer_with_space):
    # Given
    lender = Mock()
    issuer, space = issuer_with_space

    # When
    issuer.repay_bond(lender, 100, 10)

    # Then
    space.repay_bond.assert_called_with(issuer, lender, 100, 10)
