import pytest
from model.agents.bank import Bank
from model.agents.firm import Firm
from model.spaces.credit_market import CreditMarket


@pytest.fixture
def model(fake_model):
    # Given
    model = fake_model
    return model


@pytest.fixture
def market(model):
    # Given
    market = CreditMarket(model)
    return market


@pytest.fixture
def bank(model, market):
    # Given
    bank = Bank(model)
    market.add_bank(bank)
    return bank


@pytest.fixture
def firm(model, market):
    # Given
    firm = Firm(model)
    market.add_firm(firm)
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
