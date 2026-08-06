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
