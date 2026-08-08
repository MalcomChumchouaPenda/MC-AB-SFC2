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


@pytest.fixture
def bank_as_lender():
    # Given
    borrowers = [Mock(loan_demand=100) for _ in range(5)]
    lender = Mock(loan_applicants=borrowers)
    bank = BankAgent(model=Mock())
    bank.roles["lender"] = lender
    bank.calc_loan_rate = Mock(return_value=0.02)
    bank.calc_loan_probability = Mock(return_value=0.4)
    bank.update_credit_capacity = Mock()
    random = bank.model.nprandom
    random.choice.return_value = 0
    return bank


def test_grant_loans_and_processes_all_loan_applicants(bank_as_lender):
    # Given
    bank = bank_as_lender
    bank.credit_capacity = 500
    lender = bank.roles["lender"]
    applicants = lender.loan_applicants
    random = bank.model.random

    # When
    bank.grant_loans()

    # Then
    random.shuffle.assert_called_with(applicants)
    for borrower in applicants:
        bank.calc_loan_rate.assert_any_call(borrower)
        bank.calc_loan_probability.assert_any_call(borrower)


def test_grant_loans_with_computed_probability(bank_as_lender):
    # Given
    bank = bank_as_lender
    bank.credit_capacity = 500
    lender = bank.roles["lender"]
    applicants = lender.loan_applicants
    random = bank.model.nprandom
    random.choice.side_effect = iter([1, 0, 0, 0, 0])

    # When
    bank.grant_loans()

    # Then
    random.choice.assert_called_with([0, 1], p=[0.6, 0.4])
    lender.grant_loan.assert_called_with(applicants[0], 100, 0.02)
    assert lender.grant_loan.call_count == 1


def test_grant_loans_in_regards_of_credit_capacity(bank_as_lender):
    # Given
    bank = bank_as_lender
    bank.credit_capacity = 200
    lender = bank.roles["lender"]
    applicants = lender.loan_applicants
    random = bank.model.nprandom
    random.choice.return_value = 1

    # When
    bank.grant_loans()

    # Then
    lender.grant_loan.assert_any_call(applicants[0], 100, 0.02)
    lender.grant_loan.assert_any_call(applicants[1], 100, 0.02)
    assert lender.grant_loan.call_count == 2
