import pytest
from unittest.mock import Mock
from model.agents.government import Government

# ---------------------------------------------------
# ARCHITECTURE TESTS
# ----------------------------------------------------


def test_is_eco_agent():
    # Given
    from model.base import EcoAgent

    # Assert
    assert issubclass(Government, EcoAgent)


@pytest.fixture
def govt_before_setup():
    # Given
    model = Mock()
    govt = Government(model)
    return govt


def test_has_tax_rate(govt_before_setup):
    # Given
    govt = govt_before_setup

    # When
    govt.setup()

    # Then
    assert govt.tax_rate == 0


def test_has_bond_rate(govt_before_setup):
    # Given
    govt = govt_before_setup

    # When
    govt.setup()

    # Then
    assert govt.bond_rate == 0


def test_has_public_spending(govt_before_setup):
    # Given
    govt = govt_before_setup

    # When
    govt.setup()

    # Then
    assert govt.public_spending == 0


def test_has_desired_public_spending(govt_before_setup):
    # Given
    govt = govt_before_setup

    # When
    govt.setup()

    # Then
    assert govt.desired_public_spending == 0


def test_has_new_public_debt(govt_before_setup):
    # Given
    govt = govt_before_setup

    # When
    govt.setup()

    # Then
    assert govt.new_public_debt == 0


def test_has_budget_deficit(govt_before_setup):
    # Given
    govt = govt_before_setup

    # When
    govt.setup()

    # Then
    assert govt.budget_deficit == 0


def test_has_budget_surplus(govt_before_setup):
    # Given
    govt = govt_before_setup

    # When
    govt.setup()

    # Then
    assert govt.budget_surplus == 0


def test_has_prev_public_spending(govt_before_setup):
    # Given
    govt = govt_before_setup

    # When
    govt.setup()

    # Then
    assert govt.prev_public_spending == 0


def test_has_prev_budget_surplus(govt_before_setup):
    # Given
    govt = govt_before_setup

    # When
    govt.setup()

    # Then
    assert govt.prev_budget_surplus == 0


@pytest.fixture
def govt_with_roles_and_account(govt_before_setup):
    # Given
    roles = {}
    account = Mock(stocks={}, flows={})
    govt = govt_before_setup
    govt.account = account
    govt.roles = roles
    return govt, roles, account


# ---------------------------------------------------
# PUBLIC TRANSFERS TESTS
# ----------------------------------------------------


@pytest.fixture
def govt_as_authority(govt_with_roles_and_account):
    # Given
    role = Mock()
    govt, roles, _ = govt_with_roles_and_account
    roles["fiscal_authority"] = role
    return govt, role


def test_pay_public_transfers(govt_as_authority):
    # Given
    found = [Mock() for _ in range(2)]
    govt, role = govt_as_authority
    govt.public_spending = 100
    role.find_citizens.return_value = found

    # When
    govt.pay_public_transfers()

    # Then
    role.pay_public_transfers.assert_any_call(found[0], 50.0)
    role.pay_public_transfers.assert_any_call(found[1], 50.0)


# ---------------------------------------------------
#  BUDGET BALANCE
# ----------------------------------------------------


def test_calc_budget_balance(govt_with_roles_and_account):
    # Given
    govt, _, account = govt_with_roles_and_account
    account.flows["public_transfers"] = 700
    account.flows["taxes"] = 1000
    account.flows["bond_interests"] = 100

    # When
    balance = govt.calc_budget_balance()

    # Then
    assert balance == 200


def test_calc_and_records_budget_deficit(govt_with_roles_and_account):
    # Given
    govt, _, account = govt_with_roles_and_account
    account.flows["public_transfers"] = 600
    account.flows["taxes"] = 500
    account.flows["bond_interests"] = 100

    # When
    govt.calc_budget_balance()

    # Then
    assert govt.budget_deficit == 200
    assert govt.budget_surplus == 0


def test_calc_and_records_budget_surplus(govt_with_roles_and_account):
    # Given
    govt, _, account = govt_with_roles_and_account
    account.flows["public_transfers"] = 700
    account.flows["taxes"] = 1000
    account.flows["bond_interests"] = 100

    # When
    govt.calc_budget_balance()

    # Then
    assert govt.budget_surplus == 200
    assert govt.budget_deficit == 0


def test_calc_and_records_with_no_deficit_or_surplus(govt_with_roles_and_account):
    # Given
    govt, _, account = govt_with_roles_and_account
    account.flows["public_transfers"] = 700
    account.flows["taxes"] = 800
    account.flows["bond_interests"] = 100

    # When
    govt.calc_budget_balance()

    # Then
    assert govt.budget_deficit == 0
    assert govt.budget_surplus == 0


def test_calc_and_records_desired_public_spending(govt_as_authority):
    # Given
    govt, role = govt_as_authority
    govt.prev_public_spending = 10
    role.get_average_price.return_value = 2
    role.get_average_productivity.return_value = 3

    # When
    desired = govt.calc_desired_public_spending()

    # Then
    assert desired == 60
    assert govt.desired_public_spending == desired


# ---------------------------------------------------
#  PUBLIC POLICY
# ----------------------------------------------------


@pytest.mark.parametrize("tax_rate, expected", [(0.38, 0.40), (0.58, 0.50)])
def test_tax_rate_is_bounded(govt_before_setup, tax_rate, expected):
    # Given
    govt = govt_before_setup
    govt.tax_rate = tax_rate
    govt.p.tax_min = 0.40
    govt.p.tax_max = 0.50

    # When
    govt.apply_tax_rate_bounds()

    # Then
    assert govt.tax_rate == expected


@pytest.mark.parametrize("spending, expected", [(80, 100), (150, 120)])
def test_public_spending_is_bounded_by_gdp(govt_as_authority, spending, expected):
    # Given
    govt, role = govt_as_authority
    govt.public_spending = spending
    govt.p.g_min = 0.10
    govt.p.g_max = 0.12
    role.get_gdp.return_value = 1000

    # When
    govt.apply_public_spending_bounds()

    # Then
    assert govt.public_spending == expected


@pytest.fixture
def govt_for_policy(govt_as_authority):
    # Given
    govt, role = govt_as_authority
    govt.p.dmax = 0.05
    govt.p.delta = 0.10
    govt.tax_rate = 0.20
    govt.public_spending = 100
    govt.desired_public_spending = 0
    govt.apply_tax_rate_bounds = Mock()
    govt.apply_public_spending_bounds = Mock()
    govt.calc_desired_public_spending = Mock(return_value=0)
    govt.model.random.uniform.return_value = 0.05
    role.get_gdp.return_value = 1000
    return govt


def test_update_fiscal_policy_with_random_variation(govt_for_policy):
    # Given
    govt = govt_for_policy
    govt.budget_deficit = 100
    govt.desired_public_spending = 80
    random = govt.model.random

    # When
    govt.update_fiscal_policy()

    # Then
    random.uniform.assert_called_with(0, 0.10)


def test_update_fiscal_policy_with_multi_steps(govt_for_policy):
    # Given
    govt = govt_for_policy
    govt.budget_deficit = 100
    govt.desired_public_spending = 80

    # When
    govt.update_fiscal_policy()

    # Then
    govt.calc_desired_public_spending.assert_called_with()
    govt.apply_public_spending_bounds.assert_called_with()
    govt.apply_tax_rate_bounds.assert_called_with()


def test_reduce_spending_and_increase_tax_when_deficit_high(govt_for_policy):
    # Given
    govt = govt_for_policy
    govt.budget_deficit = 100
    govt.calc_desired_public_spending.return_value = 80

    # When
    govt.update_fiscal_policy()

    # Then
    assert govt.public_spending == pytest.approx(95)
    assert govt.tax_rate == pytest.approx(0.21)


def test_keep_spending_and_increase_tax_when_deficit_high(govt_for_policy):
    # Given
    govt = govt_for_policy
    govt.budget_deficit = 100
    govt.calc_desired_public_spending.return_value = 120

    # When
    govt.update_fiscal_policy()

    # Then
    assert govt.public_spending == pytest.approx(100)
    assert govt.tax_rate == pytest.approx(0.21)


def test_reduce_spending_and_tax_when_deficit_low(govt_for_policy):
    # Given
    govt = govt_for_policy
    govt.budget_deficit = 20
    govt.calc_desired_public_spending.return_value = 80

    # When
    govt.update_fiscal_policy()

    # Then
    assert govt.public_spending == pytest.approx(95)
    assert govt.tax_rate == pytest.approx(0.19)


def test_increase_spending_and_keep_tax_when_deficit_low(govt_for_policy):
    # Given
    govt = govt_for_policy
    govt.budget_deficit = 20
    govt.calc_desired_public_spending.return_value = 120

    # When
    govt.update_fiscal_policy()

    # Then
    assert govt.public_spending == pytest.approx(105)
    assert govt.tax_rate == pytest.approx(0.20)


# ---------------------------------------------------
#  BOND SUPPLY
# ----------------------------------------------------


@pytest.fixture
def govt_before_bond_calc(govt_with_roles_and_account):
    # Given
    govt, roles, _ = govt_with_roles_and_account
    roles["fiscal_authority"] = Mock()
    return govt


def test_calc_new_debt(govt_before_bond_calc):
    # Given
    govt = govt_before_bond_calc
    govt.budget_deficit = 200
    govt.prev_budget_surplus = 50
    govt.account.stocks["bonds"] = 1000

    # When
    new_debt = govt.calc_new_debt()

    # Then
    assert new_debt == 1150
    assert govt.new_public_debt == 1150


def test_calc_new_bonds(govt_before_bond_calc):
    # Given
    govt = govt_before_bond_calc
    govt.new_public_debt = 1150
    govt.account.stocks["bonds"] = 1000

    # When
    issuance = govt.calc_new_bonds()

    # Then
    assert issuance == 150


def test_calc_not_new_bonds_with_enough_bonds(govt_before_bond_calc):
    # Given
    govt = govt_before_bond_calc
    govt.new_public_debt = 900
    govt.account.stocks["bonds"] = 1000

    # When
    issuance = govt.calc_new_bonds()

    # Then
    assert issuance == 0


@pytest.fixture
def govt_before_bond_supply(govt_with_roles_and_account):
    # Given
    govt, roles, _ = govt_with_roles_and_account
    govt.calc_new_debt = Mock(return_value=0)
    govt.calc_new_bonds = Mock(return_value=0)
    govt.bond_supply = 0
    roles["bond_issuer"] = Mock()
    roles["fiscal_authority"] = Mock()
    return govt


def test_issues_bonds_with_role(govt_before_bond_supply):
    # Given
    govt = govt_before_bond_supply
    govt.bond_supply = 100
    govt.calc_new_bonds.return_value = 500
    govt.roles["fiscal_authority"].get_gdp.return_value = 1000
    role = govt.roles["bond_issuer"]

    # When
    govt.issue_bonds()

    # Then
    assert govt.bond_supply == 600
    assert role.debt_ratio == 0.6
    assert role.bond_value == 6.0
    assert role.bond_number == 100


def test_issues_bonds_with_multi_step(govt_before_bond_supply):
    # Given
    govt = govt_before_bond_supply
    govt.roles["fiscal_authority"].get_gdp.return_value = 1000

    # When
    govt.issue_bonds()

    # Then
    govt.calc_new_debt.assert_called_with()
    govt.calc_new_bonds.assert_called_with()


# ---------------------------------------------------
#  BOND REPAYMENT
# ----------------------------------------------------


@pytest.fixture
def govt_before_repayment(govt_with_roles_and_account):
    # Given
    govt, roles, _ = govt_with_roles_and_account
    roles["bond_issuer"] = Mock()
    roles["fiscal_authority"] = Mock()
    return govt


def test_update_bond_rate(govt_before_repayment):
    # Given
    govt = govt_before_repayment
    govt.p.chi = 0.02
    govt.account.stocks["bonds"] = 500
    govt.roles["fiscal_authority"].get_gdp.return_value = 1000
    govt.roles["fiscal_authority"].get_discount_rate.return_value = 0.03

    # when
    rate = govt.update_bond_rate()

    # Then
    assert rate == 0.04
    assert govt.bond_rate == 0.04


def test_repay_bonds(govt_before_repayment):
    # Given
    buyer = object()
    bonds = [{"buyer": buyer, "amount": 500}]
    govt = govt_before_repayment
    govt.bond_rate = 0.01
    role = govt.roles["bond_issuer"]
    role.find_bonds.return_value = bonds

    # When
    govt.repay_bonds()

    # Then
    role.repay_bonds.assert_called_with(buyer, 500, 5.0)


# ---------------------------------------------------
#  DEPOSIT GUARANTEE
# ----------------------------------------------------


@pytest.fixture
def govt_as_deposit_guarantee(govt_with_roles_and_account):
    # Given
    role = Mock()
    govt, roles, _ = govt_with_roles_and_account
    govt.bond_supply = 0
    govt._defaults = []
    roles["bond_issuer"] = Mock()
    roles["deposit_guarantee"] = role
    return govt, role


def test_issue_deposit_guarantee_bonds(govt_as_deposit_guarantee):
    # Given
    bank = Mock()
    bank.account.stocks = {"deposits": 100}
    govt, role = govt_as_deposit_guarantee
    govt.bond_supply = 200
    role.find_defaulted_banks.return_value = [bank]

    # When
    govt.issue_deposit_guarantee_bonds()

    # Then
    assert govt.bond_supply == 300
    assert govt.roles["bond_issuer"].bond_value == 3
    assert govt.roles["bond_issuer"].bond_number == 100


def test_issue_deposit_guarantee_bonds_registers_defaults(govt_as_deposit_guarantee):
    # Given
    bank = Mock()
    bank.account.stocks = {"deposits": 100}
    govt, role = govt_as_deposit_guarantee
    role.find_defaulted_banks.return_value = [bank]

    # When
    govt.issue_deposit_guarantee_bonds()

    # Then
    assert govt._defaults == [bank]


def test_reimburse_deposits(govt_as_deposit_guarantee):
    # Given
    bank, client = Mock(), Mock()
    deposits = [{"depositor": client, "amount": 100}]
    govt, role = govt_as_deposit_guarantee
    govt._defaults = [bank]
    role.find_deposit_accounts.return_value = deposits

    # When
    govt.reimburse_deposits()

    # Then
    role.find_deposit_accounts.assert_called_with(bank)
    role.reimburse_deposits.assert_called_with(client, 100)


def test_update_public_spending_history(govt_before_setup):
    # Given
    govt = govt_before_setup
    govt.public_spending = 200
    govt.prev_public_spending = 150

    # When
    govt.update_history()

    # Then
    assert govt.prev_public_spending == 200


def test_update_budget_history(govt_before_setup):
    # Given
    govt = govt_before_setup
    govt.budget_surplus = 100
    govt.prev_budget_surplus = 0

    # When
    govt.update_history()

    # Then
    assert govt.prev_budget_surplus == 100
