import math
import pytest
from unittest.mock import Mock, PropertyMock
from mc_ab_sfc.agents import Bank, Firm, NationalCentralBank
from mc_ab_sfc.spaces import CreditMarket, Country


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
def bank(model, monkeypatch):
    # Given
    mock_deposits = PropertyMock()
    monkeypatch.setattr(Bank, "deposits", mock_deposits)
    bank = Bank(model)
    bank.mock_deposits = mock_deposits
    return bank


@pytest.fixture
def firm(model, monkeypatch):
    # Given
    mock_deposits = PropertyMock()
    monkeypatch.setattr(Firm, "deposits", mock_deposits)
    firm = Firm(model)
    firm.mock_deposits = mock_deposits
    return firm


@pytest.fixture
def cb(model, monkeypatch):
    # Given
    mock_rate = PropertyMock(return_value=0.05)
    monkeypatch.setattr(NationalCentralBank, "discount_rate", mock_rate)
    cb = NationalCentralBank(model)
    cb.setup()
    return cb


@pytest.fixture
def credit_market(model):
    # Given
    return CreditMarket(model)


def test_firm_request_loans(firm, bank, cb, credit_market):
    # Given
    bank.central_bank = cb
    firm.desired_loans = 500
    borrower = credit_market.add_borrower(firm)
    lender = credit_market.add_lender(bank)

    # When
    firm.request_loan()

    # Then
    assert lender.loan_applicants == [borrower]


def test_bank_evaluates_credit_request(firm, bank, cb, credit_market):
    # Given
    firm.equity = 100
    firm.desired_loans = 200
    bank.central_bank = cb
    borrower = credit_market.add_borrower(firm)

    # When
    firm.request_loan()
    probability = bank.calc_loan_probability(borrower)
    rate = bank.calc_loan_rate(borrower)

    # Then
    assert probability == pytest.approx(math.exp(-2))
    assert rate == pytest.approx(0.15)


def test_bank_grant_loans(firm, bank, cb, credit_market):
    # Given
    firm.equity = 500
    firm.loans = 0
    firm.mock_deposits.return_value = 200
    firm.desired_loans = 1000
    bank.central_bank = cb
    bank.equity = 7500
    bank.loans = 0
    bank.mock_deposits.return_value = 1000
    credit_market.add_borrower(firm)
    credit_market.add_lender(bank)

    # When
    firm.request_loan()
    bank.update_credit_capacity()
    bank.grant_loans()

    # Then
    assert bank.loans > 0
    assert firm.loans == bank.loans
    # assert firm.deposits > 200
