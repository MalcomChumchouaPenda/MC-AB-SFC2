import pytest
from unittest.mock import Mock
from model.roles.bond_buyer import BondBuyer

# ---------------------------------------------------
# ARCHITECTURE
# ----------------------------------------------------


def test_inherits_from_eco_role():
    # Given
    from model.extensions import EcoRole

    # Then
    assert issubclass(BondBuyer, EcoRole)


@pytest.fixture
def agent():
    # Given
    return Mock()


@pytest.fixture
def env():
    # Given
    return Mock()


@pytest.fixture
def role(agent, env):
    # Given
    return BondBuyer(agent, env)


def test_initializes_defaulted(role):
    # Then
    assert role.defaulted is False


# ---------------------------------------------------
#  PERCEPTIONS
# ----------------------------------------------------


@pytest.fixture
def issuers(make_dlist):
    # Given
    eligible = Mock(bond_number=1)
    ineligible = Mock(bond_number=0)
    return make_dlist([eligible, ineligible])


def test_find_issuers_uses_env_find_method(role, env, issuers):
    # Given
    env.find_all_roles = Mock(return_value=issuers)

    # When
    role.find_issuers()

    # Then
    env.find_all_roles.assert_called_with("bond_issuer")


def test_find_issuers_returns_roles_with_positive_bond_number(role, env, issuers):
    # Given
    eligible = issuers[0]
    env.find_all_roles = Mock(return_value=issuers)

    # When
    result = role.find_issuers()

    # Then
    assert list(result) == [eligible]


# ---------------------------------------------------
#  ACTIONS
# ----------------------------------------------------


def test_buy_bonds(role, env):
    # Given
    issuer = Mock()

    # When
    role.buy_bonds(issuer, 2)

    # Then
    env.buy_bonds.assert_called_with(role, issuer, 2)
