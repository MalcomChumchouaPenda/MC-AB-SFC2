import pytest
from model.agents.bank import Bank
from model.agents.firm import Firm
from model.spaces.monetary_union import MonetaryUnion


@pytest.fixture
def model(fake_model):
    # Given
    model = fake_model
    model.p.country_number = 1
    model.p.initial_tax_rate = 0.0
    model.p.initial_discount_rate = 0.0
    return model


@pytest.fixture
def union(model):
    # Given
    union = MonetaryUnion(model)
    union.create_countries()
    union.create_markets()
    return union


@pytest.fixture
def bank(model, union):
    # Given
    bank = Bank(model)
    bank.country_pos = 0
    union.add_agents([bank])
    return bank


@pytest.fixture
def firm(model, union):
    # Given
    firm = Firm(model)
    union.add_agents([firm])
    return firm


def test_creates_loan_application(firm, bank):
    # Given
    firm.roles["employer"].wage = 4
    firm.desired_rd = 100
    firm.desired_labor = 100
    firm_role = firm.roles["borrower"]

    # When
    firm.request_loans()

    # Then
    assert firm.desired_loans == 500
    assert firm_role.loan_demand == 500
    assert bank.roles["lender"].loan_applicants == [firm_role]
