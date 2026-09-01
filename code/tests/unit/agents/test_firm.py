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
def firm():
    # Given
    model = Mock()
    firm = Firm(model)
    return firm


def test_has_default_stocks(firm):
    # Assert
    assert firm.cash == 0
    assert firm.inventories == 0
    assert firm.loans == 0
    assert firm.equity == 0


def test_has_default_flows(firm):
    # Assert
    assert firm.sales == 0
    assert firm.wage_bill == 0
    assert firm.loan_interest == 0
    assert firm.rd == 0
    assert firm.taxes == 0
    assert firm.dividends == 0


def test_has_default_choices(firm):
    # Assert
    assert firm.price == 0
    assert firm.wage_offer == 0
    assert firm.expected_sales == 0
    assert firm.desired_labor == 0
    assert firm.desired_output == 0
    assert firm.desired_loans == 0
    assert firm.desired_rd == 0
    assert firm.taxes_payable == 0
    assert firm.dividends_payable == 0


def test_has_default_indicators(firm):
    # Assert
    assert firm.country is None
    assert firm.position == 0.0
    assert firm.productivity == 0.0
    assert firm.net_worth == 0.0
    assert firm.net_cash_flow == 0.0
    assert firm.prev_sales == 0
    assert firm.prev_output == 0
    assert firm.prev_expected_sales == 0
    assert firm.prev_inventories == 0
    assert firm.prev_labor == 0
    assert firm.prev_desired_labor == 0


# ---------------------------------------------------
# DERIVED STATE TESTS
# ----------------------------------------------------


def test_expose_deposits_total(firm):
    # Given
    deposits = [{"bank": object(), "amount": 500}]
    deposit_market = Mock()
    deposit_market.get_client_deposits.return_value = deposits
    firm.model.deposit_markets = {"any": deposit_market}

    # Assert
    assert firm.deposits == 500


def test_expose_deposit_interests_total(firm):
    # Given
    deposits = [{"bank": object(), "interests": 50.0}]
    deposit_market = Mock()
    deposit_market.get_client_deposits.return_value = deposits
    firm.model.deposit_markets = {"any": deposit_market}

    # Assert
    assert firm.dep_interests == pytest.approx(50.0)


# ---------------------------------------------------
# PRODUCTION TESTS
# ----------------------------------------------------


def test_calc_desired_output(firm):
    # Given
    firm.expected_sales = 100
    firm.inventories = 20
    firm.p.theta = 0.20

    # When
    desired_output = firm.calc_desired_output()

    # Then
    assert desired_output == 100
    assert firm.desired_output == 100


def test_calc_desired_output_decreases_with_inventories(firm):
    # Given
    firm.expected_sales = 100
    firm.inventories = 50
    firm.p.theta = 0.20

    # When
    firm.calc_desired_output()

    # Then
    assert firm.desired_output == 70


def test_calc_labor_demand(firm):
    # Given
    firm.desired_output = 100
    firm.productivity = 2

    # When
    labor = firm.calc_labor_demand()

    # Then
    assert labor == 50
    assert firm.desired_labor == 50


def test_calc_desired_output_cannot_be_negative(firm):
    # Given
    firm.expected_sales = 50
    firm.inventories = 100
    firm.p.theta = 0.10

    # When
    firm.calc_desired_output()

    # Then
    assert firm.desired_output == 0


def test_plan_production_by_two_steps(firm):
    # Given
    firm.calc_desired_output = Mock(side_effect=setattr(firm, "yD", 10))
    firm.calc_labor_demand = Mock(side_effect=setattr(firm, "yD", firm.yD + 10))

    # When
    firm.plan_production()

    # Then
    assert firm.yD == 20


# ---------------------------------------------------
# PRICES AND EXPECTATIONS TESTS
# ----------------------------------------------------


@pytest.fixture
def pricing_firm():
    model = Mock()
    model.p.delta = 0.1
    firm = Firm(model)
    firm.wage_bill = 10
    firm.productivity = 2
    firm.expected_sales = 100
    firm.price = 10
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


def test_calc_revision_probability():
    # Given
    model = Mock()
    model.p.upsilon = 1.0
    model.p.upsilon_f = 0.9
    employer_role = Mock()
    employer_role.get_unemployment_rate.return_value = 0.1
    firm = Firm(model)
    firm.roles["employer"] = employer_role

    # When
    result = firm.calc_revision_probability()

    # Then
    assert result == 0.9 * math.exp(-1.0 * 0.1)


@pytest.fixture
def hiring_firm():
    # Given
    model = Mock()
    model.p.delta = 0.9
    firm = Firm(model)
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


def test_calc_desired_rd():
    # Given
    model = Mock()
    model.p.gamma = 0.1
    firm = Firm(model)
    firm.wage_offer = 10
    firm.desired_labor = 50

    # When
    rd = firm.calc_desired_rd()

    # Then
    assert rd == 50
    assert firm.desired_wage_bill == 500
    assert firm.desired_rd == 50


def test_execute_rd_without_constraints():
    # Given
    model = Mock()
    firm = Firm(model)
    firm.desired_rd = 100
    firm.desired_labor = 50
    firm.labor = 50
    firm.desired_loans = 200
    firm.loans = 200

    # When
    firm.execute_rd()

    # Then
    assert firm.rd == 100


def test_execute_rd_with_labor_constraint():
    # Given
    model = Mock()
    firm = Firm(model)
    firm.desired_rd = 100
    firm.desired_labor = 100
    firm.labor = 80
    firm.desired_loans = 200
    firm.loans = 200

    # When
    firm.execute_rd()

    # Then
    assert firm.rd == 0


def test_execute_rd_with_financial_constraint():
    # Given
    model = Mock()
    firm = Firm(model)
    firm.desired_rd = 100
    firm.desired_labor = 50
    firm.labor = 50
    firm.desired_loans = 200
    firm.loans = 100

    # When
    firm.execute_rd()

    # Then
    assert firm.rd == 0


@pytest.fixture
def firm_with_rd_project():
    model = Mock()
    model.p.nu = 0.5
    firm = Firm(model)
    firm.rd = 100
    firm.roles["producer"] = Mock()
    return firm


def test_calc_rd_success_probability_tradable(firm_with_rd_project):
    # Given
    firm = firm_with_rd_project
    firm.tradable = True
    producer_role = firm.roles["producer"]
    producer_role.get_average_price.return_value = 20
    producer_role.get_average_productivity.return_value = 10

    # When
    probability = firm.calc_rd_success_probability()

    # Then
    expected = 1 - math.exp(-0.5 * 100 / (20 * 10))
    assert probability == pytest.approx(expected)


def test_calc_rd_success_probability_non_tradable(firm_with_rd_project):
    # Given
    firm = firm_with_rd_project
    firm.tradable = False
    producer_role = firm.roles["producer"]
    producer_role.get_average_price.return_value = 15
    producer_role.get_average_productivity.return_value = 20

    # When
    probability = firm.calc_rd_success_probability()

    # Then
    expected = 1 - math.exp(-0.5 * 100 / (15 * 20))
    assert probability == pytest.approx(expected)


@pytest.fixture
def innovating_firm():
    model = Mock()
    model.p.delta = 0.2
    firm = Firm(model)
    firm.calc_desired_rd = Mock(side_effect=setattr(firm, "desired_rd", 100))
    firm.execute_rd = Mock(side_effect=setattr(firm, "rd", 100))
    firm.calc_rd_success_probability = Mock(return_value=0.6)
    firm.roles["producer"] = Mock()
    return firm


def test_update_productivity_with_multi_steps(innovating_firm):
    # Given
    firm = innovating_firm
    firm.productivity = 10
    random = firm.model.nprandom
    random.choice.return_value = 1
    random.uniform.return_value = 0.05
    producer_role = firm.roles["producer"]
    producer_role.get_average_productivity.return_value = 10

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
    firm.productivity = 10
    random = firm.model.nprandom
    random.choice.return_value = 0
    producer_role = firm.roles["producer"]
    producer_role.get_average_productivity.return_value = 10

    # When
    firm.update_productivity()

    # Then
    assert firm.productivity == 10


def test_update_productivity_by_innovation(innovating_firm):
    # Given
    firm = innovating_firm
    firm.productivity = 10
    random = firm.model.nprandom
    random.choice.return_value = 1
    random.uniform = lambda a, b: b
    producer_role = firm.roles["producer"]
    producer_role.get_average_productivity.return_value = 10

    # When
    firm.update_productivity()

    # Then
    assert firm.productivity == 12


def test_update_productivity_by_imitation(innovating_firm):
    # Given
    firm = innovating_firm
    firm.productivity = 10
    random = firm.model.nprandom
    random.choice.return_value = 1
    random.uniform = lambda a, b: b
    producer_role = firm.roles["producer"]
    producer_role.get_average_productivity.return_value = 20

    # When
    firm.update_productivity()

    # Then
    assert firm.productivity == 20


# ---------------------------------------------------
# CREDIT RELATED TESTS
# ----------------------------------------------------


@pytest.fixture
def mock_deposits(monkeypatch):
    # Given
    mock_deposits = PropertyMock()
    monkeypatch.setattr(Firm, "deposits", mock_deposits)
    return mock_deposits


@pytest.fixture
def borrowing_firm(mock_deposits):
    # Given
    model = Mock()
    firm = Firm(model)
    firm.wage_offer = 10
    firm.desired_labor = 10
    firm.desired_rd = 50
    firm.mock_deposits = mock_deposits
    firm.roles["borrower"] = Mock()
    return firm


def test_calc_desired_loans_when_external_finance_needed(borrowing_firm):
    # Given
    firm = borrowing_firm
    firm.mock_deposits.return_value = 20

    # When
    firm.calc_desired_loans()

    # Then
    assert firm.desired_loans == 130


def test_calc_desired_loans_when_internal_funds_are_sufficient(borrowing_firm):
    # Given
    firm = borrowing_firm
    firm.mock_deposits.return_value = 150

    # When
    firm.calc_desired_loans()

    # Then
    assert firm.desired_loans == 0


def test_request_loan_to_all_lenders(borrowing_firm):
    # Given
    firm = borrowing_firm
    firm.desired_loans = 100
    lenders = [Mock() for _ in range(3)]
    borrower = firm.roles["borrower"]
    borrower.search_lenders.return_value = lenders

    # When
    firm.request_loan()

    # Then
    for lender in lenders:
        borrower.request_loan.assert_any_call(lender)


def test_request_loan_and_set_loan_demand(borrowing_firm):
    # Given
    firm = borrowing_firm
    firm.desired_loans = 100
    borrower = firm.roles["borrower"]
    borrower.search_lenders.return_value = [Mock()]

    # When
    firm.request_loan()

    # Then
    assert borrower.loan_demand == 100


# ---------------------------------------------------
# PROFITS, TAXES AND DIVIDENDS TESTS
# ----------------------------------------------------


@pytest.fixture
def firm_with_dep_interests(monkeypatch):
    # Given
    mock_interests = PropertyMock()
    monkeypatch.setattr(Firm, "dep_interests", mock_interests)
    model = Mock()
    firm = Firm(model)
    return firm, mock_interests


@pytest.mark.parametrize("sales, expected", [(600, 200), (200, -200)])
def test_calc_net_cash_flow(firm_with_dep_interests, sales, expected):
    # Given
    firm, dep_interests = firm_with_dep_interests
    firm.sales = sales
    firm.loan_interest = 20
    firm.wage_bill = 300
    firm.rd = 90
    dep_interests.return_value = 10

    # When
    net_cash_flow = firm.calc_net_cash_flow()

    # Then
    assert net_cash_flow == expected


def test_calc_profit(firm):
    # Given
    firm.net_cash_flow = 200
    firm.inventories = 60
    firm.prev_inventories = 50
    firm.productivity = 2
    firm.wage_offer = 20

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
def firm_with_govt(model_with_govt):
    # Given
    model, govt = model_with_govt
    firm = Firm(model)
    firm.country = "any"
    firm.taxes = 0
    firm.reserves = 0
    return firm, govt


@pytest.mark.parametrize("taxable, expected", [(100, 20), (-100, 0)])
def test_calc_taxes(firm_with_govt, taxable, expected):
    # Given
    firm, govt = firm_with_govt
    firm.net_cash_flow = taxable
    govt.tax_rate = 0.20

    # When
    taxes = firm.calc_taxes()

    # Then
    assert taxes == expected


@pytest.mark.parametrize("taxable, taxes, expected", [(100, 20, 40), (-100, 0, 0)])
def test_calc_dividends(firm, taxable, taxes, expected):
    # Given
    firm.net_cash_flow = taxable
    firm.taxes_payable = taxes
    firm.p.rho = 0.5

    # When
    dividends = firm.calc_dividends()

    # Then
    assert dividends == pytest.approx(expected)


def test_compute_profit_distribution(firm):
    # Given
    firm.calc_net_cash_flow = Mock(return_value=90)
    firm.calc_profit = Mock(return_value=100)
    firm.calc_taxes = Mock(return_value=20)
    firm.calc_dividends = Mock(return_value=30)

    # When
    firm.compute_profit_distribution()

    # Then
    assert firm.profit == 100
    assert firm.net_cash_flow == 90
    assert firm.taxes_payable == 20
    assert firm.dividends_payable == 30


def test_update_net_worth(firm):
    # Given
    issuer = Mock()
    firm.net_worth = 1000
    firm.net_cash_flow = 500
    firm.taxes_payable = 100
    firm.dividends_payable = 200
    firm.roles["equity_issuer"] = issuer

    # When
    firm.update_net_worth()

    # Then
    issuer.update_equity_holdings.assert_called_once_with()
    assert firm.net_worth == pytest.approx(1200)


def test_pay_taxes(firm_with_govt):
    # Given
    firm, govt = firm_with_govt
    firm.taxes_payable = 100

    # When
    firm.pay_taxes()

    # Then
    assert firm.taxes_payable == 0
    assert firm.taxes == 100
    assert firm.cash == -100
    assert govt.taxes == 100
    assert govt.reserves == 100


def test_pay_no_taxes(firm_with_govt):
    # Given
    firm, govt = firm_with_govt
    firm.taxes_payable = 0

    # When
    firm.pay_taxes()

    # Then
    assert firm.taxes_payable == 0
    assert firm.taxes == 0
    assert firm.cash == 0
    assert govt.taxes == 0
    assert govt.reserves == 0


def test_pay_dividends(firm):
    # Given
    issuer = Mock()
    firm.dividends_payable = 200
    firm.roles["equity_issuer"] = issuer

    # When
    firm.pay_dividends()

    # Then
    issuer.distribute_dividends.assert_called_once_with(200)
    assert firm.dividends_payable == 0


def test_pay_no_dividends(firm):
    # Given
    issuer = Mock()
    firm.dividends_payable = 0
    firm.roles["equity_issuer"] = issuer

    # When
    firm.pay_dividends()

    # Then
    issuer.distribute_dividends.assert_not_called()


# ---------------------------------------------------
# ENDOGENEOUS EXIT TESTS
# ----------------------------------------------------


@pytest.fixture
def firm_before_exit():
    model = Mock()
    firm = Firm(model)
    firm.roles = {"equity_issuer": Mock()}
    firm.wage_offer = 100
    return firm


def test_exit_when_bankrupt(firm_before_exit):
    # Given
    firm = firm_before_exit
    firm.net_worth = 90
    issuer = firm.roles["equity_issuer"]

    # When
    firm.exit()

    # Then
    issuer.close_firm.assert_called_once_with(firm)


def test_does_not_exit_when_not_bankrupt(firm_before_exit):
    # Given
    firm = firm_before_exit
    firm.net_worth = 150
    issuer = firm.roles["equity_issuer"]

    # When
    firm.exit()

    # Then
    issuer.close_firm.assert_not_called()


# ---------------------------------------------------
# HISTORIC DATA STORAGE TESTS
# ----------------------------------------------------


@pytest.fixture
def firm_with_history():
    # Given
    model = Mock()
    firm = Firm(model)
    firm.prev_expected_sales = 100
    firm.prev_output = 50
    firm.prev_sales = 50
    firm.prev_inventories = 20

    firm.expected_sales = 120
    firm.output = 100
    firm.sales = 100
    firm.inventories = 10
    return firm


def test_update_history_overwrites_previous_values(firm_with_history):
    # Given
    firm = firm_with_history

    # When
    firm.update_history()

    # Then
    assert firm.prev_expected_sales == 120
    assert firm.prev_output == 100
    assert firm.prev_sales == 100
    assert firm.prev_inventories == 10


def test_update_history_does_not_modify_current_values(firm_with_history):
    # Given
    firm = firm_with_history

    # When
    firm.update_history()

    # Then
    assert firm.expected_sales == 120
    assert firm.output == 100
    assert firm.sales == 100
    assert firm.inventories == 10
