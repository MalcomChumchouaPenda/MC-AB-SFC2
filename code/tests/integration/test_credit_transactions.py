import math
import pytest
from unittest.mock import Mock
from mc_ab_sfc.agents import BankAgent, FirmAgent
from mc_ab_sfc.spaces import CreditMarket, BankSystem


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
def bank_system(model):
    # Given
    return BankSystem(model)


@pytest.fixture
def credit_market(model):
    # Given
    return CreditMarket(model)


@pytest.fixture
def central_bank(bank_system):
    # Given
    agent = Mock(discount_rate=0.05, roles={})
    bank_system.add_central_bank(agent)
    return agent


@pytest.fixture
def bank(model, central_bank, bank_system, credit_market):
    # Given
    bank = BankAgent(model)
    central_role = central_bank.roles["central_bank"]
    bank_role = bank_system.add_commercial_bank(bank)
    bank_system.assign_central_bank(bank_role, central_role)
    credit_market.add_lender(bank)
    return bank


@pytest.fixture
def firm(model, credit_market):
    # Given
    firm = FirmAgent(model)
    firm.desired_loans = 500
    credit_market.add_borrower(firm)
    return firm


def test_firm_request_loans(firm, bank):
    # Given
    borrower = firm.roles["borrower"]
    lender = bank.roles["lender"]

    # When
    firm.request_loan()

    # Then
    assert lender.loan_applicants == [borrower]


def test_bank_evaluates_credit_request(firm, bank):
    # Given
    firm.equity = 100
    firm.desired_loans = 200
    borrower = firm.roles["borrower"]

    # When
    firm.request_loan()
    probability = bank.calc_loan_probability(borrower)
    rate = bank.calc_loan_rate(borrower)

    # Then
    assert probability == pytest.approx(math.exp(-2))
    assert rate == pytest.approx(0.15)


def test_bank_grant_loans(firm, bank):
    # Given
    firm.equity = 500
    firm.loans = 0
    firm.deposits = 200
    firm.desired_loans = 1000
    bank.equity = 7500
    bank.loans = 0
    bank.deposits = 1000

    # When
    firm.request_loan()
    bank.update_credit_capacity()
    bank.grant_loans()

    # Then
    assert bank.loans > 0
    assert firm.loans == bank.loans
    assert firm.deposits > 200
