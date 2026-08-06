import pytest
from unittest.mock import Mock
from mc_ab_sfc.roles import DepositProviderRole

# ---------------------------------------------------
# ARCHITECTURAL TESTS
# ----------------------------------------------------


def test_is_ecorole():
    # Given
    from mc_ab_sfc.base import EcoRole

    # Assert
    assert issubclass(DepositProviderRole, EcoRole)


# ---------------------------------------------------
# BEHAVIORAL TESTS
# ----------------------------------------------------


@pytest.fixture
def deposit_provider():
    # Given
    space = Mock()
    owner = Mock(id=1)
    return DepositProviderRole(owner, space)


def test_get_deposit_rate(deposit_provider):
    # Given
    bank = deposit_provider.owner
    bank.deposit_rate = 0.05

    # When
    deposit_rate = deposit_provider.get_deposit_rate()

    # Then
    assert deposit_rate == 0.05
