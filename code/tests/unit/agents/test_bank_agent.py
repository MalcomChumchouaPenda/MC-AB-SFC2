import math
import pytest
from unittest.mock import Mock
from mc_ab_sfc.agents import BankAgent

# ---------------------------------------------------
# ARCHITECTURE TESTS
# ----------------------------------------------------


def test_is_eco_agent():
    # Given
    from mc_ab_sfc.base import EcoAgent

    # Assert
    assert issubclass(BankAgent, EcoAgent)


@pytest.fixture
def bank():
    # Given
    model = Mock()
    return BankAgent(model)


def test_has_default_stocks(bank):
    # Assert
    assert bank.loans == 0
    assert bank.deposits == 0
    assert bank.equity == 0
    assert bank.reserves == 0
    assert bank.cash_advances == 0


def test_has_default_flows(bank):
    # Assert
    assert bank.loan_interest == 0
    assert bank.deposit_interest == 0
    assert bank.bond_interest == 0
    assert bank.reserve_interest == 0
    assert bank.cash_advance_interest == 0
    assert bank.dividends == 0


def test_has_default_choices(bank):
    # Assert
    assert bank.deposit_rate == 0
    assert bank.taxes_payable == 0
    assert bank.dividends_payable == 0


def test_has_default_indicators(bank):
    # Assert
    assert bank.credit_capacity == 0
    assert bank.net_worth == 0
    assert bank.profit == 0


# ---------------------------------------------------
# BEHAVIORS TESTS
# ----------------------------------------------------


def test_update_deposit_rate_as_fraction_of_discount_rate(bank):
    # Given
    bank_role = Mock()
    bank_role.get_discount_rate.return_value = 0.05
    bank.roles["commercial_bank"] = bank_role
    bank.p.zeta = 0.8

    # When
    bank.update_deposit_rate()

    # Then
    assert bank.deposit_rate == pytest.approx(0.04)


def test_pay_deposit_interest_delegates_to_role(bank):
    # Given
    bank_role = Mock()
    bank.roles["deposit_bank"] = bank_role

    # When
    bank.pay_deposit_interest()

    # Then
    bank_role.pay_deposit_interest.assert_called_once()


def test_updates_credit_capacity(bank):
    # Given
    bank.equity = 100
    bank.p.mu1 = 10

    # When
    bank.update_credit_capacity()

    # Then
    assert bank.credit_capacity == pytest.approx(1000)


def test_calc_loan_probability(bank):
    # Given
    bank.p.iota_l = 1
    borrower = Mock(loan_demand=100, target_leverage=0.5)

    # When
    probability = bank.calc_loan_probability(borrower)

    # Then
    assert probability == pytest.approx(math.exp(-0.5))


def test_calc_loan_rate(bank):
    # Given
    bank_role = Mock()
    bank_role.get_discount_rate.return_value = 0.05
    bank.roles["commercial_bank"] = bank_role
    bank.p.chi = 0.02
    borrower = Mock(target_leverage=5.0)

    # When
    rate = bank.calc_loan_rate(borrower)

    # Then
    assert rate == pytest.approx(0.02 * 5.0 + 0.05)


@pytest.fixture
def bank_as_lender():
    # Given
    borrowers = [Mock(loan_demand=100) for _ in range(5)]
    lender = Mock(loan_applicants=borrowers)
    bank = BankAgent(model=Mock())
    bank.roles["lender"] = lender
    bank.calc_loan_rate = Mock(return_value=0.02)
    bank.calc_loan_probability = Mock(return_value=0.4)
    bank.update_credit_capacity = Mock()
    random = bank.model.nprandom
    random.choice.return_value = 0
    return bank


def test_grant_loans_and_processes_all_loan_applicants(bank_as_lender):
    # Given
    bank = bank_as_lender
    bank.credit_capacity = 500
    lender = bank.roles["lender"]
    applicants = lender.loan_applicants
    random = bank.model.random

    # When
    bank.grant_loans()

    # Then
    random.shuffle.assert_called_with(applicants)
    for borrower in applicants:
        bank.calc_loan_rate.assert_any_call(borrower)
        bank.calc_loan_probability.assert_any_call(borrower)


def test_grant_loans_with_computed_probability(bank_as_lender):
    # Given
    bank = bank_as_lender
    bank.credit_capacity = 500
    lender = bank.roles["lender"]
    applicants = lender.loan_applicants
    random = bank.model.nprandom
    random.choice.side_effect = iter([1, 0, 0, 0, 0])

    # When
    bank.grant_loans()

    # Then
    random.choice.assert_called_with([0, 1], p=[0.6, 0.4])
    lender.grant_loan.assert_called_with(applicants[0], 100, 0.02)
    assert lender.grant_loan.call_count == 1


def test_grant_loans_in_regards_of_credit_capacity(bank_as_lender):
    # Given
    bank = bank_as_lender
    bank.credit_capacity = 200
    lender = bank.roles["lender"]
    applicants = lender.loan_applicants
    random = bank.model.nprandom
    random.choice.return_value = 1

    # When
    bank.grant_loans()

    # Then
    lender.grant_loan.assert_any_call(applicants[0], 100, 0.02)
    lender.grant_loan.assert_any_call(applicants[1], 100, 0.02)
    assert lender.grant_loan.call_count == 2


def test_grant_loans_cleans_loan_applicants_list(bank_as_lender):
    # Given
    bank = bank_as_lender
    bank.credit_capacity = 200
    lender = bank.roles["lender"]
    random = bank.model.nprandom
    random.choice.return_value = 1

    # When
    bank.grant_loans()

    # Then
    assert len(lender.loan_applicants) == 0


@pytest.fixture
def bank_in_banksystem():
    model = Mock()
    model.p.mu2 = 0.1
    bank = BankAgent(model)
    bank.roles["commercial_bank"] = Mock()
    return bank


def test_doesnot_request_cash_advance_when_sufficient_reserves(bank_in_banksystem):
    # Given
    bank = bank_in_banksystem
    bank.deposits = 1000
    bank.reserves = 200

    # When
    bank.request_cash_advances()

    # Then
    bank_role = bank.roles["commercial_bank"]
    bank_role.request_cash_advances.assert_not_called()


def test_request_cash_advance_when_insufficient_reserves(bank_in_banksystem):
    # Given
    bank = bank_in_banksystem
    bank.deposits = 1000
    bank.reserves = 50

    # When
    bank.request_cash_advances()

    # Then
    bank_role = bank.roles["commercial_bank"]
    bank_role.request_cash_advances.assert_called_with(50)


def test_calc_bond_purchases_probability():
    # Given
    model = Mock()
    model.p.iota_b = 2
    bank = BankAgent(model)
    issuer = Mock(bonds=500, gdp=1000)

    # When
    probability = bank.calc_bond_purchases_probability(issuer)

    # Then
    assert probability == math.exp(-1)


@pytest.fixture
def bond_issuers():
    return [
        Mock(bond_supply=100, bonds=100, gdp=100),
        Mock(bond_supply=100, bonds=100, gdp=100),
    ]


@pytest.fixture
def bond_buyer(bond_issuers):
    buyer_role = Mock()
    buyer_role.get_bond_issuers.return_value = bond_issuers
    return buyer_role


@pytest.fixture
def bank_as_bondbuyer(bond_buyer):
    model = Mock()
    model.p.mu2 = 0.1
    bank = BankAgent(model)
    bank.roles["bond_buyer"] = bond_buyer
    bank.calc_bond_purchases_probability = Mock(return_value=0)
    bank.model.nprandom.choice.return_value = 1
    return bank


def test_buy_bonds_and_shuffles_all_bonds(bank_as_bondbuyer, bond_issuers):
    # Given
    bank = bank_as_bondbuyer
    bank.reserves = 300
    bank.deposits = 1000
    random = bank.model.random

    # When
    bank.invest_excess_reserves()

    # Then
    random.shuffle.assert_called_with(bond_issuers)


def test_buy_bonds_with_purchases_probability(bank_as_bondbuyer, bond_issuers):
    # Given
    bank = bank_as_bondbuyer
    bank.reserves = 300
    bank.deposits = 1000
    calc_prob = bank.calc_bond_purchases_probability
    calc_prob.return_value = 0.4
    random = bank.model.nprandom

    # When
    bank.invest_excess_reserves()

    # Then
    random.choice.assert_called_with([0, 1], p=[0.6, 0.4])
    assert random.choice.call_count == 2
    for bond_issuer in bond_issuers:
        calc_prob.assert_any_call(bond_issuer)


def test_buy_bonds_with_excess_reserves(bank_as_bondbuyer, bond_issuers):
    # Given
    bank = bank_as_bondbuyer
    bank.reserves = 150
    bank.deposits = 1000
    buyer = bank.roles["bond_buyer"]

    # When
    bank.invest_excess_reserves()

    # Then
    buyer.buy_bonds.assert_called_once_with(bond_issuers[0], 50)


def test_calc_profit():
    # Given
    bank = BankAgent(model=Mock())
    bank.loan_interest = 100
    bank.bond_interest = 30
    bank.reserve_interest = 10
    bank.bad_debt = 20
    bank.deposit_interest = 40
    bank.cash_advance_interest = 10

    # When
    profit = bank.calc_profit()

    # Then
    assert profit == 70


@pytest.mark.parametrize("profit, expected", [(100, 20), (0, 0), (-50, 0)])
def test_calc_taxes(profit, expected):
    # Given
    role = Mock()
    role.get_tax_rate.return_value = 0.20
    bank = BankAgent(model=Mock())
    bank.roles["tax_payer"] = role
    bank.profit = profit

    # When
    taxes = bank.calc_taxes()

    # Then
    assert taxes == expected


def test_calc_dividends():
    # Given
    model = Mock()
    model.p.rho = 0.5
    bank = BankAgent(model)
    bank.profit = 100
    bank.taxes_payable = 20

    # When
    dividends = bank.calc_dividends()

    # Then
    assert dividends == 40


def test_compute_profit_distribution(bank):
    # Given
    bank.calc_profit = Mock(return_value=100)
    bank.calc_taxes = Mock(return_value=20)
    bank.calc_dividends = Mock(return_value=30)

    # When
    bank.compute_profit_distribution()

    # Then
    assert bank.profit == 100
    assert bank.taxes_payable == 20
    assert bank.dividends_payable == 30


def test_update_net_worth(bank):
    # Given
    issuer = Mock()
    bank.profit = 500
    bank.net_worth = 500
    bank.taxes_payable = 50
    bank.dividends_payable = 100
    bank.roles["equity_issuer"] = issuer

    # When
    bank.update_net_worth()

    # Then
    issuer.update_equity_holdings.assert_called_once_with()
    assert bank.net_worth == pytest.approx(850)


def test_pay_taxes(bank):
    # Given
    tax_payer = Mock()
    bank.taxes_payable = 50
    bank.roles["tax_payer"] = tax_payer

    # When
    bank.pay_taxes()

    # Then
    tax_payer.pay_taxes.assert_called_once_with(50)
    assert bank.taxes_payable == 0


def test_pay_no_taxes(bank):
    # Given
    tax_payer = Mock()
    bank.taxes_payable = 0
    bank.roles["tax_payer"] = tax_payer

    # When
    bank.pay_taxes()

    # Then
    tax_payer.pay_taxes.assert_not_called()


def test_pay_dividends(bank):
    # Given
    issuer = Mock()
    bank.dividends_payable = 100
    bank.roles["equity_issuer"] = issuer

    # When
    bank.pay_dividends()

    # Then
    issuer.distribute_dividends.assert_called_once_with(100)
    assert bank.dividends_payable == 0


def test_pay_no_dividends(bank):
    # Given
    issuer = Mock()
    bank.dividends_payable = 0
    bank.roles["equity_issuer"] = issuer

    # When
    bank.pay_dividends()

    # Then
    issuer.distribute_dividends.assert_not_called()
