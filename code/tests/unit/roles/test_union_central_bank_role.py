import pytest
from unittest.mock import Mock
from mc_ab_sfc.roles.central_bank import UnionCentralBankRole

# ---------------------------------------------------
# ARCHITECTURE TESTS
# ----------------------------------------------------


def test_is_eco_role():
    # Given
    from mc_ab_sfc.base import EcoRole

    # Assert
    assert issubclass(UnionCentralBankRole, EcoRole)


@pytest.fixture
def role():
    # Given
    space = Mock()
    agent = Mock(id=1)
    return UnionCentralBankRole(agent, space)


def test_exposes_discount_rate(role):
    # Given
    union = role.space
    union.discount_rate = 0.05

    # Assert
    assert role.discount_rate == 0.05


def test_change_discount_rate(role):
    # Given
    union = role.space
    union.discount_rate = 0.04

    # When
    role.discount_rate = 0.05

    # Then
    assert union.discount_rate == 0.05


# ---------------------------------------------------
# BEHAVIORAL TESTS
# ----------------------------------------------------


def test_get_average_inflation(role):
    # Given
    union = role.space
    union.average_inflation = 0.05

    # When
    average_inflation = role.get_average_inflation()

    # Assert
    assert average_inflation == 0.05
