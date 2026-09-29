from unittest.mock import Mock
import pytest
from model.agents.bank import Bank
from model.agents.firm import Firm
from model.spaces.monetary_union import MonetaryUnion


@pytest.fixture
def union(fake_model):
    # Given
    model = fake_model
    model.p.K = 1
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
def banks(fake_model, country):
    # Given
    model = fake_model
    model.p.iota_l = 0
    model.p.chi = 0.0
    model.p.mu1 = 1.0
    banks = []
    for _ in range(2):
        bank = Bank(model)
        banks.append(bank)
        country.add_company(bank, "B")
        bank.account["equities"] = 100
    return banks


@pytest.fixture
def firm(fake_model):
    # Given
    model = fake_model
    firm = Firm(model)
    return firm


@pytest.fixture
def firm_with_deposit_demander(firm, banks, markets):
    # Given
    deposit_supplier = markets[1].add_supplier(firm)
    deposit_demander = markets[1].add_demander(banks[1])
    markets[1].join_bank(deposit_supplier, deposit_demander)
    return firm, banks[1]


@pytest.fixture
def firm_with_loan_demand(firm_with_deposit_demander, markets):
    # Given
    amount = 50
    firm, _ = firm_with_deposit_demander
    borrower = markets[0].add_borrower(firm)
    borrower.loan_demand = amount
    borrower.net_worth = 100
    return firm, amount


@pytest.fixture
def bank_with_loan_demand(firm_with_loan_demand, banks, markets):
    # Given
    firm, amount = firm_with_loan_demand
    borrower = firm.roles["borrower"]
    lender = markets[0].add_lender(banks[0])
    lender.loan_applicants = [borrower]
    return banks[0], amount


def test_increases_firm_loans(firm, bank_with_loan_demand):
    # Given
    bank, amount = bank_with_loan_demand

    # When
    bank.grant_loans()

    # Then
    assert bank.account["loans"] == amount
    assert firm.account["loans"] == -amount


def test_increases_firm_deposits(firm_with_deposit_demander, bank_with_loan_demand):
    # Given
    firm, deposit_demander = firm_with_deposit_demander
    credit_bank, amount = bank_with_loan_demand

    # When
    credit_bank.grant_loans()

    # Then
    assert firm.account["deposits"] == amount
    assert deposit_demander.account["deposits"] == -amount


def test_transfers_cash_between_banks(firm_with_deposit_demander, bank_with_loan_demand):
    # Given
    _, deposit_demander = firm_with_deposit_demander
    credit_bank, amount = bank_with_loan_demand

    # When
    credit_bank.grant_loans()

    # Then
    assert credit_bank.account["cash"] == -amount
    assert deposit_demander.account["cash"] == amount


def test_creates_loan_as_link(firm_with_deposit_demander, bank_with_loan_demand, markets):
    # Given
    bank, amount = bank_with_loan_demand
    firm, _ = firm_with_deposit_demander
    firm_role = firm.roles["borrower"]
    bank_role = bank.roles["lender"]

    # When
    bank.grant_loans()

    # Then
    assert markets[0].graph[bank_role][firm_role]["amount"] == amount
    assert markets[0].graph[bank_role][firm_role]["rate"] == 0.05
