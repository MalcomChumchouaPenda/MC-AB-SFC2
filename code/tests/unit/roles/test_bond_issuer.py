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
def issuer_with_env(issuer_before_setup):
    # Given
    env = Mock()
    issuer = issuer_before_setup
    issuer.env = env
    return issuer, env


def test_get_discount_rate(issuer_with_env):
    # Given
    issuer, env = issuer_with_env
    env.discount_rate = 0.05

    # When
    result = issuer.get_discount_rate()

    # Then
    assert result == 0.05


def test_find_bonds(issuer_with_env):
    # Given
    issuer, env = issuer_with_env

    # When
    result = issuer.find_bonds()

    # Then
    env.find_bonds.assert_called_once_with(issuer)
    assert result == env.find_bonds.return_value


# ---------------------------------------------------
# ACTIONS
# ----------------------------------------------------


def test_repay_bond_use_env_method(issuer_with_env):
    # Given
    buyer = Mock()
    issuer, env = issuer_with_env

    # When
    issuer.repay_bonds(buyer, 100, 10)

    # Then
    env.repay_bonds.assert_called_with(buyer, issuer, 100, 10)
