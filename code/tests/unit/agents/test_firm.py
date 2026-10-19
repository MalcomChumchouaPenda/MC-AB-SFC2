import math
import pytest
from unittest.mock import Mock
from model.agents.firm import Firm

# ---------------------------------------------------
# ARCHITECTURE
# ----------------------------------------------------


def test_inherits_from_eco_agent():
    # Given
    from model.extensions import EcoAgent

    # When
    is_derived = issubclass(Firm, EcoAgent)

    # Then
    assert is_derived


@pytest.fixture
def model(fake_model):
    # Given
    model = fake_model
    model.nprandom = Mock()
    return model


def test_initializes_tradable(model):
    # When
    firm = Firm(model)

    # Then
    assert firm.tradable is False


def test_initializes_defaulted(model):
    # When
    firm = Firm(model)

    # Then
    assert firm.defaulted is False


def test_initializes_expected_sales(model):
    # When
    firm = Firm(model)

    # Then
    assert firm.expected_sales == 0


def test_initializes_desired_labor(model):
    # When
    firm = Firm(model)

    # Then
    assert firm.desired_labor == 0


def test_initializes_desired_output(model):
    # When
    firm = Firm(model)

    # Then
    assert firm.desired_output == 0


def test_initializes_desired_loans(model):
    # When
    firm = Firm(model)

    # Then
    assert firm.desired_loans == 0


def test_initializes_desired_rd_expense(model):
    # When
    firm = Firm(model)

    # Then
    assert firm.desired_rd == 0


def test_initializes_taxes_payable(model):
    # When
    firm = Firm(model)

    # Then
    assert firm.taxes_payable == 0


def test_initializes_dividends_payable(model):
    # When
    firm = Firm(model)

    # Then
    assert firm.dividends_payable == 0


def test_initializes_net_worth(model):
    # When
    firm = Firm(model)

    # Then
    assert firm.net_worth == 0.0


def test_initializes_net_cash_flow(model):
    # When
    firm = Firm(model)

    # Then
    assert firm.net_cash_flow == 0.0


def test_initializes_prev_sales(model):
    # When
    firm = Firm(model)

    # Then
    assert firm.prev_sales == 0


def test_initializes_prev_output(model):
    # When
    firm = Firm(model)

    # Then
    assert firm.prev_output == 0


def test_initializes_prev_expected_sales(model):
    # When
    firm = Firm(model)

    # Then
    assert firm.prev_expected_sales == 0


def test_initializes_prev_inventories(model):
    # When
    firm = Firm(model)

    # Then
    assert firm.prev_inventories == 0


def test_initializes_prev_labor(model):
    # When
    firm = Firm(model)

    # Then
    assert firm.prev_labor == 0


def test_initializes_prev_desired_labor(model):
    # When
    firm = Firm(model)

    # Then
    assert firm.prev_desired_labor == 0


# ---------------------------------------------------
# PRODUCTION PLANNING
# ----------------------------------------------------


@pytest.fixture
def firm(fake_model):
    # Given
    model = fake_model
    model.random = Mock()
    model.nprandom = Mock()
    return Firm(model)


def test_plan_production_by_two_steps(firm):
    # Given
    firm._calc_desired_output = Mock(side_effect=setattr(firm, "desired_output", 10))
    firm._calc_labor_demand = Mock(side_effect=setattr(firm, "desired_output", 20))

    # When
    firm.plan_production()

    # Then
    firm._calc_desired_output.assert_called_once_with()
    firm._calc_labor_demand.assert_called_once_with()
    assert firm.desired_output == 20


@pytest.fixture
def firm_with_roles_and_account(firm):
    # Given
    roles = {}
    account = {}
    firm.account = account
    firm.roles = roles
    return firm, roles, account


@pytest.fixture
def before_production(firm_with_roles_and_account):
    # Given
    role = Mock(inventories=0)
    firm, roles, account = firm_with_roles_and_account
    account["inventories"] = 0
    roles["producer"] = role
    return firm


def test_calc_desired_output(before_production):
    # Given
    firm = before_production
    firm.expected_sales = 100
    firm.p.theta = 0.20
    firm.roles["producer"].inventories = 20

    # When
    desired_output = firm._calc_desired_output()

    # Then
    assert desired_output == 100
    assert firm.desired_output == 100


def test_calc_desired_output_decreases_with_inventories(before_production):
    # Given
    firm = before_production
    firm.expected_sales = 100
    firm.p.theta = 0.20
    firm.roles["producer"].inventories = 50

    # When
    firm._calc_desired_output()

    # Then
    assert firm.desired_output == 70


def test_calc_labor_demand(before_production):
    # Given
    firm = before_production
    firm.desired_output = 100
    firm.roles["producer"].phi = 2

    # When
    labor = firm._calc_labor_demand()

    # Then
    assert labor == 50
    assert firm.desired_labor == 50


def test_calc_desired_output_cannot_be_negative(before_production):
    # Given
    firm = before_production
    firm.expected_sales = 50
    firm.p.theta = 0.10
    firm.roles["producer"].inventories = 100

    # When
    firm._calc_desired_output()

    # Then
    assert firm.desired_output == 0


# ---------------------------------------------------
# PRICES AND EXPECTATIONS
# ----------------------------------------------------


@pytest.fixture
def before_pricing(firm_with_roles_and_account):
    role = Mock(phi=2, price=10)
    firm, roles, account = firm_with_roles_and_account
    firm.expected_sales = 100
    firm.p.delta = 0.1
    account["wages"] = 10
    roles["producer"] = role
    return firm


def test_increase_expectations_when_sales_exceed_expectations(before_pricing):
    # Given
    firm = before_pricing
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
    assert firm.roles["producer"].price == pytest.approx(11.0)


def test_decrease_expectations_when_unsold_goods_exist(before_pricing):
    # Given
    firm = before_pricing
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
    assert firm.roles["producer"].price == pytest.approx(9.0)


def test_keep_expectations_when_supply_constraint(before_pricing):
    # Given
    firm = before_pricing
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
    assert firm.roles["producer"].price == pytest.approx(10)


def test_price_cannot_be_below_unit_cost(before_pricing):
    # Given
    firm = before_pricing
    firm.prev_sales = 80
    firm.prev_output = 100
    firm.prev_expected_sales = 100
    firm.prev_inventories = 20
    firm.roles["producer"].price = 5
    random = firm.model.random
    random.uniform.return_value = 0.05

    # When
    firm.adapt_expectations()

    # Then
    assert firm.expected_sales == pytest.approx(95)
    assert firm.roles["producer"].price == pytest.approx(5)


# ---------------------------------------------------
# WAGE REVISION
# ----------------------------------------------------


def test_calc_revision_probability(firm_with_roles_and_account):
    # Given
    role = Mock()
    role.get_unemployment.return_value = 0.1
    firm, roles, _ = firm_with_roles_and_account
    firm.p.upsilon = 1.0
    roles["employer"] = role

    # When
    result = firm._calc_revision_probability()

    # Then
    assert result == math.exp(-1.0 * 0.1)


@pytest.fixture
def before_hiring(firm):
    # Given
    firm._calc_revision_probability = Mock(return_value=0)
    firm.roles["employer"] = Mock(wage=10.0)
    firm.model.nprandom = Mock()
    firm.p.delta = 0.9
    return firm


def test_increases_wage_when_labor_shortage(before_hiring):
    # Given
    firm = before_hiring
    firm.prev_labor = 80
    firm.prev_desired_labor = 100
    random = firm.model.nprandom
    random.choice.return_value = 1
    random.uniform.return_value = 0.05

    # When
    firm.revise_wage_offer()

    # Then
    random.uniform.assert_called_with(0, firm.p.delta)
    assert firm.roles["employer"].wage > 10.0


def test_increases_wage_with_upward_revision_prob(before_hiring):
    # Given
    firm = before_hiring
    firm.prev_labor = 80
    firm.prev_desired_labor = 100
    firm._calc_revision_probability.return_value = 0.6
    random = firm.model.nprandom
    random.choice.return_value = 1
    random.uniform.return_value = 0.05

    # When
    firm.revise_wage_offer()

    # Then
    random.choice.assert_called_with([0, 1], p=[1 - 0.6, 0.6])


def test_can_choose_to_not_increases_wage(before_hiring):
    # Given
    firm = before_hiring
    firm.prev_labor = 80
    firm.prev_desired_labor = 100
    random = firm.model.nprandom
    random.choice.return_value = 0
    random.uniform.return_value = 0.05

    # When
    firm.revise_wage_offer()

    # Then
    random.uniform.assert_not_called()
    assert firm.roles["employer"].wage == 10.0


def test_decreases_wage_when_all_positions_filled(before_hiring):
    # Given
    firm = before_hiring
    firm.prev_labor = 100
    firm.prev_desired_labor = 100
    random = firm.model.nprandom
    random.choice.return_value = 1
    random.uniform.return_value = 0.05

    # When
    firm.revise_wage_offer()

    # Then
    random.uniform.assert_called_with(0, firm.p.delta)
    assert firm.roles["employer"].wage < 10.0


def test_decreases_wage_with_downward_revision_prob(before_hiring):
    # Given
    firm = before_hiring
    firm.prev_labor = 100
    firm.prev_desired_labor = 100
    firm._calc_revision_probability.return_value = 0.6
    random = firm.model.nprandom
    random.choice.return_value = 1
    random.uniform.return_value = 0.05

    # When
    firm.revise_wage_offer()

    # Then
    random.choice.assert_called_with([0, 1], p=[0.6, 1 - 0.6])


def test_can_choose_to_not_decreases_wage(before_hiring):
    # Given
    firm = before_hiring
    firm.prev_labor = 100
    firm.prev_desired_labor = 100
    random = firm.model.nprandom
    random.choice.return_value = 0
    random.uniform.return_value = 0.05

    # When
    firm.revise_wage_offer()

    # Then
    random.uniform.assert_not_called()
    assert firm.roles["employer"].wage == 10.0


# ---------------------------------------------------
# R & D INVESTMENTS
# ----------------------------------------------------


def test_calc_desired_rd(firm):
    # Given
    firm.p.gamma = 0.1
    firm.desired_labor = 50
    firm.roles["employer"] = Mock(wage=10)

    # When
    rd = firm.calc_desired_rd()

    # Then
    assert rd == 50
    assert firm.desired_wage_bill == 500
    assert firm.desired_rd == 50


@pytest.fixture
def before_rd_investment(firm_with_roles_and_account):
    # Given
    producer_role = Mock()
    employer_role = Mock(labor=50.0)
    firm, roles, account = firm_with_roles_and_account
    roles["employer"] = employer_role
    roles["producer"] = producer_role
    return firm, producer_role, account


def test_execute_rd_launchs_innovation_if_no_constraints(before_rd_investment):
    # Given
    firm, role, account = before_rd_investment
    firm.desired_rd = 100
    firm.desired_labor = 50
    firm.desired_loans = 200
    account["loans"] = 200

    # When
    firm.execute_rd()

    # Then
    role.execute_rd.assert_called_with(100)


def test_execute_rd_does_nothing_if_no_desire(before_rd_investment):
    # Given
    firm, role, account = before_rd_investment
    firm.desired_rd = 0
    firm.desired_labor = 100
    firm.desired_loans = 200
    account["loans"] = 200

    # When
    firm.execute_rd()

    # Then
    role.execute_rd.assert_not_called()


def test_execute_rd_does_nothing_if_labor_constraint(before_rd_investment):
    # Given
    firm, role, account = before_rd_investment
    firm.desired_rd = 100
    firm.desired_labor = 100
    firm.desired_loans = 200
    account["loans"] = 200

    # When
    firm.execute_rd()

    # Then
    role.execute_rd.assert_not_called()


def test_execute_rd_does_nothing_if_financial_constraint(before_rd_investment):
    # Given
    firm, role, account = before_rd_investment
    firm.desired_rd = 100
    firm.desired_labor = 50
    firm.desired_loans = 200
    account["loans"] = 100

    # When
    firm.execute_rd()

    # Then
    role.execute_rd.assert_not_called()


# ---------------------------------------------------
# PRODUCTION
# ----------------------------------------------------


@pytest.fixture
def before_production(firm_with_roles_and_account):
    # Given
    firm, roles, _ = firm_with_roles_and_account
    roles["producer"] = Mock()
    roles["employer"] = Mock()
    return firm


def test_produce_goods_with_job_quantity(before_production):
    # Given
    firm = before_production
    producer_role = firm.roles["producer"]
    employer_role = firm.roles["employer"]
    employer_role.labor = 0.9

    # When
    firm.produce_goods()

    # Then
    producer_role.produce_goods.assert_called_with(0.9)


# ---------------------------------------------------
# CREDIT DEMAND
# ----------------------------------------------------


@pytest.fixture
def before_borrowing(firm_with_roles_and_account):
    # Given
    firm, roles, account = firm_with_roles_and_account
    firm.desired_labor = 10
    firm.desired_rd = 50
    account["deposits"] = 0
    roles["employer"] = Mock(wage=10)
    return firm


def test_calc_desired_loans_when_external_finance_needed(before_borrowing):
    # Given
    firm = before_borrowing
    firm.account["deposits"] = 20

    # When
    result = firm._calc_desired_loans()

    # Then
    assert result == 130


def test_calc_desired_loans_when_internal_funds_are_sufficient(before_borrowing):
    # Given
    firm = before_borrowing
    firm.account["deposits"] = 150

    # When
    result = firm._calc_desired_loans()

    # Then
    assert result == 0


@pytest.fixture
def firm_as_borrower(firm_with_roles_and_account):
    # Given
    role = Mock()
    role.find_lenders.return_value = []
    firm, roles, account = firm_with_roles_and_account
    firm._calc_desired_loans = Mock(return_value=10)
    account["equities"] = 100
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
    firm._calc_desired_loans.return_value = 100
    role.find_lenders.return_value = [Mock()]

    # When
    firm.request_loans()

    # Then
    assert role.loan_demand == 100


def test_request_loans_and_registers_desired_loans(firm_as_borrower):
    # Given
    firm, _ = firm_as_borrower
    firm._calc_desired_loans.return_value = 100

    # When
    firm.request_loans()

    # Then
    assert firm.desired_loans == 100


@pytest.mark.parametrize("desired", [0, -100])
def test_dont_request_unneccessary_loans(firm_as_borrower, desired):
    # Given
    firm, role = firm_as_borrower
    firm._calc_desired_loans.return_value = desired

    # When
    firm.request_loans()

    # Then
    role.request_loans.assert_not_called()


# ---------------------------------------------------
# CREDIT AND LOAN REPAYMENT
# ----------------------------------------------------


@pytest.fixture
def firm_after_borrowing(firm_with_roles_and_account):
    # Given
    role = Mock()
    role.find_loans.return_value = []
    firm, roles, account = firm_with_roles_and_account
    account["deposits"] = 100
    account["loans"] = 100
    account["cash"] = 100
    roles["depositor"] = Mock()
    roles["borrower"] = role
    return firm, roles, account


@pytest.mark.parametrize("cash, expected", [(100, 80), (50, 50), (0, 0)])
def test_repay_loans_after_making_deposits(firm_after_borrowing, cash, expected):
    # Given
    firm, roles, account = firm_after_borrowing
    account["deposits"] = 20
    account["cash"] = cash
    account["loans"] = 100
    role = roles["depositor"]

    # When
    firm.repay_loans()

    # Then
    role.make_deposits.assert_called_once_with(expected)


def test_repay_loans_to_all_lenders(firm_after_borrowing):
    # Given
    lender = object()
    loan = {"lender": lender, "amount": 100, "rate": 0.1}
    firm, roles, account = firm_after_borrowing
    account["deposits"] = 200
    role = roles["borrower"]
    role.find_loans.return_value = [loan]

    # When
    firm.repay_loans()

    # Then
    role.repay_loans.assert_called_once_with(lender, 100, 10.0)


@pytest.mark.parametrize("fund, default", [(100, 0), (80, 20), (0, 100)])
def test_repay_loans_with_available_deposits(firm_after_borrowing, fund, default):
    # Given
    lender = object()
    loan = {"lender": lender, "amount": 100, "rate": 0.1}
    firm, roles, account = firm_after_borrowing
    account["deposits"] = fund
    role = roles["borrower"]
    role.find_loans.return_value = [loan]

    # When
    firm.repay_loans()

    # Then
    role.repay_loans.assert_called_once_with(lender, fund, 0.0)
    role.make_defaults.assert_called_once_with(lender, default)


# ---------------------------------------------------
# WAGES PAYMENT
# ----------------------------------------------------


@pytest.fixture
def before_wages_payment(firm_with_roles_and_account):
    # Given
    firm, roles, _ = firm_with_roles_and_account
    roles["employer"] = Mock(wage=2.0)
    return firm


def test_pay_wages_by_job(before_wages_payment):
    # Given
    worker = Mock()
    job = {"worker": worker, "quantity": 0.5}
    firm = before_wages_payment
    role = firm.roles["employer"]
    role.get_jobs.return_value = [job]

    # When
    firm.pay_wages()

    # Then
    role.pay_wages.assert_called_with(worker, 1.0)


# ---------------------------------------------------
# PROFITS, TAXES AND DIVIDENDS COMPUTATION
# ----------------------------------------------------


@pytest.mark.parametrize("sales, expected", [(600, 200), (200, -200)])
def test_calc_net_cash_flow(firm_with_roles_and_account, sales, expected):
    # Given
    firm, _, account = firm_with_roles_and_account
    account["consumption"] = sales
    account["loan_interests"] = 20
    account["wages"] = 390
    account["dep_interests"] = 10

    # When
    net_cash_flow = firm._calc_net_cash_flow()

    # Then
    assert net_cash_flow == expected


def test_calc_profit(firm_with_roles_and_account):
    # Given
    firm, roles, _ = firm_with_roles_and_account
    firm.net_cash_flow = 200
    firm.prev_inventories = 50
    roles["employer"] = Mock(wage=20)
    roles["producer"] = Mock(inventories=60, phi=2)

    # When
    profit = firm._calc_profit()

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
    firm, roles, _ = firm_with_roles_and_account
    firm.account["taxes"] = 0
    roles["company"] = role
    return firm, role


@pytest.mark.parametrize("taxable, expected", [(100, 20), (-100, 0)])
def test_calc_taxes(firm_as_tax_payer, taxable, expected):
    # Given
    firm, role = firm_as_tax_payer
    firm.net_cash_flow = taxable
    role.get_tax_rate.return_value = 0.20

    # When
    taxes = firm._calc_taxes()

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
    dividends = firm._calc_dividends()

    # Then
    assert dividends == pytest.approx(expected)


def test_compute_profit_distribution(firm):
    # Given
    firm._calc_net_cash_flow = Mock(return_value=90)
    firm._calc_profit = Mock(return_value=100)
    firm._calc_taxes = Mock(return_value=20)
    firm._calc_dividends = Mock(return_value=30)
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
    firm, *_ = firm_with_roles_and_account
    firm._update_equity_shares = Mock()
    firm.net_worth = 1000
    firm.net_cash_flow = 500
    firm.taxes_payable = 100
    firm.dividends_payable = 200
    firm.account["equities"] = -1000

    # When
    firm.update_net_worth()

    # Then
    firm._update_equity_shares.assert_called_once_with(200)
    assert firm.net_worth == pytest.approx(1200)


def test_update_equity_shares(firm_with_roles_and_account):
    # Given
    founder1, founder2 = Mock(), Mock()
    share1 = {"founder": founder1, "value": 1000}
    share2 = {"founder": founder2, "value": 3000}
    role = Mock()
    role.get_equity_shares.return_value = [share1, share2]
    firm, roles, _ = firm_with_roles_and_account
    roles["company"] = role

    # When
    firm._update_equity_shares(-100)

    # Then
    role.update_equity_share.assert_any_call(founder1, -25)
    role.update_equity_share.assert_any_call(founder2, -75)


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
    founder, role = Mock(), Mock()
    share = {"founder": founder, "value": 1000}
    role.get_equity_shares.return_value = [share]
    firm, roles, _ = firm_with_roles_and_account
    firm.dividends_payable = 200
    roles["company"] = role

    # When
    firm.pay_dividends()

    # Then
    role.pay_dividends.assert_called_with(founder, 200)
    assert firm.dividends_payable == 0


def test_pay_no_dividends(firm_with_roles_and_account):
    # Given
    role = Mock()
    role.get_equity_shares.return_value = []
    firm, roles, _ = firm_with_roles_and_account
    firm.dividends_payable = 0
    roles["company"] = role

    # When
    firm.pay_dividends()

    # Then
    role.get_equity_shares.assert_not_called()
    role.pay_dividends.assert_not_called()


# ---------------------------------------------------
# ENDOGENEOUS EXIT
# ----------------------------------------------------


@pytest.fixture
def before_exit(firm_with_roles_and_account):
    # Given
    borrower_role, company_role = Mock(), Mock()
    borrower_role.find_loans.return_value = []
    company_role.get_equity_shares.return_value = []
    firm, roles, account = firm_with_roles_and_account
    firm.net_worth = 50
    roles["company"] = company_role
    roles["borrower"] = borrower_role
    roles["employer"] = Mock(wage=100)
    roles["depositor"] = Mock()
    account["deposits"] = 0
    account["loans"] = 0
    account["cash"] = 0
    return firm, roles, account


@pytest.mark.parametrize("net_worth, defaulted", [(90, True), (150, False)])
def test_exit_when_bankrupt(before_exit, net_worth, defaulted):
    # Given
    firm, *_ = before_exit
    firm.net_worth = net_worth

    # When
    firm.exit()

    # Then
    assert firm.defaulted == defaulted


def test_exit_withdraws_residual_deposits(before_exit):
    # Given
    firm, roles, account = before_exit
    account["deposits"] = 100
    role = roles["depositor"]

    # When
    firm.exit()

    # Then
    role.withdraw_deposits.assert_called_with(100)


def test_exit_doesnt_withdraw_with_no_deposit(before_exit):
    # Given
    firm, roles, account = before_exit
    account["deposits"] = 0
    role = roles["depositor"]

    # When
    firm.exit()

    # Then
    role.withdraw_deposits.assert_not_called()


def test_exit_makes_default_on_all_loans(before_exit):
    # Given
    lender = object()
    loan = {"lender": lender, "amount": 100, "rate": 0.1}
    firm, roles, _ = before_exit
    role = roles["borrower"]
    role.find_loans.return_value = [loan]

    # When
    firm.exit()

    # Then
    role.make_defaults.assert_called_with(lender, 100)


def test_exit_doesnt_make_default_with_no_loans(before_exit):
    # Given
    firm, roles, _ = before_exit
    role = roles["borrower"]
    role.find_loans.return_value = []

    # When
    firm.exit()

    # Then
    role.make_defaults.assert_not_called()


def test_exit_transfer_residual_cash_to_founders(before_exit):
    # Given
    founder = object()
    share = {"founder": founder, "value": 1000}
    firm, roles, account = before_exit
    account["cash"] = 200
    role = roles["company"]
    role.get_equity_shares.return_value = [share]

    # When
    firm.exit()

    # Then
    role.transfer_residual_cash.assert_called_with(founder, 200)


def test_exit_sets_all_roles_defaulted(before_exit):
    # Given
    firm, roles, _ = before_exit
    firm.net_worth = 90
    roles["any"] = Mock()

    # When
    firm.exit()

    # Then
    for role in roles.values():
        assert role.defaulted is True
