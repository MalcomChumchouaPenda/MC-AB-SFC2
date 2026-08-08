import math
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


def test_has_default_stocks(bank):
    # Assert
    assert bank.cash == 0
    assert bank.loans == 0
    assert bank.deposits == 0


def test_has_default_flows(bank):
    # Assert
    assert bank.loan_interest == 0
    assert bank.deposit_interest == 0
    assert bank.dividends == 0


def test_has_default_prices(bank):
    # Assert
    assert bank.deposit_rate == 0


def test_has_default_credit_capacity(bank):
    # Assert
    assert bank.credit_capacity == 0


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


def test_updates_credit_capacity(bank):
    # Given
    bank.equity = 100
    bank.p.mu1 = 10

    # When
    bank.update_credit_capacity()

    # Then
    assert bank.credit_capacity == pytest.approx(1000)


def test_calc_loan_probability(bank):
    # Given
    bank.p.iota_l = 1
    borrower = Mock(loan_demand=100, target_leverage=0.5)

    # When
    probability = bank.calc_loan_probability(borrower)

    # Then
    assert probability == pytest.approx(math.exp(-0.5))


def test_calc_loan_rate(bank):
    # Given
    bank_role = Mock()
    bank_role.get_discount_rate.return_value = 0.05
    bank.roles["commercial_bank"] = bank_role
    bank.p.chi = 0.02
    borrower = Mock(target_leverage=5.0)

    # When
    rate = bank.calc_loan_rate(borrower)

    # Then
    assert rate == pytest.approx(0.02 * 5.0 + 0.05)
