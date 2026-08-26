import math
import pytest
from unittest.mock import Mock
from mc_ab_sfc.agents import Bank, Firm
from mc_ab_sfc.spaces import CreditMarket, CountrySpace


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
def bank(model):
    # Given
    bank = Bank(model)
    return bank


@pytest.fixture
def firm(model):
    # Given
    firm = Firm(model)
    return firm


@pytest.fixture
def country(model):
    # Given
    country = CountrySpace(model)
    country.discount_rate = 0.05
    return country


@pytest.fixture
def credit_market(model):
    # Given
    return CreditMarket(model)


def test_firm_request_loans(firm, bank, credit_market, country):
    # Given
    firm.desired_loans = 500
    country.central_bank_role = Mock()
    country.add_commercial_bank(bank)
    borrower = credit_market.add_borrower(firm)
    lender = credit_market.add_lender(bank)

    # When
    firm.request_loan()

    # Then
    assert lender.loan_applicants == [borrower]


def test_bank_evaluates_credit_request(firm, bank, credit_market, country):
    # Given
    firm.equity = 100
    firm.desired_loans = 200
    country.central_bank_role = Mock()
    country.add_commercial_bank(bank)
    borrower = credit_market.add_borrower(firm)

    # When
    firm.request_loan()
    probability = bank.calc_loan_probability(borrower)
    rate = bank.calc_loan_rate(borrower)

    # Then
    assert probability == pytest.approx(math.exp(-2))
    assert rate == pytest.approx(0.15)


def test_bank_grant_loans(firm, bank, credit_market, country):
    # Given
    firm.equity = 500
    firm.loans = 0
    firm.deposits = 200
    firm.desired_loans = 1000
    bank.equity = 7500
    bank.loans = 0
    bank.deposits = 1000
    country.central_bank_role = Mock()
    country.add_commercial_bank(bank)
    credit_market.add_borrower(firm)
    credit_market.add_lender(bank)

    # When
    firm.request_loan()
    bank.update_credit_capacity()
    bank.grant_loans()

    # Then
    assert bank.loans > 0
    assert firm.loans == bank.loans
    assert firm.deposits > 200
