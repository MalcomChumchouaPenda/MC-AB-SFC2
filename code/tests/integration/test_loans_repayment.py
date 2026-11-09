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
    union.add_agents([bank])
    return bank


@pytest.fixture
def firm(model, union):
    # Given
    firm = Firm(model)
    firm.country_pos = 0
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
def before_repayment(firm, bank, markets):
    # Given
    lender = bank.roles["lender"]
    borrower = firm.roles["borrower"]
    deposit_bank = bank.roles["deposit_bank"]
    depositor = firm.roles["country_0_depositor"]
    markets[0].grant_loan(lender, borrower, 50, 0.1)
    markets[1].join_deposit_bank(depositor, deposit_bank, amount=100)


@pytest.mark.usefixtures("before_repayment")
def test_increases_loan_interests(firm, bank):
    # When
    firm.repay_loans()

    # Then
    assert bank.account["loan_interests"] == 50 * 0.1
    assert firm.account["loan_interests"] == -50 * 0.1


@pytest.mark.usefixtures("before_repayment")
def test_decreases_loans_as_stock(firm, bank):
    # When
    firm.repay_loans()

    # Then
    assert firm.account["loans"] == 0
    assert bank.account["loans"] == 0


@pytest.mark.usefixtures("before_repayment")
def test_decreases_loan_as_link(markets, firm, bank):
    # Given
    firm_role = firm.roles["borrower"]
    bank_role = bank.roles["lender"]

    # When
    firm.repay_loans()

    # Then
    assert markets[0].graph[firm_role][bank_role]["amount"] == 0


@pytest.mark.usefixtures("before_repayment")
def test_decreases_firm_cash(firm, bank):
    # Given
    firm.account["cash"] = 200
    bank.account["cash"] = 200
    repayment = 50 * (1 + 0.1)

    # When
    firm.repay_loans()

    # Then
    assert firm.account["cash"] == pytest.approx(200 - repayment)
    assert bank.account["cash"] == pytest.approx(200 + repayment)
