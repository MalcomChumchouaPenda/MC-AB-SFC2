import math
import pytest
from unittest.mock import Mock
from model.agents.bank import Bank

# ---------------------------------------------------
# ARCHITECTURE
# ----------------------------------------------------


def test_inherits_from_eco_agent():
    # Given
    from model.extensions import EcoAgent

    # Then
    assert issubclass(Bank, EcoAgent)


def test_initializes_taxes_payable(fake_model):
    # Given
    model = fake_model

    # When
    bank = Bank(model)

    # Then
    assert bank.taxes_payable == 0


def test_initializes_dividends_payable(fake_model):
    # Given
    model = fake_model

    # When
    bank = Bank(model)

    # Then
    assert bank.dividends_payable == 0


def test_initializes_credit_capacity(fake_model):
    # Given
    model = fake_model

    # When
    bank = Bank(model)

    # Then
    assert bank.credit_capacity == 0


def test_initializes_defaulted(fake_model):
    # Given
    model = fake_model

    # When
    bank = Bank(model)

    # Then
    assert bank.defaulted == False


# ---------------------------------------------------
# DEPOSIT INTERESTS PAYMENT
# ----------------------------------------------------


@pytest.fixture
def bank(fake_model):
    # Given
    model = fake_model
    model.nprandom = Mock()
    model.random = Mock()
    return Bank(model)


def test_pay_deposit_interests_to_all_clients(bank):
    # Given
    role, client = Mock(), Mock()
    role.find_deposits.return_value = [{"depositor": client, "amount": 100}]
    role.get_deposit_rate.return_value = 0.05
    bank.roles["deposit_bank"] = role

    # When
    bank.pay_deposit_interests()

    # Then
    role.find_deposits.assert_called_once_with()
    role.pay_interests.assert_called_once_with(client, 5.0)


# ---------------------------------------------------
#  CREDIT SUPPLY
# ----------------------------------------------------


@pytest.fixture
def account(bank):
    # Given
    account = {}
    bank.account = account
    return account


@pytest.fixture
def company_role(bank):
    # Given
    role = Mock()
    bank.roles["company"] = role
    return role


def test_calc_credit_capacity(bank, account):
    # Given
    bank.p.mu1 = 10
    account["equities"] = -100

    # When
    result = bank._calc_credit_capacity()

    # Then
    assert result == pytest.approx(1000)


def test_calc_loan_probability(bank):
    # Given
    bank.p.iota_l = 1
    borrower = Mock(loan_demand=100, net_worth=200)

    # When
    probability = bank._calc_loan_probability(borrower)

    # Then
    assert probability == pytest.approx(math.exp(-0.5))


def test_calc_loan_rate(bank, company_role):
    # Given
    bank.p.chi = 0.02
    company_role.get_discount_rate.return_value = 0.05
    borrower = Mock(loan_demand=100, net_worth=200)

    # When
    rate = bank._calc_loan_rate(borrower)

    # Then
    assert rate == pytest.approx(0.02 * 0.5 + 0.05)


@pytest.fixture
def lender_role(bank):
    # Given
    role = Mock()
    bank.roles["lender"] = role
    return role


@pytest.fixture
def deposit_bank_role(bank):
    # Given
    role = Mock()
    bank.roles["deposit_bank"] = role
    return role


@pytest.fixture
def borrowers():
    # Given
    return [Mock(id=i, loan_demand=100) for i in range(5)]


@pytest.fixture
def bank_before_loan(bank, lender_role, deposit_bank_role, borrowers):
    # Given
    _ = deposit_bank_role
    lender_role.loan_applicants = borrowers
    bank._calc_loan_rate = Mock(return_value=0.02)
    bank._calc_loan_probability = Mock(return_value=0.4)
    bank._calc_credit_capacity = Mock(return_value=500)
    random = bank.model.nprandom
    random.choice.return_value = 0
    return bank


def test_grant_loans_and_processes_all_loan_applicants(bank_before_loan, lender_role):
    # Given
    bank = bank_before_loan
    bank.credit_capacity = 500
    applicants = lender_role.loan_applicants
    random = bank.model.random

    # When
    bank.grant_loans()

    # Then
    random.shuffle.assert_called_with(applicants)
    for borrower in applicants:
        bank._calc_loan_rate.assert_any_call(borrower)
        bank._calc_loan_probability.assert_any_call(borrower)


def test_grant_loans_with_computed_probability(bank_before_loan, lender_role):
    # Given
    bank = bank_before_loan
    bank.credit_capacity = 500
    applicants = lender_role.loan_applicants
    random = bank.model.nprandom
    random.choice.side_effect = iter([1, 0, 0, 0, 0])

    # When
    bank.grant_loans()

    # Then
    random.choice.assert_called_with([0, 1], p=[0.6, 0.4])
    lender_role.grant_loan.assert_called_with(applicants[0], 100, 0.02)
    assert lender_role.grant_loan.call_count == 1


def test_grant_loans_in_regards_of_credit_capacity(bank_before_loan, lender_role):
    # Given
    bank = bank_before_loan
    bank._calc_credit_capacity.return_value = 200
    applicants = lender_role.loan_applicants
    random = bank.model.nprandom
    random.choice.return_value = 1

    # When
    bank.grant_loans()

    # Then
    lender_role.grant_loan.assert_any_call(applicants[0], 100, 0.02)
    lender_role.grant_loan.assert_any_call(applicants[1], 100, 0.02)
    assert lender_role.grant_loan.call_count == 2


def test_grant_loans_cleans_loan_applicants_list(bank_before_loan, lender_role):
    # Given
    bank = bank_before_loan
    bank._calc_credit_capacity.return_value = 200
    random = bank.model.nprandom
    random.choice.return_value = 1

    # When
    bank.grant_loans()

    # Then
    assert len(lender_role.loan_applicants) == 0


def test_grant_loans_and_make_deposits(bank_before_loan, lender_role):
    # Given
    bank = bank_before_loan
    applicants = lender_role.loan_applicants
    depositors = {a.id: Mock() for a in applicants}
    deposit_bank = bank.roles["deposit_bank"]
    deposit_bank.find_depositor.side_effect = lambda i: depositors[i]
    random = bank.model.nprandom
    random.choice.return_value = 1

    # When
    bank.grant_loans()

    # Then
    for id, depositor in depositors.items():
        deposit_bank.find_depositor.assert_any_call(id)
        deposit_bank.make_deposits.assert_any_call(depositor, 100)


# ---------------------------------------------------
#  ADVANCES REQUEST
# ----------------------------------------------------


@pytest.fixture
def bank_before_advance(bank, account):
    # Given
    bank.p.mu2 = 0.1
    account["cash"] = 0
    account["deposits"] = -1000
    account["advances"] = 0
    return bank


def test_request_advance_when_sufficient_reserves(bank_before_advance, company_role):
    # Given
    bank = bank_before_advance
    bank.account["cash"] = 200

    # When
    bank.request_cash_advances()

    # Then
    company_role.request_advances.assert_not_called()


def test_request_advance_when_insufficient_reserves(bank_before_advance, company_role):
    # Given
    bank = bank_before_advance
    bank.account["cash"] = 50

    # When
    bank.request_cash_advances()

    # Then
    company_role.request_advances.assert_called_with(50)


def test_repay_advance_when_insufficient_reserves(bank_before_advance, company_role):
    # Given
    bank = bank_before_advance
    bank.account["advances"] = -100
    company_role.get_discount_rate.return_value = 0.02

    # When
    bank.repay_cash_advances()

    # Then
    company_role.repay_advances.assert_called_with(100, 2)


# ---------------------------------------------------
# BONDS PURCHASES
# ----------------------------------------------------


def test_calc_bond_purchases_prob():
    # Given
    model = Mock()
    model.p.iota_b = 2
    bank = Bank(model)
    issuer = Mock(debt_ratio=0.5)

    # When
    probability = bank._calc_bond_purchases_prob(issuer)

    # Then
    assert probability == math.exp(-1)


@pytest.mark.parametrize("cash, expected", [(150, 50), (100, 0)])
def test_calc_excess_reserves(bank_before_advance, cash, expected):
    # Given
    bank = bank_before_advance
    bank.p.mu2 = 0.1
    bank.account["cash"] = cash

    # When
    excess_reserves = bank._calc_excess_reserves()

    # Then
    assert excess_reserves == expected


@pytest.fixture
def bond_buyer_role(bank):
    # Given
    role = Mock()
    bank.roles["bond_buyer"] = role
    return role


@pytest.fixture
def bank_without_bonds(bank, bond_buyer_role):
    # Given
    bond_buyer_role.find_issuers = Mock(return_value=[])
    bank._calc_bond_purchases_prob = Mock(return_value=0)
    bank._calc_excess_reserves = Mock(return_value=0)
    bank.model.nprandom.choice.return_value = 1
    return bank


def test_find_bond_suppliers_gets_and_shuffles_issuers(
    bank_without_bonds, bond_buyer_role
):
    # Given
    bank = bank_without_bonds
    random = bank.model.random
    bond_issuers = [Mock() for _ in range(3)]
    bond_buyer_role.find_issuers.return_value = bond_issuers

    # When
    result = bank._find_bond_issuers()

    # Then
    bond_buyer_role.find_issuers.assert_called_with()
    random.shuffle.assert_called_with(bond_issuers)
    assert result == bond_issuers


@pytest.fixture
def bond_issuers():
    return [
        Mock(bond_value=50, bond_number=2, debt_ratio=1.0),
        Mock(bond_value=50, bond_number=2, debt_ratio=1.0),
    ]


def test_buy_bonds_with_purchases_probability(
    bank_without_bonds, bond_issuers, bond_buyer_role
):
    # Given
    bank = bank_without_bonds
    bank._calc_excess_reserves.return_value = 1000
    bond_buyer_role.find_issuers.return_value = bond_issuers
    calc_prob = bank._calc_bond_purchases_prob
    calc_prob.return_value = 0.4
    random = bank.model.nprandom

    # When
    bank.buy_bonds()

    # Then
    random.choice.assert_called_with([0, 1], p=[0.6, 0.4])
    assert random.choice.call_count == 2
    for bond_issuer in bond_issuers:
        calc_prob.assert_any_call(bond_issuer)


def test_buy_bonds_with_excess_reserves(
    bank_without_bonds, bond_issuers, bond_buyer_role
):
    # Given
    bank = bank_without_bonds
    bank._calc_excess_reserves.return_value = 50
    bond_buyer_role.find_issuers.return_value = bond_issuers

    # When
    bank.buy_bonds()

    # Then
    bond_buyer_role.buy_bonds.assert_called_once_with(bond_issuers[0], 1)


def test_dont_buy_bonds_with_insufficient_reserves(
    bank_without_bonds, bond_issuers, bond_buyer_role
):
    # Given
    bank = bank_without_bonds
    bank._calc_excess_reserves.return_value = 50
    bond_buyer_role.find_issuers.return_value = bond_issuers

    # When
    bank.buy_bonds()

    # Then
    bond_buyer_role.buy_bonds.assert_called_once_with(bond_issuers[0], 1)


# ---------------------------------------------------
#  PROFIT AND TAXES
# ----------------------------------------------------


def test_calc_profit(bank, account):
    # Given
    account["cash_interests"] = 10
    account["loan_interests"] = 100
    account["loan_defaults"] = -20
    account["adv_interests"] = -10
    account["dep_interests"] = -40
    account["bond_interests"] = 30

    # When
    profit = bank._calc_profit()

    # Then
    assert profit == 70


@pytest.mark.parametrize("profit, expected", [(100, 20), (0, 0), (-50, 0)])
def test_calc_taxes(bank, company_role, profit, expected):
    # Given
    bank.profit = profit
    company_role.get_tax_rate.return_value = 0.20

    # When
    taxes = bank._calc_taxes()

    # Then
    assert taxes == expected


@pytest.mark.parametrize("profit, expected", [(100, 40), (-100, 0)])
def test_calc_dividends(bank, profit, expected):
    # Given
    bank.p.rho = 0.5
    bank.profit = profit
    bank.taxes_payable = 20

    # When
    dividends = bank._calc_dividends()

    # Then
    assert dividends == expected


def test_compute_profit_distribution(bank):
    # Given
    bank._calc_profit = Mock(return_value=100)
    bank._calc_taxes = Mock(return_value=20)
    bank._calc_dividends = Mock(return_value=30)

    # When
    bank.compute_profit_distribution()

    # Then
    assert bank.profit == 100
    assert bank.taxes_payable == 20
    assert bank.dividends_payable == 30


def test_update_net_worth(bank, company_role):
    # Given
    bank.profit = 500
    bank.taxes_payable = 50
    bank.dividends_payable = 100

    # When
    bank.update_net_worth()

    # Then
    company_role.update_equity_shares.assert_called_once_with(350)


def test_pay_taxes(bank, company_role):
    # Given
    bank.taxes_payable = 50

    # When
    bank.pay_taxes()

    # Then
    company_role.pay_taxes.assert_called_with(50)
    assert bank.taxes_payable == 0


def test_pay_no_taxes(bank, company_role):
    # Given
    bank.taxes_payable = 0

    # When
    bank.pay_taxes()

    # Then
    company_role.pay_taxes.assert_not_called()


def test_pay_dividends(bank, company_role):
    # Given
    founder = Mock()
    share = {"citizen": founder, "value": 1000}
    company_role.get_equity_shares.return_value = [share]
    bank.dividends_payable = 100

    # When
    bank.pay_dividends()

    # Then
    company_role.pay_dividends.assert_called_once_with(founder, 100)
    assert bank.dividends_payable == 0


def test_pay_no_dividends(bank, company_role):
    # Given
    company_role.get_equity_shares.return_value = []
    bank.dividends_payable = 0

    # When
    bank.pay_dividends()

    # Then
    company_role.get_equity_shares.assert_not_called()
    company_role.pay_dividends.assert_not_called()


# ---------------------------------------------------
# ENDOGENEOUS EXIT
# ----------------------------------------------------


@pytest.fixture
def bank_before_exit(bank, company_role, account):
    # Given
    account["cash"] = 0
    company_role.get_average_wage.return_value = 100
    return bank


@pytest.mark.parametrize("net_worth, defaulted", [(90, True), (150, False)])
def test_exit_when_bankrupt(bank_before_exit, net_worth, defaulted):
    # Given
    bank = bank_before_exit
    bank.account["equities"] = -net_worth

    # When
    bank.exit()

    # Then
    assert bank.defaulted == defaulted


def test_exit_transfer_residual_cash_to_founders(bank_before_exit, company_role):
    # Given
    founder = object()
    share = {"citizen": founder, "value": 90}
    bank = bank_before_exit
    bank.account["cash"] = 200
    bank.account["equities"] = -90
    company_role.get_equity_shares.return_value = [share]

    # When
    bank.exit()

    # Then
    company_role.transfer_residual_cash.assert_called_with(founder, 200)


def test_exit_sets_all_roles_defaulted(bank_before_exit):
    # Given
    bank = bank_before_exit
    bank.roles["any"] = Mock()
    bank.account["equities"] = -90

    # When
    bank.exit()

    # Then
    for role in bank.roles.values():
        assert role.defaulted is True


# ---------------------------------------------------
#  OBSERVATION
# ----------------------------------------------------
