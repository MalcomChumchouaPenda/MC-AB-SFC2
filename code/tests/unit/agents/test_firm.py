import math
import pytest
from unittest.mock import Mock, PropertyMock
from model.agents.firm import Firm

# ---------------------------------------------------
# ARCHITECTURE TESTS
# ----------------------------------------------------


def test_is_eco_agent():
    # Given
    from model.base import EcoAgent

    # Assert
    assert issubclass(Firm, EcoAgent)


@pytest.fixture
def firm_before_setup():
    # Given
    model = Mock()
    firm = Firm(model)
    return firm


def test_has_default_rd_expenditure(firm_before_setup):
    # Given
    firm = firm_before_setup

    # When
    firm.setup()

    # Then
    assert firm.rd == 0


def test_has_default_choices(firm_before_setup):
    # Given
    firm = firm_before_setup

    # When
    firm.setup()

    # Then
    assert firm.price == 0
    assert firm.wage_offer == 0
    assert firm.expected_sales == 0
    assert firm.desired_labor == 0
    assert firm.desired_output == 0
    assert firm.desired_loans == 0
    assert firm.desired_rd == 0
    assert firm.taxes_payable == 0
    assert firm.dividends_payable == 0


def test_has_default_variety(firm_before_setup):
    # Given
    firm = firm_before_setup

    # When
    firm.setup()

    # Then
    assert firm.variety == 0.0


def test_has_default_net_worth(firm_before_setup):
    # Given
    firm = firm_before_setup

    # When
    firm.setup()

    # Then
    assert firm.net_worth == 0.0


def test_has_default_net_cash_flow(firm_before_setup):
    # Given
    firm = firm_before_setup

    # When
    firm.setup()

    # Then
    assert firm.net_cash_flow == 0.0


def test_has_default_prev_sales(firm_before_setup):
    # Given
    firm = firm_before_setup

    # When
    firm.setup()

    # Then
    assert firm.prev_sales == 0


def test_has_default_prev_output(firm_before_setup):
    # Given
    firm = firm_before_setup

    # When
    firm.setup()

    # Then
    assert firm.prev_output == 0


def test_has_default_prev_expected_sales(firm_before_setup):
    # Given
    firm = firm_before_setup

    # When
    firm.setup()

    # Then
    assert firm.prev_expected_sales == 0


def test_has_default_prev_inventories(firm_before_setup):
    # Given
    firm = firm_before_setup

    # When
    firm.setup()

    # Then
    assert firm.prev_inventories == 0


def test_has_default_prev_labor(firm_before_setup):
    # Given
    firm = firm_before_setup

    # When
    firm.setup()

    # Then
    assert firm.prev_labor == 0


def test_has_default_prev_desired_labor(firm_before_setup):
    # Given
    firm = firm_before_setup

    # When
    firm.setup()

    # Then
    assert firm.prev_desired_labor == 0


@pytest.fixture
def firm_with_roles_and_account(firm_before_setup):
    # Given
    roles = {}
    account = Mock(stocks={}, flows={})
    firm = firm_before_setup
    firm.account = account
    firm.roles = roles
    return firm, roles, account


# ---------------------------------------------------
# PRODUCTION TESTS
# ----------------------------------------------------


@pytest.fixture
def firm_before_production(firm_with_roles_and_account):
    # Given
    role = Mock(inventories=0)
    firm, roles, account = firm_with_roles_and_account
    account.stocks["inventories"] = 0
    roles["producer"] = role
    return firm


def test_calc_desired_output(firm_before_production):
    # Given
    firm = firm_before_production
    firm.expected_sales = 100
    firm.p.theta = 0.20
    firm.roles["producer"].inventories = 20

    # When
    desired_output = firm.calc_desired_output()

    # Then
    assert desired_output == 100
    assert firm.desired_output == 100


def test_calc_desired_output_decreases_with_inventories(firm_before_production):
    # Given
    firm = firm_before_production
    firm.expected_sales = 100
    firm.p.theta = 0.20
    firm.roles["producer"].inventories = 50

    # When
    firm.calc_desired_output()

    # Then
    assert firm.desired_output == 70


def test_calc_labor_demand(firm_before_production):
    # Given
    firm = firm_before_production
    firm.desired_output = 100
    firm.roles["producer"].productivity = 2

    # When
    labor = firm.calc_labor_demand()

    # Then
    assert labor == 50
    assert firm.desired_labor == 50


def test_calc_desired_output_cannot_be_negative(firm_before_production):
    # Given
    firm = firm_before_production
    firm.expected_sales = 50
    firm.p.theta = 0.10
    firm.roles["producer"].inventories = 100

    # When
    firm.calc_desired_output()

    # Then
    assert firm.desired_output == 0


def test_plan_production_by_two_steps(firm_before_setup):
    # Given
    firm = firm_before_setup
    firm.calc_desired_output = Mock(side_effect=setattr(firm, "desired_output", 10))
    firm.calc_labor_demand = Mock(side_effect=setattr(firm, "desired_output", 20))

    # When
    firm.plan_production()

    # Then
    firm.calc_desired_output.assert_called_once_with()
    firm.calc_labor_demand.assert_called_once_with()
    assert firm.desired_output == 20


# ---------------------------------------------------
# PRICES AND EXPECTATIONS TESTS
# ----------------------------------------------------


@pytest.fixture
def pricing_firm(firm_with_roles_and_account):
    role = Mock(productivity=2)
    firm, roles, account = firm_with_roles_and_account
    firm.p.delta = 0.1
    firm.price = 10
    firm.expected_sales = 100
    account.flows["wages"] = 10
    roles["producer"] = role
    return firm


def test_increase_expectations_when_sales_exceed_expectations(pricing_firm):
    # Given
    firm = pricing_firm
    firm.prev_sales = 120
    firm.prev_output = 100
    firm.prev_expected_sales = 100
    firm.prev_inventories = 0
    random = firm.model.random
    random.uniform = Mock(side_effect=iter([0.05, 0.10, 0.15]))

    # When
    firm.adapt_expectations()

    # Then
    random.uniform.assert_called_with(0, 0.1)
    assert firm.expected_sales == pytest.approx(105)
    assert firm.price == pytest.approx(11.0)


def test_decrease_expectations_when_unsold_goods_exist(pricing_firm):
    # Given
    firm = pricing_firm
    firm.prev_sales = 80
    firm.prev_output = 100
    firm.prev_expected_sales = 100
    firm.prev_inventories = 20
    random = firm.model.random
    random.uniform = Mock(side_effect=iter([0.05, 0.10, 0.15]))

    # When
    firm.adapt_expectations()

    # Then
    random.uniform.assert_called_with(0, 0.1)
    assert firm.expected_sales == pytest.approx(95)
    assert firm.price == pytest.approx(9.0)


def test_keep_expectations_when_supply_constraint(pricing_firm):
    # Given
    firm = pricing_firm
    firm.prev_sales = 80
    firm.prev_output = 40
    firm.prev_expected_sales = 100
    firm.prev_inventories = 20
    random = firm.model.random
    random.uniform.return_value = 0.05

    # When
    firm.adapt_expectations()

    # Then
    assert firm.expected_sales == pytest.approx(100)
    assert firm.price == pytest.approx(10)


def test_price_cannot_be_below_unit_cost(pricing_firm):
    # Given
    firm = pricing_firm
    firm.prev_sales = 80
    firm.prev_output = 100
    firm.prev_expected_sales = 100
    firm.prev_inventories = 20
    firm.price = 5
    random = firm.model.random
    random.uniform.return_value = 0.05

    # When
    firm.adapt_expectations()

    # Then
    assert firm.expected_sales == pytest.approx(95)
    assert firm.price == pytest.approx(5)


# ---------------------------------------------------
# WAGE REVISION TESTS
# ----------------------------------------------------


def test_calc_revision_probability(firm_with_roles_and_account):
    # Given
    role = Mock()
    role.get_unemployment_rate.return_value = 0.1
    firm, roles, _ = firm_with_roles_and_account
    firm.p.upsilon = 1.0
    firm.p.upsilon_f = 0.9
    roles["employer"] = role

    # When
    result = firm.calc_revision_probability()

    # Then
    assert result == 0.9 * math.exp(-1.0 * 0.1)


@pytest.fixture
def hiring_firm(firm_before_setup):
    # Given
    firm = firm_before_setup
    firm.p.delta = 0.9
    firm.wage_offer = 10.0
    firm.calc_revision_probability = Mock(return_value=0)
    return firm


def test_increases_wage_when_labor_shortage(hiring_firm):
    # Given
    firm = hiring_firm
    firm.prev_labor = 80
    firm.prev_desired_labor = 100
    random = firm.model.nprandom
    random.choice.return_value = 1
    random.uniform.return_value = 0.05

    # When
    firm.revise_wage_offer()

    # Then
    random.uniform.assert_called_with(0, firm.p.delta)
    assert firm.wage_offer > 10.0


def test_increases_wage_with_upward_revision_prob(hiring_firm):
    # Given
    firm = hiring_firm
    firm.prev_labor = 80
    firm.prev_desired_labor = 100
    firm.calc_revision_probability.return_value = 0.6
    random = firm.model.nprandom
    random.choice.return_value = 1
    random.uniform.return_value = 0.05

    # When
    firm.revise_wage_offer()

    # Then
    random.choice.assert_called_with([0, 1], p=[1 - 0.6, 0.6])


def test_can_choose_to_not_increases_wage(hiring_firm):
    # Given
    firm = hiring_firm
    firm.prev_labor = 80
    firm.prev_desired_labor = 100
    random = firm.model.nprandom
    random.choice.return_value = 0
    random.uniform.return_value = 0.05

    # When
    firm.revise_wage_offer()

    # Then
    random.uniform.assert_not_called()
    assert firm.wage_offer == 10.0


def test_decreases_wage_when_all_positions_filled(hiring_firm):
    # Given
    firm = hiring_firm
    firm.prev_labor = 100
    firm.prev_desired_labor = 100
    random = firm.model.nprandom
    random.choice.return_value = 1
    random.uniform.return_value = 0.05

    # When
    firm.revise_wage_offer()

    # Then
    random.uniform.assert_called_with(0, firm.p.delta)
    assert firm.wage_offer < 10.0


def test_decreases_wage_with_downward_revision_prob(hiring_firm):
    # Given
    firm = hiring_firm
    firm.prev_labor = 100
    firm.prev_desired_labor = 100
    firm.calc_revision_probability.return_value = 0.6
    random = firm.model.nprandom
    random.choice.return_value = 1
    random.uniform.return_value = 0.05

    # When
    firm.revise_wage_offer()

    # Then
    random.choice.assert_called_with([0, 1], p=[0.6, 1 - 0.6])


def test_can_choose_to_not_decreases_wage(hiring_firm):
    # Given
    firm = hiring_firm
    firm.prev_labor = 100
    firm.prev_desired_labor = 100
    random = firm.model.nprandom
    random.choice.return_value = 0
    random.uniform.return_value = 0.05

    # When
    firm.revise_wage_offer()

    # Then
    random.uniform.assert_not_called()
    assert firm.wage_offer == 10.0


# ---------------------------------------------------
# R & D INVESTMENTS TESTS
# ----------------------------------------------------


def test_calc_desired_rd(firm_before_setup):
    # Given
    firm = firm_before_setup
    firm.p.gamma = 0.1
    firm.wage_offer = 10
    firm.desired_labor = 50

    # When
    rd = firm.calc_desired_rd()

    # Then
    assert rd == 50
    assert firm.desired_wage_bill == 500
    assert firm.desired_rd == 50


def test_execute_rd_without_constraints(firm_with_roles_and_account):
    # Given
    firm, _, account = firm_with_roles_and_account
    firm.desired_rd = 100
    firm.desired_labor = 50
    firm.labor = 50
    firm.desired_loans = 200
    account.stocks["loans"] = 200

    # When
    firm.execute_rd()

    # Then
    assert firm.rd == 100


def test_execute_rd_with_labor_constraint(firm_with_roles_and_account):
    # Given
    firm, _, account = firm_with_roles_and_account
    firm.desired_rd = 100
    firm.desired_labor = 100
    firm.labor = 80
    firm.desired_loans = 200
    account.stocks["loans"] = 200

    # When
    firm.execute_rd()

    # Then
    assert firm.rd == 0


def test_execute_rd_with_financial_constraint(firm_with_roles_and_account):
    # Given
    firm, _, account = firm_with_roles_and_account
    firm.desired_rd = 100
    firm.desired_labor = 50
    firm.labor = 50
    firm.desired_loans = 200
    account.stocks["loans"] = 100

    # When
    firm.execute_rd()

    # Then
    assert firm.rd == 0


@pytest.fixture
def firm_with_rd_project(firm_with_roles_and_account):
    # Given
    firm, roles, _ = firm_with_roles_and_account
    firm.p.nu = 0.5
    firm.rd = 100
    roles["producer"] = Mock()
    return firm


def test_calc_rd_success_probability_tradable(firm_with_rd_project):
    # Given
    firm = firm_with_rd_project
    firm.tradable = True
    role = firm.roles["producer"]
    role.get_average_price.return_value = 20
    role.get_average_productivity.return_value = 10

    # When
    probability = firm.calc_rd_success_probability()

    # Then
    expected = 1 - math.exp(-0.5 * 100 / (20 * 10))
    assert probability == pytest.approx(expected)


def test_calc_rd_success_probability_non_tradable(firm_with_rd_project):
    # Given
    firm = firm_with_rd_project
    firm.tradable = False
    role = firm.roles["producer"]
    role.get_average_price.return_value = 15
    role.get_average_productivity.return_value = 20

    # When
    probability = firm.calc_rd_success_probability()

    # Then
    expected = 1 - math.exp(-0.5 * 100 / (15 * 20))
    assert probability == pytest.approx(expected)


@pytest.fixture
def innovating_firm(firm_with_roles_and_account):
    firm, roles, _ = firm_with_roles_and_account
    firm.p.delta = 0.2
    firm.calc_desired_rd = Mock(side_effect=setattr(firm, "desired_rd", 100))
    firm.execute_rd = Mock(side_effect=setattr(firm, "rd", 100))
    firm.calc_rd_success_probability = Mock(return_value=0.6)
    roles["producer"] = Mock()
    return firm


def test_update_productivity_with_multi_steps(innovating_firm):
    # Given
    firm = innovating_firm
    random = firm.model.nprandom
    random.choice.return_value = 1
    random.uniform.return_value = 0.05
    role = firm.roles["producer"]
    role.productivity = 10
    role.get_average_productivity.return_value = 10

    # When
    firm.update_productivity()

    # Then
    assert firm.calc_desired_rd.called
    assert firm.execute_rd.called
    assert firm.calc_rd_success_probability.called
    random.choice.assert_called_with([0, 1], p=[1 - 0.6, 0.6])


def test_update_productivity_without_success(innovating_firm):
    # Given
    firm = innovating_firm
    random = firm.model.nprandom
    random.choice.return_value = 0
    role = firm.roles["producer"]
    role.get_average_productivity.return_value = 10
    role.productivity = 10

    # When
    firm.update_productivity()

    # Then
    assert role.productivity == 10


def test_update_productivity_by_innovation(innovating_firm):
    # Given
    firm = innovating_firm
    random = firm.model.nprandom
    random.choice.return_value = 1
    random.uniform = lambda a, b: b
    role = firm.roles["producer"]
    role.get_average_productivity.return_value = 10
    role.productivity = 10

    # When
    firm.update_productivity()

    # Then
    assert role.productivity == 12


def test_update_productivity_by_imitation(innovating_firm):
    # Given
    firm = innovating_firm
    random = firm.model.nprandom
    random.choice.return_value = 1
    random.uniform = lambda a, b: b
    role = firm.roles["producer"]
    role.get_average_productivity.return_value = 20
    role.productivity = 10

    # When
    firm.update_productivity()

    # Then
    assert role.productivity == 20


# ---------------------------------------------------
# CREDIT RELATED TESTS
# ----------------------------------------------------


@pytest.fixture
def firm_before_borrowing(firm_with_roles_and_account):
    # Given
    firm, _, account = firm_with_roles_and_account
    firm.wage_offer = 10
    firm.desired_labor = 10
    firm.desired_rd = 50
    account.stocks["deposits"] = 0
    return firm


def test_calc_desired_loans_when_external_finance_needed(firm_before_borrowing):
    # Given
    firm = firm_before_borrowing
    firm.account.stocks["deposits"] = 20

    # When
    result = firm.calc_desired_loans()

    # Then
    assert result == 130


def test_calc_desired_loans_when_internal_funds_are_sufficient(firm_before_borrowing):
    # Given
    firm = firm_before_borrowing
    firm.account.stocks["deposits"] = 150

    # When
    result = firm.calc_desired_loans()

    # Then
    assert result == 0


@pytest.fixture
def firm_as_borrower(firm_with_roles_and_account):
    # Given
    role = Mock()
    role.find_lenders.return_value = []
    firm, roles, account = firm_with_roles_and_account
    firm.calc_desired_loans = Mock(return_value=10)
    account.stocks["equities"] = 100
    roles["borrower"] = role
    return firm, role


def test_request_loans_to_all_lenders(firm_as_borrower):
    # Given
    lender = Mock()
    firm, role = firm_as_borrower
    role.find_lenders.return_value = [lender]

    # When
    firm.request_loans()

    # Then
    role.request_loans.assert_any_call(lender)


def test_request_loans_and_set_loan_demand(firm_as_borrower):
    # Given
    firm, role = firm_as_borrower
    firm.calc_desired_loans.return_value = 100
    role.find_lenders.return_value = [Mock()]

    # When
    firm.request_loans()

    # Then
    assert role.loan_demand == 100


def test_request_loans_and_registers_networth(firm_as_borrower):
    # Given
    firm, role = firm_as_borrower
    firm.account.stocks["equities"] = 200
    firm.calc_desired_loans.return_value = 100

    # When
    firm.request_loans()

    # Then
    assert role.net_worth == 200


def test_request_loans_and_registers_desired_loans(firm_as_borrower):
    # Given
    firm, _ = firm_as_borrower
    firm.calc_desired_loans.return_value = 100

    # When
    firm.request_loans()

    # Then
    assert firm.desired_loans == 100


@pytest.fixture
def firm_after_borrowing(firm_with_roles_and_account):
    # Given
    role = Mock()
    role.find_loans.return_value = []
    firm, roles, account = firm_with_roles_and_account
    account.stocks["deposits"] = 100
    account.stocks["loans"] = 100
    account.stocks["cash"] = 100
    roles["depositor"] = Mock()
    roles["borrower"] = role
    return firm, roles, account


def test_repay_loans_to_all_lenders(firm_after_borrowing):
    # Given
    firm, roles, account = firm_after_borrowing
    account.stocks["deposits"] = 200
    lender, role = object(), roles["borrower"]
    loans = [{"lender": lender, "amount": 100, "rate": 0.1}]
    role.find_loans.return_value = loans

    # When
    firm.repay_loans()

    # Then
    role.repay_loans.assert_called_once_with(lender, 100, 10.0)


def test_repay_loans_with_available_deposits(firm_after_borrowing):
    # Given
    firm, roles, account = firm_after_borrowing
    account.stocks["deposits"] = 50
    lender, role = object(), roles["borrower"]
    loans = [{"lender": lender, "amount": 100, "rate": 0.1}]
    role.find_loans.return_value = loans

    # When
    firm.repay_loans()

    # Then
    role.repay_loans.assert_called_once_with(lender, 50, 0.0)


@pytest.mark.parametrize("cash, expected", [(100, 80), (50, 50)])
def test_repay_loans_after_making_deposits(firm_after_borrowing, cash, expected):
    # Given
    firm, roles, account = firm_after_borrowing
    account.stocks["deposits"] = 20
    account.stocks["loans"] = 100
    account.stocks["cash"] = cash
    role = roles["depositor"]

    # When
    firm.repay_loans()

    # Then
    role.make_deposits.assert_called_once_with(expected)


# ---------------------------------------------------
# PROFITS, TAXES AND DIVIDENDS COMPUTAION
# ----------------------------------------------------


@pytest.mark.parametrize("sales, expected", [(600, 200), (200, -200)])
def test_calc_net_cash_flow(firm_with_roles_and_account, sales, expected):
    # Given
    firm, _, account = firm_with_roles_and_account
    account.flows["consumption"] = sales
    account.flows["loan_interests"] = 20
    account.flows["wages"] = 390
    account.flows["dep_interests"] = 10

    # When
    net_cash_flow = firm.calc_net_cash_flow()

    # Then
    assert net_cash_flow == expected


def test_calc_profit(firm_with_roles_and_account):
    # Given
    role = Mock(inventories=60, productivity=2)
    firm, roles, _ = firm_with_roles_and_account
    firm.net_cash_flow = 200
    firm.prev_inventories = 50
    firm.wage_offer = 20
    roles["producer"] = role

    # When
    profit = firm.calc_profit()

    # Then
    assert profit == 300


@pytest.fixture
def model_with_govt():
    # Given
    govt = Mock(tax_rate=0.0, reserves=0, taxes=0)
    model = Mock()
    model.governments = {"any": govt}
    return model, govt


@pytest.fixture
def firm_as_tax_payer(firm_with_roles_and_account):
    # Given
    role = Mock()
    firm, roles, account = firm_with_roles_and_account
    firm.account.flows["taxes"] = 0
    firm.reserves = 0
    roles["company"] = role
    return firm, role


@pytest.mark.parametrize("taxable, expected", [(100, 20), (-100, 0)])
def test_calc_taxes(firm_as_tax_payer, taxable, expected):
    # Given
    firm, role = firm_as_tax_payer
    firm.net_cash_flow = taxable
    role.get_tax_rate.return_value = 0.20

    # When
    taxes = firm.calc_taxes()

    # Then
    assert taxes == expected


@pytest.mark.parametrize("taxable, taxes, expected", [(100, 20, 40), (-100, 0, 0)])
def test_calc_dividends(firm_as_tax_payer, taxable, taxes, expected):
    # Given
    firm, _ = firm_as_tax_payer
    firm.net_cash_flow = taxable
    firm.taxes_payable = taxes
    firm.p.rho = 0.5

    # When
    dividends = firm.calc_dividends()

    # Then
    assert dividends == pytest.approx(expected)


def test_compute_profit_distribution(firm_before_setup):
    # Given
    firm = firm_before_setup
    firm.calc_net_cash_flow = Mock(return_value=90)
    firm.calc_profit = Mock(return_value=100)
    firm.calc_taxes = Mock(return_value=20)
    firm.calc_dividends = Mock(return_value=30)
    firm.update_production_history = Mock()

    # When
    firm.compute_profit_distribution()

    # Then
    assert firm.profit == 100
    assert firm.net_cash_flow == 90
    assert firm.taxes_payable == 20
    assert firm.dividends_payable == 30


# ---------------------------------------------------
# NET WORTH AND STATS UPDATES
# ----------------------------------------------------


def test_update_production_history(firm_with_roles_and_account):
    # Given
    role = Mock(output=100, sales=100, inventories=10)
    firm, roles, _ = firm_with_roles_and_account
    firm.expected_sales = 120
    roles["producer"] = role

    # When
    firm.update_production_history()

    # Then
    assert firm.prev_expected_sales == 120
    assert firm.prev_output == 100
    assert firm.prev_sales == 100
    assert firm.prev_inventories == 10


def test_update_net_worth(firm_with_roles_and_account):
    # Given
    role = Mock()
    firm, roles, _ = firm_with_roles_and_account
    firm.net_worth = 1000
    firm.net_cash_flow = 500
    firm.taxes_payable = 100
    firm.dividends_payable = 200
    roles["company"] = role

    # When
    firm.update_net_worth()

    # Then
    role.update_equity_holdings.assert_called_once_with()
    assert firm.net_worth == pytest.approx(1200)


# ---------------------------------------------------
# TAXES AND DIVIDENDS PAYMENTS
# ----------------------------------------------------


def test_pay_taxes(firm_as_tax_payer):
    # Given
    firm, role = firm_as_tax_payer
    firm.taxes_payable = 100

    # When
    firm.pay_taxes()

    # Then
    role.pay_taxes.assert_called_with(100)
    assert firm.taxes_payable == 0


def test_pay_no_taxes(firm_as_tax_payer):
    # Given
    firm, role = firm_as_tax_payer
    firm.taxes_payable = 0

    # When
    firm.pay_taxes()

    # Then
    role.pay_taxes.assert_not_called()
    assert firm.taxes_payable == 0


def test_pay_dividends(firm_with_roles_and_account):
    # Given
    role = Mock()
    firm, roles, _ = firm_with_roles_and_account
    firm.dividends_payable = 200
    roles["company"] = role

    # When
    firm.pay_dividends()

    # Then
    role.distribute_dividends.assert_called_once_with(200)
    assert firm.dividends_payable == 0


def test_pay_no_dividends(firm_with_roles_and_account):
    # Given
    role = Mock()
    firm, roles, _ = firm_with_roles_and_account
    firm.dividends_payable = 0
    roles["company"] = role

    # When
    firm.pay_dividends()

    # Then
    role.distribute_dividends.assert_not_called()


# ---------------------------------------------------
# ENDOGENEOUS EXIT
# ----------------------------------------------------


@pytest.fixture
def firm_before_exit(firm_with_roles_and_account):
    firm, roles, _ = firm_with_roles_and_account
    firm.wage_offer = 100
    roles["company"] = Mock()
    return firm


def test_exit_when_bankrupt(firm_before_exit):
    # Given
    firm = firm_before_exit
    firm.net_worth = 90
    role = firm.roles["company"]

    # When
    firm.exit()

    # Then
    role.close_firm.assert_called_once_with(firm)


def test_does_not_exit_when_not_bankrupt(firm_before_exit):
    # Given
    firm = firm_before_exit
    firm.net_worth = 150
    role = firm.roles["company"]

    # When
    firm.exit()

    # Then
    role.close_firm.assert_not_called()
