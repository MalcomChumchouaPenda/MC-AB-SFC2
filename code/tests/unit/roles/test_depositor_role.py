import pytest
from unittest.mock import Mock
from mc_ab_sfc.roles import DepositorRole

# ---------------------------------------------------
# ARCHITECTURAL TESTS
# ----------------------------------------------------


def test_is_ecorole():
    # Given
    from mc_ab_sfc.base import EcoRole

    # Assert
    assert issubclass(DepositorRole, EcoRole)


# ---------------------------------------------------
# BEHAVIORAL TESTS
# ----------------------------------------------------


@pytest.fixture
def role():
    # Given
    space = Mock()
    owner = Mock(id=1)
    return DepositorRole(owner, space)


def test_get_deposit_rate(role):
    # Given
    role.space.deposit_rate = 0.12

    # When
    deposit_rate = role.get_deposit_rate()

    # Then
    assert deposit_rate == 0.12
