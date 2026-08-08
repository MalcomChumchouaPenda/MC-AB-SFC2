import pytest
from unittest.mock import Mock
from mc_ab_sfc.roles import CentralBankRole

# ---------------------------------------------------
# ARCHITECTURAL TESTS
# ----------------------------------------------------


def test_is_ecorole():
    # Given
    from mc_ab_sfc.base import EcoRole

    # Assert
    assert issubclass(CentralBankRole, EcoRole)


# ---------------------------------------------------
# BEHAVIORAL TESTS
# ----------------------------------------------------


@pytest.fixture
def role():
    # Given
    space = Mock()
    agent = Mock(id=1)
    return CentralBankRole(agent, space)


def test_sets_discount_rate(role):
    # Given
    space = role.space

    # When
    role.set_discount_rate(0.05)

    # Then
    assert space.discount_rate == 0.05


def test_get_discount_rate(role):
    # Given
    space = role.space
    space.discount_rate = 0.05

    # When
    result = role.get_discount_rate()

    # Then
    assert result == 0.05
