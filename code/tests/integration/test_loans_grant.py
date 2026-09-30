from unittest.mock import Mock
import pytest
from model.agents.bank import Bank
from model.agents.firm import Firm
from model.spaces.monetary_union import MonetaryUnion


@pytest.fixture
def model(fake_model):
    # Given
    model = fake_model
    model.p.K = 1
    model.p.iota_l = 0
    model.p.chi = 0.0
    model.p.mu1 = 1.0
    return model


@pytest.fixture
def union(model):
    # Given
    union = MonetaryUnion(model)
    return union


@pytest.fixture
def country(union):
    # Given
    country = union.spaces["country_0"]
    country.monetary_authority = Mock(discount_rate=0.05)
    return country


@pytest.fixture
def markets(union, country):
    # Given
    credit_market = union.spaces["credit_market"]
    deposit_market = country.spaces["deposit_market"]
    return [credit_market, deposit_market]


@pytest.fixture
def bank(model, country, markets):
    # Given
    bank = Bank(model)
    country.add_company(bank, "B")
    markets[0].add_lender(bank)
    markets[1].add_deposit_bank(bank)
    bank.account["equities"] = 100
    return bank


@pytest.fixture
def firm(model, markets):
    # Given
    firm = Firm(model)
    markets[0].add_borrower(firm)
    markets[1].add_depositor(firm)
    return firm


@pytest.fixture
def firm_with_loan_demand(firm, bank):
    # Given
    amount = 50
    borrower = firm.roles["borrower"]
    borrower.loan_demand = amount
    borrower.net_worth = 100
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
    firm_role = firm.roles["borrower"]
    bank_role = bank.roles["lender"]

    # When
    bank.grant_loans()

    # Then
    assert markets[0].graph[bank_role][firm_role]["amount"] == amount
    assert markets[0].graph[bank_role][firm_role]["rate"] == 0.05


def test_creates_deposit_as_link(firm_with_loan_demand, bank, markets):
    # Given
    firm, amount = firm_with_loan_demand
    firm_role = firm.roles["depositor"]
    bank_role = bank.roles["deposit_bank"]

    # When
    bank.grant_loans()

    # Then
    assert markets[1].graph[bank_role][firm_role]["amount"] == amount
