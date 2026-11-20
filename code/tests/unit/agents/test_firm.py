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

    # Then
    assert issubclass(Firm, EcoAgent)


@pytest.fixture
def model(fake_model):
    # Given
    model = fake_model
    model.random = Mock()
    model.nprandom = Mock()
    return model


@pytest.fixture
def firm(model):
    # Given
    return Firm(model)


def test_initializes_tradable(firm):
    # Then
    assert firm.tradable is False


def test_initializes_defaulted(firm):
    # Then
    assert firm.defaulted is False


def test_initializes_expected_sales(firm):
    # Then
    assert firm.expected_sales == 0


def test_initializes_desired_labor(firm):
    # Then
    assert firm.desired_labor == 0


def test_initializes_desired_output(firm):
    # Then
    assert firm.desired_output == 0


def test_initializes_desired_loans(firm):
    # Then
    assert firm.desired_loans == 0


def test_initializes_desired_rd_expense(firm):
    # Then
    assert firm.desired_rd == 0


def test_initializes_taxes_payable(firm):
    # Then
    assert firm.taxes_payable == 0


def test_initializes_dividends_payable(firm):
    # Then
    assert firm.dividends_payable == 0


def test_initializes_net_cash_flow(firm):
    # Then
    assert firm.net_cash_flow == 0.0


def test_initializes_prev_sales(firm):
    # Then
    assert firm.prev_sales == 0


def test_initializes_prev_output(firm):
    # Then
    assert firm.prev_output == 0


def test_initializes_prev_expected_sales(firm):
    # Then
    assert firm.prev_expected_sales == 0


def test_initializes_prev_inventories(firm):
    # Then
    assert firm.prev_inventories == 0


def test_initializes_prev_labor(firm):
    # Then
    assert firm.prev_labor == 0


def test_initializes_prev_desired_labor(firm):
    # Then
    assert firm.prev_desired_labor == 0


# ---------------------------------------------------
# PRODUCTION PLANNING
# ----------------------------------------------------


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
def account(firm):
    # Given
    account = {}
    firm.account = account
    return account


@pytest.fixture
def producer_role(firm):
    # Given
    role = Mock()
    firm.roles["producer"] = role
    return role


@pytest.fixture
def firm_before_planning(firm, producer_role, account):
    # Given
    producer_role.inventories = 0
    account["inventories"] = 0
    return firm


@pytest.mark.parametrize("inv, expected", [(20, 100), (50, 70)])
def test_calc_desired_output(firm_before_planning, producer_role, inv, expected):
    # Given
    firm = firm_before_planning
    firm.expected_sales = 100
    firm.p.theta = 0.20
    producer_role.inventories = inv

    # When
    desired_output = firm._calc_desired_output()

    # Then
    assert desired_output == expected
    assert firm.desired_output == expected


def test_calc_labor_demand(firm_before_planning, producer_role):
    # Given
    firm = firm_before_planning
    firm.desired_output = 100
    producer_role.phi = 2

    # When
    labor = firm._calc_labor_demand()

    # Then
    assert labor == 50
    assert firm.desired_labor == 50


def test_calc_desired_output_cannot_be_negative(firm_before_planning, producer_role):
    # Given
    firm = firm_before_planning
    firm.expected_sales = 50
    firm.p.theta = 0.10
    producer_role.inventories = 100

    # When
    firm._calc_desired_output()

    # Then
    assert firm.desired_output == 0


# ---------------------------------------------------
# PRICES AND EXPECTATIONS
# ----------------------------------------------------


@pytest.fixture
def before_pricing(firm, producer_role, account):
    firm.expected_sales = 100
    firm.p.delta = 0.1
    producer_role.phi = 2
    producer_role.price = 10
    account["wages"] = -10
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


@pytest.fixture
def employer_role(firm):
    # Given
    role = Mock()
    firm.roles["employer"] = role
    return role


def test_calc_revision_probability(firm, employer_role):
    # Given
    firm.p.upsilon = 1.0
    employer_role.get_unemployment.return_value = 0.1

    # When
    result = firm._calc_revision_probability()

    # Then
    assert result == math.exp(-1.0 * 0.1)


@pytest.fixture
def firm_before_hiring(firm, employer_role):
    # Given
    employer_role.wage = 10.0
    firm._calc_revision_probability = Mock(return_value=0)
    firm.model.nprandom = Mock()
    firm.p.delta = 0.9
    return firm


def test_increases_wage_when_labor_shortage(firm_before_hiring, employer_role):
    # Given
    firm = firm_before_hiring
    firm.prev_labor = 80
    firm.prev_desired_labor = 100
    random = firm.model.nprandom
    random.choice.return_value = 1
    random.uniform.return_value = 0.05

    # When
    firm.revise_wage_offer()

    # Then
    random.uniform.assert_called_with(0, firm.p.delta)
    assert employer_role.wage > 10.0


def test_increases_wage_with_upward_revision_prob(firm_before_hiring):
    # Given
    firm = firm_before_hiring
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


def test_can_choose_to_not_increases_wage(firm_before_hiring, employer_role):
    # Given
    firm = firm_before_hiring
    firm.prev_labor = 80
    firm.prev_desired_labor = 100
    random = firm.model.nprandom
    random.choice.return_value = 0
    random.uniform.return_value = 0.05

    # When
    firm.revise_wage_offer()

    # Then
    random.uniform.assert_not_called()
    assert employer_role.wage == 10.0


def test_decreases_wage_when_all_positions_filled(firm_before_hiring, employer_role):
    # Given
    firm = firm_before_hiring
    firm.prev_labor = 100
    firm.prev_desired_labor = 100
    random = firm.model.nprandom
    random.choice.return_value = 1
    random.uniform.return_value = 0.05

    # When
    firm.revise_wage_offer()

    # Then
    random.uniform.assert_called_with(0, firm.p.delta)
    assert employer_role.wage < 10.0


def test_decreases_wage_with_downward_revision_prob(firm_before_hiring):
    # Given
    firm = firm_before_hiring
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


def test_can_choose_to_not_decreases_wage(firm_before_hiring, employer_role):
    # Given
    firm = firm_before_hiring
    firm.prev_labor = 100
    firm.prev_desired_labor = 100
    random = firm.model.nprandom
    random.choice.return_value = 0
    random.uniform.return_value = 0.05

    # When
    firm.revise_wage_offer()

    # Then
    random.uniform.assert_not_called()
    assert employer_role.wage == 10.0


# ---------------------------------------------------
# R & D INVESTMENTS
# ----------------------------------------------------


def test_calc_desired_rd(firm, employer_role):
    # Given
    firm.p.gamma = 0.1
    firm.desired_labor = 50
    employer_role.wage = 10

    # When
    rd = firm.calc_desired_rd()

    # Then
    assert rd == 50
    assert firm.desired_wage_bill == 500
    assert firm.desired_rd == 50


@pytest.fixture
def firm_before_rd(firm, employer_role, account):
    # Given
    employer_role.labor = 50.0
    account["loans"] = -200
    return firm


def test_execute_rd_launchs_innovation_if_no_constraints(firm_before_rd, producer_role):
    # Given
    firm = firm_before_rd
    firm.desired_rd = 100
    firm.desired_labor = 50
    firm.desired_loans = 200

    # When
    firm.execute_rd()

    # Then
    producer_role.execute_rd.assert_called_with(100)


def test_execute_rd_does_nothing_if_no_desire(firm_before_rd, producer_role):
    # Given
    firm = firm_before_rd
    firm.desired_rd = 0
    firm.desired_labor = 100
    firm.desired_loans = 200

    # When
    firm.execute_rd()

    # Then
    producer_role.execute_rd.assert_not_called()


def test_execute_rd_does_nothing_if_labor_constraint(firm_before_rd, producer_role):
    # Given
    firm = firm_before_rd
    firm.desired_rd = 100
    firm.desired_labor = 100
    firm.desired_loans = 200

    # When
    firm.execute_rd()

    # Then
    producer_role.execute_rd.assert_not_called()


def test_execute_rd_does_nothing_if_financial_constraint(firm_before_rd, producer_role):
    # Given
    firm = firm_before_rd
    firm.desired_rd = 100
    firm.desired_labor = 50
    firm.desired_loans = 200
    firm.account["loans"] = -100

    # When
    firm.execute_rd()

    # Then
    producer_role.execute_rd.assert_not_called()


# ---------------------------------------------------
# PRODUCTION
# ----------------------------------------------------


def test_produce_goods_with_job_quantity(firm, employer_role, producer_role):
    # Given
    employer_role.labor = 0.9

    # When
    firm.produce_goods()

    # Then
    producer_role.produce_goods.assert_called_with(0.9)


# ---------------------------------------------------
# CREDIT DEMAND
# ----------------------------------------------------


@pytest.fixture
def firm_before_loan(firm, employer_role, account):
    # Given
    firm.desired_labor = 10
    firm.desired_rd = 50
    account["deposits"] = 0
    employer_role.wage = 10
    return firm


def test_calc_desired_loans_when_external_finance_needed(firm_before_loan):
    # Given
    firm = firm_before_loan
    firm.account["deposits"] = 20

    # When
    result = firm._calc_desired_loans()

    # Then
    assert result == 130


def test_calc_desired_loans_if_sufficient_internal_funds(firm_before_loan):
    # Given
    firm = firm_before_loan
    firm.account["deposits"] = 150

    # When
    result = firm._calc_desired_loans()

    # Then
    assert result == 0


@pytest.fixture
def company_role(firm):
    # Given
    role = Mock()
    firm.roles["company"] = role
    return role


@pytest.fixture
def borrower_role(firm):
    # Given
    role = Mock()
    firm.roles["borrower"] = role
    return role


@pytest.fixture
def firm_before_credit(firm, account, borrower_role):
    # Given
    account["equities"] = -100
    borrower_role.find_lenders.return_value = []
    firm._calc_desired_loans = Mock(return_value=10)
    return firm


def test_request_loans_to_all_lenders(firm_before_credit, borrower_role):
    # Given
    lender = Mock()
    firm = firm_before_credit
    borrower_role.find_lenders.return_value = [lender]

    # When
    firm.request_loans()

    # Then
    borrower_role.request_loans.assert_any_call(lender)


def test_request_loans_and_set_loan_demand(firm_before_credit, borrower_role):
    # Given
    firm = firm_before_credit
    firm._calc_desired_loans.return_value = 100
    borrower_role.find_lenders.return_value = [Mock()]

    # When
    firm.request_loans()

    # Then
    assert borrower_role.loan_demand == 100


def test_request_loans_and_registers_desired_loans(firm_before_credit):
    # Given
    firm = firm_before_credit
    firm._calc_desired_loans.return_value = 100

    # When
    firm.request_loans()

    # Then
    assert firm.desired_loans == 100


@pytest.mark.parametrize("desired", [0, -100])
def test_dont_request_unneccessary_loans(firm_before_credit, borrower_role, desired):
    # Given
    firm = firm_before_credit
    firm._calc_desired_loans.return_value = desired

    # When
    firm.request_loans()

    # Then
    borrower_role.request_loans.assert_not_called()


# ---------------------------------------------------
# CREDIT AND LOAN REPAYMENT
# ----------------------------------------------------


@pytest.fixture
def deposit_bank():
    # Given
    return Mock(country_pos=1)


@pytest.fixture
def depositor_role(firm):
    # Given
    role = Mock()
    firm.roles["country_1_depositor"] = role
    return role


@pytest.fixture
def deposit(deposit_bank, depositor_role, account):
    # Given
    deposit = {"deposit_bank": deposit_bank, "amount": 100}
    depositor_role.find_deposits.return_value = [deposit]
    account["deposits"] = 100
    return deposit


@pytest.fixture
def loan(deposit_bank, borrower_role, account):
    # Given
    loan = {"lender": deposit_bank, "amount": 100, "rate": 0.1}
    borrower_role.find_loans.return_value = [loan]
    account["loans"] = -100
    return loan


@pytest.mark.parametrize("cash, expected", [(100, 80), (50, 50), (0, 0)])
def test_repay_loans_makes_deposit(firm, loan, deposit, depositor_role, cash, expected):
    # Given
    firm.account["cash"] = cash
    deposit["amount"] = 20
    lender = loan["lender"]

    # When
    firm.repay_loans()

    # Then
    depositor_role.make_deposits.assert_called_once_with(lender.id, expected)


def test_repay_loans_to_all_lenders(firm, loan, deposit, borrower_role):
    # Given
    firm.account["cash"] = 100
    deposit["amount"] = 200
    lender = loan["lender"]

    # When
    firm.repay_loans()

    # Then
    borrower_role.repay_loans.assert_called_once_with(lender, 100, 10.0)


@pytest.mark.parametrize("fund, default", [(100, 0), (80, 20), (0, 100)])
def test_repay_loans_makes_default(firm, loan, deposit, borrower_role, fund, default):
    # Given
    firm.account["cash"] = 0
    deposit["amount"] = fund
    lender = loan["lender"]

    # When
    firm.repay_loans()

    # Then
    borrower_role.repay_loans.assert_called_once_with(lender, fund, 0.0)
    borrower_role.make_defaults.assert_called_once_with(lender, default)


# ---------------------------------------------------
# WAGES PAYMENT
# ---------------------------------------------------


def test_pay_wages_by_job(firm, employer_role):
    # Given
    worker = Mock()
    job = {"worker": worker, "quantity": 0.5}
    employer_role.get_jobs.return_value = [job]
    employer_role.wage = 2.0

    # When
    firm.pay_wages()

    # Then
    employer_role.pay_wages.assert_called_with(worker, 1.0)


# ---------------------------------------------------
# PROFITS, TAXES AND DIVIDENDS COMPUTATION
# ----------------------------------------------------


@pytest.mark.parametrize("sales, expected", [(600, 200), (200, -200)])
def test_calc_net_cash_flow(firm, account, sales, expected):
    # Given
    account["consumption"] = sales
    account["loan_interests"] = -20
    account["wages"] = -390
    account["dep_interests"] = 10

    # When
    net_cash_flow = firm._calc_net_cash_flow()

    # Then
    assert net_cash_flow == expected


def test_calc_profit(firm, employer_role, producer_role):
    # Given
    firm.net_cash_flow = 200
    firm.prev_inventories = 50
    employer_role.wage = 20
    producer_role.phi = 2
    producer_role.inventories = 60

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


@pytest.mark.parametrize("taxable, expected", [(100, 20), (-100, 0)])
def test_calc_taxes(firm, company_role, taxable, expected):
    # Given
    firm.net_cash_flow = taxable
    company_role.get_tax_rate.return_value = 0.20

    # When
    taxes = firm._calc_taxes()

    # Then
    assert taxes == expected


@pytest.mark.parametrize("taxable, taxes, expected", [(100, 20, 40), (-100, 0, 0)])
def test_calc_dividends(firm, taxable, taxes, expected):
    # Given
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


def test_update_production_history(firm, producer_role):
    # Given
    producer_role.output = 100
    producer_role.sales = 100
    producer_role.inventories = 10
    firm.expected_sales = 120

    # When
    firm.update_production_history()

    # Then
    assert firm.prev_expected_sales == 120
    assert firm.prev_output == 100
    assert firm.prev_sales == 100
    assert firm.prev_inventories == 10


def test_update_net_worth(firm, company_role):
    # Given
    firm.net_cash_flow = 500
    firm.taxes_payable = 100
    firm.dividends_payable = 200

    # When
    firm.update_net_worth()

    # Then
    company_role.update_equity_shares.assert_called_once_with(200)


# ---------------------------------------------------
# TAXES AND DIVIDENDS PAYMENTS
# ----------------------------------------------------


def test_pay_taxes_uses_company_role(firm, company_role):
    # Given
    firm.taxes_payable = 100

    # When
    firm.pay_taxes()

    # Then
    company_role.pay_taxes.assert_called_with(100)


def test_pay_taxes_reduces_taxes_payable(firm, company_role):
    # Given
    firm.taxes_payable = 100

    # When
    firm.pay_taxes()

    # Then
    assert firm.taxes_payable == 0


def test_pay_no_taxes_if_no_taxes_payable(firm, company_role):
    # Given
    firm.taxes_payable = 0

    # When
    firm.pay_taxes()

    # Then
    company_role.pay_taxes.assert_not_called()


def test_pay_dividends_uses_company_role(firm, company_role):
    # Given
    founder = Mock()
    share = {"citizen": founder, "value": 1000}
    company_role.get_equity_shares.return_value = [share]
    firm.dividends_payable = 200

    # When
    firm.pay_dividends()

    # Then
    company_role.pay_dividends.assert_called_with(founder, 200)


def test_pay_dividends_reduces_dividends_payable(firm, company_role):
    # Given
    firm.dividends_payable = 200
    share = {"citizen": Mock(), "value": 1000}
    company_role.get_equity_shares.return_value = [share]

    # When
    firm.pay_dividends()

    # Then
    assert firm.dividends_payable == 0


def test_pay_no_dividends_if_dividends_payable(firm, company_role):
    # Given
    firm.dividends_payable = 0
    company_role.get_equity_shares.return_value = []

    # When
    firm.pay_dividends()

    # Then
    company_role.pay_dividends.assert_not_called()


# ---------------------------------------------------
# ENDOGENEOUS EXIT
# ----------------------------------------------------


@pytest.fixture
def firm_before_exit(firm, account, borrower_role, company_role, employer_role):
    # Given
    account["equities"] = -50
    account["deposits"] = 0
    account["loans"] = 0
    account["cash"] = 0
    company_role.get_equity_shares.return_value = []
    borrower_role.find_loans.return_value = []
    employer_role.wage = 100
    return firm


@pytest.mark.parametrize("net_worth, defaulted", [(90, True), (150, False)])
def test_exit_when_bankrupt(firm_before_exit, account, net_worth, defaulted):
    # Given
    firm = firm_before_exit
    account["equities"] = -net_worth
    print(firm.roles)

    # When
    firm.exit()

    # Then
    assert firm.defaulted == defaulted


def test_exit_withdraws_residual_deposits(firm_before_exit, deposit, depositor_role):
    # Given
    firm = firm_before_exit
    firm.account["deposits"] = 100
    deposit_bank = deposit["deposit_bank"]
    amount = deposit["amount"]

    # When
    firm.exit()

    # Then
    depositor_role.withdraw_deposits.assert_called_with(deposit_bank.id, amount)


def test_exit_doesnt_withdraw_with_no_deposit(firm_before_exit, depositor_role):
    # Given
    firm = firm_before_exit
    firm.account["deposits"] = 0

    # When
    firm.exit()

    # Then
    depositor_role.withdraw_deposits.assert_not_called()


def test_exit_makes_default_on_all_loans(firm_before_exit, borrower_role, loan):
    # Given
    lender = loan["lender"]
    amount = loan["amount"]
    firm = firm_before_exit

    # When
    firm.exit()

    # Then
    borrower_role.make_defaults.assert_called_with(lender, amount)


def test_exit_doesnt_make_default_with_no_loans(firm_before_exit, borrower_role):
    # Given
    firm = firm_before_exit
    borrower_role.find_loans.return_value = []

    # When
    firm.exit()

    # Then
    borrower_role.make_defaults.assert_not_called()


def test_exit_transfer_residual_cash_to_founders(firm_before_exit, company_role):
    # Given
    founder = object()
    share = {"citizen": founder, "value": 1000}
    firm = firm_before_exit
    firm.account["cash"] = 200
    company_role.get_equity_shares.return_value = [share]

    # When
    firm.exit()

    # Then
    company_role.transfer_residual_cash.assert_called_with(founder, 200)


def test_exit_sets_all_roles_defaulted(firm_before_exit):
    # Given
    firm = firm_before_exit
    firm.roles["any"] = Mock()

    # When
    firm.exit()

    # Then
    for role in firm.roles.values():
        assert role.defaulted is True


# ---------------------------------------------------
#  OBSERVATION
# ----------------------------------------------------


@pytest.fixture
def firm_before_record(
    firm,
    borrower_role,
    company_role,
    employer_role,
    producer_role,
):
    # Given
    producer_role.phi = 1.5
    return firm


def test_record_indicators_records_productivity(firm_before_record, producer_role):
    # Given
    firm = firm_before_record

    # When
    firm.record_indicators()

    # Then
    assert firm.log["phi"][-1] == producer_role.phi
