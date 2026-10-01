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
    union.build_space()
    return union


@pytest.fixture
def country(union):
    # Given
    country = union.spaces["country_0"]
    country.monetary_authority = Mock()
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
    banks = []
    model = fake_model
    for _ in range(2):
        bank = Bank(model)
        banks.append(bank)
        country.add_company(bank, "B")
    return banks


@pytest.fixture
def firm(fake_model):
    # Given
    model = fake_model
    firm = Firm(model)
    return firm


@pytest.fixture
def firm_with_deposit_bank(firm, banks, markets):
    # Given
    supplier = markets[1].add_depositor(firm)
    deposit_bank = markets[1].add_deposit_bank(banks[1])
    markets[1].join_deposit_bank(supplier, deposit_bank, amount=100)
    return firm, banks[1]


@pytest.fixture
def bank_with_loan(firm, banks, markets):
    # Given
    amount, rate = 50, 0.1
    borrower = markets[0].add_borrower(firm)
    lender = markets[0].add_lender(banks[0])
    markets[0].grant_loan(lender, borrower, amount, rate)
    return banks[0], amount, rate


def test_increases_loan_interests(firm_with_deposit_bank, bank_with_loan):
    # Given
    firm, _ = firm_with_deposit_bank
    bank, amount, rate = bank_with_loan
    interests = amount * rate

    # When
    firm.repay_loans()

    # Then
    assert bank.account["loan_interests"] == interests
    assert firm.account["loan_interests"] == -interests


def test_decreases_loans_as_stock(firm_with_deposit_bank, bank_with_loan):
    # Given
    bank, *_ = bank_with_loan
    firm, _ = firm_with_deposit_bank

    # When
    firm.repay_loans()

    # Then
    assert firm.account["loans"] == 0
    assert bank.account["loans"] == 0


def test_decreases_loan_as_link(markets, firm_with_deposit_bank, bank_with_loan):
    # Given
    bank, *_ = bank_with_loan
    firm, _ = firm_with_deposit_bank
    firm_role = firm.roles["borrower"]
    bank_role = bank.roles["lender"]

    # When
    firm.repay_loans()

    # Then
    assert markets[0].graph[firm_role][bank_role]["amount"] == 0


def test_decreases_firm_cash(firm_with_deposit_bank, bank_with_loan):
    # Given
    bank, amount, rate = bank_with_loan
    repayment = amount * (1 + rate)
    firm, _ = firm_with_deposit_bank
    firm_cash = firm.account["cash"]
    bank_cash = bank.account["cash"]

    # When
    firm.repay_loans()

    # Then
    assert firm.account["cash"] == pytest.approx(firm_cash - repayment)
    assert bank.account["cash"] == pytest.approx(bank_cash + repayment)
