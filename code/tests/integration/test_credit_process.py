import pytest
from unittest.mock import Mock
from mc_ab_sfc.agents import BankAgent, FirmAgent
from mc_ab_sfc.spaces import CreditMarket


@pytest.fixture
def model():
    # Given
    model = Mock()
    return model


@pytest.fixture
def bank(model):
    # Given
    bank = BankAgent(model)
    return bank


@pytest.fixture
def firm(model):
    # Given
    firm = FirmAgent(model)
    firm.desired_loans = 500
    return firm


def test_firm_request_loans(model, firm, bank):
    # Given
    credit_market = CreditMarket(model)
    borrower = credit_market.add_borrower(firm)
    lender = credit_market.add_lender(bank)

    # When
    firm.request_loan()

    # Then
    assert lender.loan_applicants == [borrower]
