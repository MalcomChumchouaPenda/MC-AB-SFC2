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


@pytest.fixture
def deposit_holder():
    # Given
    space = Mock()
    agent = Mock(id=1)
    return DepositHolderRole(agent, space)


def test_has_deposit_bank_reference(deposit_holder):
    # Assert
    assert deposit_holder.deposit_bank is None


# ---------------------------------------------------
# BEHAVIORAL TESTS
# ----------------------------------------------------


def test_get_deposit_rate(deposit_holder):
    # Given
    deposit_bank = Mock()
    deposit_bank.deposit_rate = 0.02
    deposit_holder.deposit_bank = deposit_bank

    # When
    deposit_rate = deposit_holder.get_deposit_rate()

    # Then
    assert deposit_rate == 0.02
