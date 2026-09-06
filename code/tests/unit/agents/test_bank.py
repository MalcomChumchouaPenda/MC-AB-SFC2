import math
import pytest
from unittest.mock import Mock, PropertyMock
from model.agents.bank import Bank

# ---------------------------------------------------
# ARCHITECTURE TESTS
# ----------------------------------------------------


def test_is_eco_agent():
    # Given
    from model.base import EcoAgent

    # Assert
    assert issubclass(Bank, EcoAgent)


@pytest.fixture
def bank_before_setup():
    # Given
    model = Mock()
    bank = Bank(model)
    return bank


@pytest.fixture
def bank_with_roles_and_account(bank_before_setup):
    # Given
    roles = {}
    account = Mock(stocks={}, flows={})
    bank = bank_before_setup
    bank.account = account
    bank.roles = roles
    return bank, roles, account


def test_has_default_deposit_rate(bank_before_setup):
    # Given
    bank = bank_before_setup

    # When
    bank.setup()

    # Then
    assert bank.deposit_rate == 0


def test_has_default_taxes_payable(bank_before_setup):
    # Given
    bank = bank_before_setup

    # When
    bank.setup()

    # Then
    assert bank.taxes_payable == 0


def test_has_default_dividends_payable(bank_before_setup):
    # Given
    bank = bank_before_setup

    # When
    bank.setup()

    # Then
    assert bank.dividends_payable == 0


def test_has_default_credit_capacity(bank_before_setup):
    # Given
    bank = bank_before_setup

    # When
    bank.setup()

    # Then
    assert bank.credit_capacity == 0


def test_has_default_net_worth(bank_before_setup):
    # Given
    bank = bank_before_setup

    # When
    bank.setup()

    # Then
    assert bank.net_worth == 0


def test_has_default_defaulted(bank_before_setup):
    # Given
    bank = bank_before_setup

    # When
    bank.setup()

    # Then
    assert bank.defaulted == False


# ---------------------------------------------------
# BEHAVIORS TESTS
# ----------------------------------------------------


def test_update_deposit_rate_as_fraction_of_discount_rate(bank_before_setup):
    # Given
    bank = bank_before_setup
    cb = Mock(discount_rate=0.05)
    bank.central_bank = cb
    bank.p.zeta = 0.8

    # When
    bank.update_deposit_rate()

    # Then
    assert bank.deposit_rate == pytest.approx(0.04)


def test_pay_deposit_interests_to_all_clients(bank_before_setup):
    # Given
    bank = bank_before_setup
    client = object()
    deposits = [{"client": client, "amount": 100}]
    deposit_market = Mock()
    deposit_market.get_bank_deposits.return_value = deposits
    bank.model.deposit_markets = {"any": deposit_market}
    bank.deposit_rate = 0.05

    # When
    bank.pay_deposit_interests()

    # Then
    deposit_market.get_bank_deposits.assert_called_once_with(bank)
    deposit_market.pay_interests.assert_called_once_with(client, bank, 5.0)


def test_updates_credit_capacity(bank_with_roles_and_account):
    # Given
    bank, _, account = bank_with_roles_and_account
    bank.p.mu1 = 10
    account.stocks["equity"] = 100

    # When
    bank.update_credit_capacity()

    # Then
    assert bank.credit_capacity == pytest.approx(1000)


def test_calc_loan_probability(bank_before_setup):
    # Given
    bank = bank_before_setup
    bank.p.iota_l = 1
    borrower = Mock(loan_demand=100, target_leverage=0.5)

    # When
    probability = bank.calc_loan_probability(borrower)

    # Then
    assert probability == pytest.approx(math.exp(-0.5))


def test_calc_loan_rate(bank_before_setup):
    # Given
    bank = bank_before_setup
    cb = Mock(discount_rate=0.05)
    bank.central_bank = cb
    bank.p.chi = 0.02
    borrower = Mock(target_leverage=5.0)

    # When
    rate = bank.calc_loan_rate(borrower)

    # Then
    assert rate == pytest.approx(0.02 * 5.0 + 0.05)


@pytest.fixture
def bank_as_lender(bank_with_roles_and_account):
    # Given
    borrowers = [Mock(loan_demand=100) for _ in range(5)]
    lender = Mock(loan_applicants=borrowers)
    bank, roles, _ = bank_with_roles_and_account
    bank.calc_loan_rate = Mock(return_value=0.02)
    bank.calc_loan_probability = Mock(return_value=0.4)
    bank.update_credit_capacity = Mock()
    random = bank.model.nprandom
    random.choice.return_value = 0
    roles["lender"] = lender
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
def bank_before_advance(bank_with_roles_and_account):
    bank, roles, account = bank_with_roles_and_account
    bank.p.mu2 = 0.1
    account.stocks["deposits"] = 1000
    account.stocks["advances"] = 0
    account.stocks["cash"] = 0
    roles["lender"] = Mock()
    return bank


def test_doesnot_request_advance_when_sufficient_reserves(bank_before_advance):
    # Given
    bank = bank_before_advance
    bank.account.stocks["cash"] = 200
    role = bank.roles["lender"]

    # When
    bank.request_cash_advances()

    # Then
    role.request_advances.assert_not_called()


def test_request_advance_when_insufficient_reserves(bank_before_advance):
    # Given
    bank = bank_before_advance
    bank.account.stocks["cash"] = 50
    role = bank.roles["lender"]

    # When
    bank.request_cash_advances()

    # Then
    role.request_advances.assert_called_with(50)


def test_calc_bond_purchases_probability():
    # Given
    model = Mock()
    model.p.iota_b = 2
    bank = Bank(model)
    issuer = Mock(debt_ratio=0.5)

    # When
    probability = bank.calc_bond_purchases_probability(issuer)

    # Then
    assert probability == math.exp(-1)


@pytest.mark.parametrize("reserves, expected", [(150, 50), (100, 0)])
def test_calc_excess_reserves(bank_before_advance, reserves, expected):
    # Given
    bank = bank_before_advance
    bank.account.stocks["cash"] = reserves
    bank.p.mu2 = 0.1

    # When
    excess_reserves = bank.calc_excess_reserves()

    # Then
    assert excess_reserves == expected


@pytest.fixture
def bank_as_bond_buyer(bank_with_roles_and_account):
    # Given
    role = Mock()
    role.find_issuers = Mock(return_value=[])
    bank, roles, _ = bank_with_roles_and_account
    bank.calc_bond_purchases_probability = Mock(return_value=0)
    bank.calc_excess_reserves = Mock(return_value=0)
    bank.model.nprandom.choice.return_value = 1
    roles["bond_buyer"] = role
    return bank, role


def test_find_bond_suppliers_gets_and_shuffles_issuers(bank_as_bond_buyer):
    # Given
    bond_issuers = [Mock() for _ in range(3)]
    bank, role = bank_as_bond_buyer
    random = bank.model.random
    role.find_issuers.return_value = bond_issuers

    # When
    result = bank.find_bond_issuers()

    # Then
    role.find_issuers.assert_called_with()
    random.shuffle.assert_called_with(bond_issuers)
    assert result == bond_issuers


@pytest.fixture
def bond_issuers():
    return [
        Mock(bond_value=50, bond_number=2, debt_ratio=1.0),
        Mock(bond_value=50, bond_number=2, debt_ratio=1.0),
    ]


def test_buy_bonds_with_purchases_probability(bank_as_bond_buyer, bond_issuers):
    # Given
    bank, role = bank_as_bond_buyer
    bank.calc_excess_reserves.return_value = 1000
    calc_prob = bank.calc_bond_purchases_probability
    calc_prob.return_value = 0.4
    random = bank.model.nprandom
    role.find_issuers.return_value = bond_issuers

    # When
    bank.buy_bonds()

    # Then
    random.choice.assert_called_with([0, 1], p=[0.6, 0.4])
    assert random.choice.call_count == 2
    for bond_issuer in bond_issuers:
        calc_prob.assert_any_call(bond_issuer)


def test_buy_bonds_with_excess_reserves(bank_as_bond_buyer, bond_issuers):
    # Given
    bank, role = bank_as_bond_buyer
    bank.calc_excess_reserves.return_value = 50
    role.find_issuers.return_value = bond_issuers

    # When
    bank.buy_bonds()

    # Then
    role.buy_bonds.assert_called_once_with(bond_issuers[0], 1)


def test_dont_buy_bonds_with_insufficient_reserves(bank_as_bond_buyer, bond_issuers):
    # Given
    bank, role = bank_as_bond_buyer
    bank.calc_excess_reserves.return_value = 50
    role.find_issuers.return_value = bond_issuers

    # When
    bank.buy_bonds()

    # Then
    role.buy_bonds.assert_called_once_with(bond_issuers[0], 1)


def test_calc_profit(bank_with_roles_and_account):
    # Given
    bank, _, account = bank_with_roles_and_account
    account.flows["loan_interests"] = 100
    account.flows["cash_interests"] = 10
    bank.bad_debt = 20
    account.flows["adv_interests"] = 10
    account.flows["dep_interests"] = 40
    account.flows["bond_interests"] = 30

    # When
    profit = bank.calc_profit()

    # Then
    assert profit == 70


@pytest.fixture
def bank_as_taxpayer(bank_with_roles_and_account):
    # Given
    role = Mock()
    bank, roles, account = bank_with_roles_and_account
    account.flows["taxes"] = 0
    account.stocks["cash"] = 0
    roles["company"] = role
    return bank, role


@pytest.mark.parametrize("profit, expected", [(100, 20), (0, 0), (-50, 0)])
def test_calc_taxes(bank_as_taxpayer, profit, expected):
    # Given
    bank, role = bank_as_taxpayer
    bank.profit = profit
    role.get_tax_rate.return_value = 0.20

    # When
    taxes = bank.calc_taxes()

    # Then
    assert taxes == expected


def test_calc_dividends(bank_as_taxpayer):
    # Given
    bank, _ = bank_as_taxpayer
    bank.p.rho = 0.5
    bank.profit = 100
    bank.taxes_payable = 20

    # When
    dividends = bank.calc_dividends()

    # Then
    assert dividends == 40


def test_compute_profit_distribution(bank_before_setup):
    # Given
    bank = bank_before_setup
    bank.calc_profit = Mock(return_value=100)
    bank.calc_taxes = Mock(return_value=20)
    bank.calc_dividends = Mock(return_value=30)

    # When
    bank.compute_profit_distribution()

    # Then
    assert bank.profit == 100
    assert bank.taxes_payable == 20
    assert bank.dividends_payable == 30


def test_update_net_worth(bank_with_roles_and_account):
    # Given
    bank, roles, _ = bank_with_roles_and_account
    role = Mock()
    bank.profit = 500
    bank.net_worth = 500
    bank.taxes_payable = 50
    bank.dividends_payable = 100
    roles["company"] = role

    # When
    bank.update_net_worth()

    # Then
    role.update_equity_holdings.assert_called_once_with()
    assert bank.net_worth == pytest.approx(850)


def test_pay_taxes(bank_as_taxpayer):
    # Given
    bank, role = bank_as_taxpayer
    bank.taxes_payable = 50

    # When
    bank.pay_taxes()

    # Then
    role.pay_taxes.assert_called_with(50)
    assert bank.taxes_payable == 0


def test_pay_no_taxes(bank_as_taxpayer):
    # Given
    bank, role = bank_as_taxpayer
    bank.taxes_payable = 0

    # When
    bank.pay_taxes()

    # Then
    role.pay_taxes.assert_not_called()


def test_pay_dividends(bank_with_roles_and_account):
    # Given
    role = Mock()
    bank, roles, _ = bank_with_roles_and_account
    bank.dividends_payable = 100
    roles["company"] = role

    # When
    bank.pay_dividends()

    # Then
    role.pay_dividends.assert_called_once_with(100)
    assert bank.dividends_payable == 0


def test_pay_no_dividends(bank_with_roles_and_account):
    # Given
    role = Mock()
    bank, roles, _ = bank_with_roles_and_account
    bank.dividends_payable = 0
    roles["company"] = role

    # When
    bank.pay_dividends()

    # Then
    role.pay_dividends.assert_not_called()


# ---------------------------------------------------
# ENDOGENEOUS EXIT TESTS
# ----------------------------------------------------


@pytest.fixture
def bank_before_exit(bank_with_roles_and_account):
    role = Mock()
    role.get_average_wage.return_value = 100
    bank, roles, _ = bank_with_roles_and_account
    roles["company"] = role
    return bank


def test_exit_when_bankrupt(bank_before_exit):
    # Given
    bank = bank_before_exit
    bank.net_worth = 90
    role = bank.roles["company"]

    # When
    bank.exit()

    # Then
    role.close_bank.assert_called_once_with(bank)


def test_does_not_exit_when_not_bankrupt(bank_before_exit):
    # Given
    bank = bank_before_exit
    bank.net_worth = 150
    role = bank.roles["company"]

    # When
    bank.exit()

    # Then
    role.close_bank.assert_not_called()
