import pytest
from unittest.mock import Mock
from mc_ab_sfc.roles import DepositEntityRole

# ---------------------------------------------------
# ARCHITECTURAL TESTS
# ----------------------------------------------------


def test_is_ecorole():
    # Given
    from mc_ab_sfc.base import EcoRole

    # Assert
    assert issubclass(DepositEntityRole, EcoRole)


# ---------------------------------------------------
# BEHAVIORAL TESTS
# ----------------------------------------------------


@pytest.fixture
def entity():
    # Given
    space = Mock()
    owner = Mock(id=1)
    return DepositEntityRole(owner, space)


def test_get_deposit_rate(entity):
    # Given
    bank = entity.owner
    bank.deposit_rate = 0.05

    # When
    deposit_rate = entity.get_deposit_rate()

    # Then
    assert deposit_rate == 0.05
