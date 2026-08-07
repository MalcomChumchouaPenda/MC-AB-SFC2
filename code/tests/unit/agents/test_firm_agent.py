import math
import pytest
from unittest.mock import Mock
from mc_ab_sfc.agents import FirmAgent

# ---------------------------------------------------
# ARCHITECTURAL TESTS
# ----------------------------------------------------


def test_is_ecoagent():
    # Given
    from mc_ab_sfc.base import EcoAgent

    # Assert
    assert issubclass(FirmAgent, EcoAgent)


# ---------------------------------------------------
# PRODUCTION TESTS
# ----------------------------------------------------


@pytest.fixture
def firm():
    # Given
    model = Mock()
    firm = FirmAgent(model)
    return firm


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
    firm = FirmAgent(model)
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
    firm = FirmAgent(model)
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
    firm = FirmAgent(model)
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
    firm = FirmAgent(model)
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
    firm = FirmAgent(model)
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
    firm = FirmAgent(model)
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
    firm = FirmAgent(model)
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
    firm = FirmAgent(model)
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
    firm.tradable = True
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
    firm = FirmAgent(model)
    firm.calc_desired_rd = Mock(side_effect=setattr(firm, "desired_rd", 100))
    firm.execute_rd = Mock(side_effect=setattr(firm, "rd", 100))
    firm.calc_rd_success_probability = Mock(return_value=0.6)
    return firm


def test_update_productivity_with_multi_steps(innovating_firm):
    # Given
    firm = innovating_firm
    firm.productivity = 10
    firm.average_productivity = 10
    random = firm.model.nprandom
    random.choice.return_value = 1
    random.uniform.return_value = 0.05

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
    firm.average_productivity = 10
    random = firm.model.nprandom
    random.choice.return_value = 0

    # When
    firm.update_productivity()

    # Then
    assert firm.productivity == 10


def test_update_productivity_by_innovation(innovating_firm):
    # Given
    firm = innovating_firm
    firm.productivity = 10
    firm.average_productivity = 10
    random = firm.model.nprandom
    random.choice.return_value = 1
    random.uniform = lambda a, b: b

    # When
    firm.update_productivity()

    # Then
    assert firm.productivity == 12


def test_update_productivity_by_imitation(innovating_firm):
    # Given
    firm = innovating_firm
    firm.productivity = 10
    firm.average_productivity = 20
    random = firm.model.nprandom
    random.choice.return_value = 1
    random.uniform = lambda a, b: b

    # When
    firm.update_productivity()

    # Then
    assert firm.productivity == 20


# ---------------------------------------------------
# HISTORIC DATA STORAGE TESTS
# ----------------------------------------------------


@pytest.fixture
def firm_with_history():
    # Given
    model = Mock()
    firm = FirmAgent(model)
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
