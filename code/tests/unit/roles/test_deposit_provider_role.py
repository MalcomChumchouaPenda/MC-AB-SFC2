import pytest
from unittest.mock import Mock
from mc_ab_sfc.roles import DepositBankRole

# ---------------------------------------------------
# ARCHITECTURAL TESTS
# ----------------------------------------------------


def test_is_ecorole():
    # Given
    from mc_ab_sfc.base import EcoRole

    # Assert
    assert issubclass(DepositBankRole, EcoRole)


# ---------------------------------------------------
# BEHAVIORAL TESTS
# ----------------------------------------------------


@pytest.fixture
def deposit_bank():
    # Given
    space = Mock()
    owner = Mock(id=1)
    return DepositBankRole(owner, space)


def test_get_deposit_rate(deposit_bank):
    # Given
    bank = deposit_bank.owner
    bank.deposit_rate = 0.05

    # When
    deposit_rate = deposit_bank.get_deposit_rate()

    # Then
    assert deposit_rate == 0.05
