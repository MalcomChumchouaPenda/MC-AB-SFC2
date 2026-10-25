from unittest.mock import Mock
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
    union.create_markets()
    union.create_countries()
    return union


@pytest.fixture
def bank(model, union):
    # Given
    bank = Bank(model)
    bank.country_pos = 0
    union.add_bank(bank)
    return bank


@pytest.fixture
def firm(model, union):
    # Given
    firm = Firm(model)
    union.add_agents([firm])
    return firm


@pytest.fixture
def markets(union):
    # Given
    country = union.spaces["country_0"]
    credit_market = union.spaces["credit_market"]
    deposit_market = country.spaces["deposit_market"]
    return [credit_market, deposit_market]


@pytest.fixture
def firm_with_deposit(firm, bank, markets):
    # Given
    amount = 100
    deposit_bank = bank.roles["deposit_bank"]
    depositor = firm.roles["country_0_depositor"]
    markets[1].join_deposit_bank(depositor, deposit_bank, amount=amount)
    return firm, amount


@pytest.fixture
def bank_with_loan(firm, bank, markets):
    # Given
    amount, rate = 50, 0.1
    lender = bank.roles["lender"]
    borrower = firm.roles["borrower"]
    markets[0].grant_loan(lender, borrower, amount, rate)
    return bank, amount, rate


def test_increases_loan_interests(firm_with_deposit, bank_with_loan):
    # Given
    firm, _ = firm_with_deposit
    bank, amount, rate = bank_with_loan
    interests = amount * rate

    # When
    firm.repay_loans()

    # Then
    assert bank.account["loan_interests"] == interests
    assert firm.account["loan_interests"] == -interests


def test_decreases_loans_as_stock(firm_with_deposit, bank_with_loan):
    # Given
    bank, *_ = bank_with_loan
    firm, _ = firm_with_deposit

    # When
    firm.repay_loans()

    # Then
    assert firm.account["loans"] == 0
    assert bank.account["loans"] == 0


def test_decreases_loan_as_link(markets, firm_with_deposit, bank_with_loan):
    # Given
    bank, *_ = bank_with_loan
    firm, _ = firm_with_deposit
    firm_role = firm.roles["borrower"]
    bank_role = bank.roles["lender"]

    # When
    firm.repay_loans()

    # Then
    assert markets[0].graph[firm_role][bank_role]["amount"] == 0


def test_decreases_firm_cash(firm_with_deposit, bank_with_loan):
    # Given
    bank, amount, rate = bank_with_loan
    repayment = amount * (1 + rate)
    firm, _ = firm_with_deposit
    firm_cash = firm.account["cash"]
    bank_cash = bank.account["cash"]

    # When
    firm.repay_loans()

    # Then
    assert firm.account["cash"] == pytest.approx(firm_cash - repayment)
    assert bank.account["cash"] == pytest.approx(bank_cash + repayment)
