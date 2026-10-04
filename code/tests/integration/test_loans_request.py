import pytest
from model.agents.bank import Bank
from model.agents.firm import Firm
from model.spaces.credit_market import CreditMarket


@pytest.fixture
def market(fake_model):
    # Given
    model = fake_model
    market = CreditMarket(model)
    return market


@pytest.fixture
def bank(fake_model, market):
    # Given
    model = fake_model
    bank = Bank(model)
    market.place_bank(bank)
    return bank


@pytest.fixture
def firm(fake_model, market):
    # Given
    model = fake_model
    firm = Firm(model)
    market.place_firm(firm)
    return firm


def test_creates_loan_application(firm, bank):
    # Given
    firm.wage_offer = 4
    firm.desired_rd = 100
    firm.desired_labor = 100
    firm_role = firm.roles["borrower"]

    # When
    firm.request_loans()

    # Then
    assert firm.desired_loans == 500
    assert firm_role.loan_demand == 500
    assert bank.roles["lender"].loan_applicants == [firm_role]
