import pytest
from unittest.mock import Mock
from mc_ab_sfc.roles import DepositHolderRole

# ---------------------------------------------------
# ARCHITECTURAL TESTS
# ----------------------------------------------------


def test_is_ecorole():
    # Given
    from mc_ab_sfc.base import EcoRole

    # Assert
    assert issubclass(DepositHolderRole, EcoRole)


# ---------------------------------------------------
# BEHAVIORAL TESTS
# ----------------------------------------------------


@pytest.fixture
def deposit_holder():
    # Given
    space = Mock()
    owner = Mock(id=1)
    return DepositHolderRole(owner, space)


def test_get_deposit_rate(deposit_holder):
    # Given
    bank_role = Mock()
    bank_role.get_deposit_rate.return_value = 0.02
    deposit_holder.bank = bank_role

    # When
    deposit_rate = deposit_holder.get_deposit_rate()

    # Then
    assert deposit_rate == 0.02
