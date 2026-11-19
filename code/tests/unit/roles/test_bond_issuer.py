import pytest
from unittest.mock import Mock
from model.roles.bond_issuer import BondIssuer

# ---------------------------------------------------
# ARCHITECTURE
# ----------------------------------------------------


def test_inherits_from_eco_role():
    # Given
    from model.extensions import EcoRole

    # Then
    assert issubclass(BondIssuer, EcoRole)


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
    return BondIssuer(agent, env)


def test_initializes_debt_ratio(role):
    # Then
    assert role.debt_ratio == 0.0


def test_initializes_bond_number(role):
    # Then
    assert role.bond_number == 0.0


def test_initializes_bond_value(role):
    # Then
    assert role.bond_value == 0.0


# ---------------------------------------------------
# PERCEPTIONS
# ----------------------------------------------------


def test_get_discount_rate(role, env):
    # Given
    env.discount_rate = 0.05

    # When
    result = role.get_discount_rate()

    # Then
    assert result == 0.05


def test_find_bonds_returns_buyer_and_amount(role, env):
    # Given
    bond = Mock()
    env.links.return_value = [bond]

    # When
    result = role.find_bonds()

    # Then
    env.links.assert_called_with(role)
    assert result == [bond]


# ---------------------------------------------------
# ACTIONS
# ----------------------------------------------------


def test_repay_bond_use_env_method(role, env):
    # Given
    buyer = Mock()

    # When
    role.repay_bonds(buyer, 100, 10)

    # Then
    env.repay_bonds.assert_called_with(buyer, role, 100, 10)
