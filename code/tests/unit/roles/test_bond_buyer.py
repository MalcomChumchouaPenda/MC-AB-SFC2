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


def test_find_issuers_with_positive_bond_number(role_with_env, make_dlist):
    # Given
    role, env = role_with_env
    eligible = Mock(bond_number=1)
    ineligible = Mock(bond_number=0)
    issuers = make_dlist([eligible, ineligible])
    env.find_all_roles = Mock(return_value=issuers)

    # When
    result = role.find_issuers()

    # Then
    env.find_all_roles.assert_called_with("bond_issuer")
    assert list(result) == [eligible]


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
