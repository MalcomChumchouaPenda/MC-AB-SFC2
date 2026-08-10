import math
import pytest
from unittest.mock import Mock
from mc_ab_sfc.agents import BankAgent, FirmAgent, CentralBankAgent
from mc_ab_sfc.spaces import CreditMarket, MonetaryUnionSpace


@pytest.fixture
def model():
    # Given
    model = Mock()
    model.p.iota_l = 1
    model.p.chi = 0.05
    model.p.mu1 = 0.05
    random = model.nprandom
    random.choice.return_value = 1
    return model


@pytest.fixture
def central_bank(model):
    # Given
    central_bank = CentralBankAgent(model)
    central_bank.discount_rate = 0.05
    return central_bank


@pytest.fixture
def bank(model):
    # Given
    bank = BankAgent(model)
    return bank


@pytest.fixture
def firm(model):
    # Given
    firm = FirmAgent(model)
    return firm


@pytest.fixture
def union(model, central_bank):
    # Given
    return MonetaryUnionSpace(model, central_bank)


@pytest.fixture
def credit_market(model):
    # Given
    return CreditMarket(model)


def test_firm_request_loans(firm, bank, credit_market, union):
    # Given
    firm.desired_loans = 500
    borrower = credit_market.add_borrower(firm)
    lender = credit_market.add_lender(bank)
    union.add_commercial_bank(bank)

    # When
    firm.request_loan()

    # Then
    assert lender.loan_applicants == [borrower]


def test_bank_evaluates_credit_request(firm, bank, credit_market, union):
    # Given
    firm.equity = 100
    firm.desired_loans = 200
    borrower = credit_market.add_borrower(firm)
    union.add_commercial_bank(bank)

    # When
    firm.request_loan()
    probability = bank.calc_loan_probability(borrower)
    rate = bank.calc_loan_rate(borrower)

    # Then
    assert probability == pytest.approx(math.exp(-2))
    assert rate == pytest.approx(0.15)


def test_bank_grant_loans(firm, bank, credit_market, union):
    # Given
    firm.equity = 500
    firm.loans = 0
    firm.deposits = 200
    firm.desired_loans = 1000
    bank.equity = 7500
    bank.loans = 0
    bank.deposits = 1000
    credit_market.add_borrower(firm)
    credit_market.add_lender(bank)
    union.add_commercial_bank(bank)

    # When
    firm.request_loan()
    bank.update_credit_capacity()
    bank.grant_loans()

    # Then
    assert bank.loans > 0
    assert firm.loans == bank.loans
    assert firm.deposits > 200
