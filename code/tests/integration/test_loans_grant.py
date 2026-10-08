from unittest.mock import Mock
import pytest
from model.agents.bank import Bank
from model.agents.firm import Firm
from model.spaces.monetary_union import MonetaryUnion


@pytest.fixture
def model(fake_model):
    # Given
    model = fake_model
    model.p.initial_tax_rate = 0.0
    model.p.initial_discount_rate = 0.0
    model.p.iota_l = 0
    model.p.chi = 0.0
    model.p.mu1 = 1.0
    return model


@pytest.fixture
def union(model):
    # Given
    union = MonetaryUnion(model)
    union.create_markets()
    union.create_countries(1)
    country = union.spaces["country_0"]
    country.discount_rate = 0.05
    return union


@pytest.fixture
def markets(union):
    # Given
    country = union.spaces["country_0"]
    credit_market = union.spaces["credit_market"]
    deposit_market = country.spaces["deposit_market"]
    return [credit_market, deposit_market]


@pytest.fixture
def bank(model, union):
    # Given
    bank = Bank(model)
    union.add_bank(bank)
    bank.account["equities"] = -100
    return bank


@pytest.fixture
def firm(model, union):
    # Given
    firm = Firm(model)
    union.add_firm(firm)
    firm.account["equities"] = -100
    return firm


@pytest.fixture
def firm_with_loan_demand(firm, bank):
    # Given
    amount = 50
    borrower = firm.roles["borrower"]
    borrower.loan_demand = amount
    lender = bank.roles["lender"]
    lender.loan_applicants = [borrower]
    return firm, amount


def test_increases_firm_loans(firm_with_loan_demand, bank):
    # Given
    firm, amount = firm_with_loan_demand

    # When
    bank.grant_loans()

    # Then
    assert bank.account["loans"] == amount
    assert firm.account["loans"] == -amount


def test_increases_firm_deposits(firm_with_loan_demand, bank):
    # Given
    firm, amount = firm_with_loan_demand

    # When
    bank.grant_loans()

    # Then
    assert firm.account["deposits"] == amount
    assert bank.account["deposits"] == -amount


def test_creates_loan_as_link(firm_with_loan_demand, bank, markets):
    # Given
    firm, amount = firm_with_loan_demand
    borrower_role = firm.roles["borrower"]
    lender_role = bank.roles["lender"]

    # When
    bank.grant_loans()

    # Then
    assert markets[0].graph[lender_role][borrower_role]["amount"] == amount
    assert markets[0].graph[lender_role][borrower_role]["rate"] == 0.05


def test_creates_deposit_as_link(firm_with_loan_demand, bank, markets):
    # Given
    firm, amount = firm_with_loan_demand
    borrower_role = firm.roles["country_0_depositor"]
    lender_role = bank.roles["deposit_bank"]

    # When
    bank.grant_loans()

    # Then
    assert markets[1].graph[lender_role][borrower_role]["amount"] == amount
