import pytest
from unittest.mock import Mock
from mc_ab_sfc.roles import DepositBankRole

# ---------------------------------------------------
# ARCHITECTURE TESTS
# ----------------------------------------------------


def test_is_eco_role():
    # Given
    from mc_ab_sfc.base import EcoRole

    # Assert
    assert issubclass(DepositBankRole, EcoRole)


@pytest.fixture
def deposit_bank():
    # Given
    space = Mock()
    agent = Mock(id=1)
    return DepositBankRole(agent, space)


def test_exposes_deposit_rate(deposit_bank):
    # Given
    bank = deposit_bank.agent
    bank.deposit_rate = 0.05

    # Assert
    assert deposit_bank.deposit_rate == 0.05


# ---------------------------------------------------
# BEHAVIORAL TESTS
# ----------------------------------------------------


def test_deposit_bank_role_delegates_payment(deposit_bank):
    # Given
    role = deposit_bank
    market = deposit_bank.space

    # When
    role.pay_deposit_interest()

    # Then
    market.pay_deposit_interest.assert_called_once_with(role)
