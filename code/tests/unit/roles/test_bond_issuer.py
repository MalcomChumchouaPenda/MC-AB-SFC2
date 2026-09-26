import pytest
from unittest.mock import Mock
from model.base import EcoRole
from model.roles.bond_issuer import BondIssuer

# ---------------------------------------------------
# ARCHITECTURE TESTS
# ----------------------------------------------------


def test_inherits_from_eco_role():
    # Assert
    assert issubclass(BondIssuer, EcoRole)


@pytest.fixture
def role():
    # Given
    agent, env = Mock(), Mock()
    return BondIssuer(agent, env)


def test_has_default_debt_ratio(role):
    # Assert
    assert role.debt_ratio == 0.0


def test_has_default_bond_number(role):
    # Assert
    assert role.bond_number == 0.0


def test_has_default_bond_value(role):
    # Assert
    assert role.bond_value == 0.0


# ---------------------------------------------------
# PERCEPTIONS
# ----------------------------------------------------


def test_get_discount_rate(role):
    # Given
    env = role.env
    env.discount_rate = 0.05

    # When
    result = role.get_discount_rate()

    # Then
    assert result == 0.05


def test_find_bonds_returns_buyer_and_amount(role):
    # Given
    bond = Mock()
    env = role.env
    env.find_links.return_value = [bond]

    # When
    result = role.find_bonds()

    # Then
    env.find_links.assert_called_with(role, "buyer")
    assert result == [bond]


# ---------------------------------------------------
# ACTIONS
# ----------------------------------------------------


def test_repay_bond_use_env_method(role):
    # Given
    buyer = Mock()
    env = role.env

    # When
    role.repay_bonds(buyer, 100, 10)

    # Then
    env.repay_bonds.assert_called_with(buyer, role, 100, 10)
