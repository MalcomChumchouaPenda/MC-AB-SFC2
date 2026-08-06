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
    firm.wages = 10
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
