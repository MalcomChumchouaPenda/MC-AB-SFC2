import pytest
from unittest.mock import Mock
from mc_ab_sfc.agents import BankAgent

# ---------------------------------------------------
# ARCHITECTURAL TESTS
# ----------------------------------------------------


def test_is_ecoagent():
    # Given
    from mc_ab_sfc.base import EcoAgent

    # Assert
    assert issubclass(BankAgent, EcoAgent)


@pytest.fixture
def bank():
    # Given
    model = Mock()
    return BankAgent(model)


# ---------------------------------------------------
# BEHAVIORS TESTS
# ----------------------------------------------------


def test_update_deposit_rate_as_fraction_of_discount_rate(bank):
    # Given
    bank_role = Mock()
    bank_role.get_discount_rate.return_value = 0.05
    bank.roles["commercial_bank"] = bank_role
    bank.p.zeta = 0.8

    # When
    bank.update_deposit_rate()

    # Then
    assert bank.deposit_rate == pytest.approx(0.04)


def test_pay_deposit_interest_delegates_to_role(bank):
    # Given
    bank_role = Mock()
    bank.roles["deposit_bank"] = bank_role

    # When
    bank.pay_deposit_interest()

    # Then
    bank_role.pay_deposit_interest.assert_called_once()
