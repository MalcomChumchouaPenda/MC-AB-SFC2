import pytest
from unittest.mock import Mock
from model.base import EcoRole
from model.roles.bond_buyer import BondBuyer

# ---------------------------------------------------
# ARCHITECTURE TESTS
# ----------------------------------------------------


def test_inherits_from_eco_role():
    # Assert
    assert issubclass(BondBuyer, EcoRole)


@pytest.fixture
def role():
    # Given
    agent, env = Mock(), Mock()
    return BondBuyer(agent, env)


# ---------------------------------------------------
#  PERCEPTIONS
# ----------------------------------------------------


def test_find_issuers_with_positive_bond_number(role, make_dlist):
    # Given
    eligible = Mock(bond_number=1)
    ineligible = Mock(bond_number=0)
    issuers = make_dlist([eligible, ineligible])
    env = role.env
    env.find_all_roles = Mock(return_value=issuers)

    # When
    result = role.find_issuers()

    # Then
    env.find_all_roles.assert_called_with("bond_issuer")
    assert list(result) == [eligible]


# ---------------------------------------------------
#  ACTIONS
# ----------------------------------------------------


def test_buy_bonds(role):
    # Given
    issuer = Mock()
    env = role.env

    # When
    role.buy_bonds(issuer, 2)

    # Then
    env.buy_bonds.assert_called_with(role, issuer, 2)
