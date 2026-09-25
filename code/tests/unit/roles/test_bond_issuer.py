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
def role_with_env():
    # Given
    agent, env = Mock(), Mock()
    role = BondIssuer(agent, env)
    return role, env


def test_has_default_debt_ratio(role_with_env):
    # Given
    role, _ = role_with_env

    # Assert
    assert role.debt_ratio == 0.0


def test_has_default_bond_number(role_with_env):
    # Given
    role, _ = role_with_env

    # Assert
    assert role.bond_number == 0.0


def test_has_default_bond_value(role_with_env):
    # Given
    role, _ = role_with_env

    # Assert
    assert role.bond_value == 0.0


# ---------------------------------------------------
# PERCEPTIONS
# ----------------------------------------------------


def test_get_discount_rate(role_with_env):
    # Given
    role, env = role_with_env
    env.discount_rate = 0.05

    # When
    result = role.get_discount_rate()

    # Then
    assert result == 0.05


def test_find_bonds_returns_buyer_and_amount(role_with_env):
    # Given
    role, env = role_with_env
    bond_item = {"buyer": Mock(), "amount": 100}
    env.find_links.return_value = [bond_item]

    # When
    result = role.find_bonds()

    # Then
    env.find_links.assert_called_with(role, neighbor_name="buyer")
    assert result == [bond_item]


# ---------------------------------------------------
# ACTIONS
# ----------------------------------------------------


def test_repay_bond_use_env_method(role_with_env):
    # Given
    buyer = Mock()
    role, env = role_with_env

    # When
    role.repay_bonds(buyer, 100, 10)

    # Then
    env.repay_bonds.assert_called_with(buyer, role, 100, 10)
