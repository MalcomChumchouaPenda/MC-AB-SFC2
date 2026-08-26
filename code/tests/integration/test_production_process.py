from unittest.mock import Mock
from mc_ab_sfc.agents import Firm


def test_production_planning_pipeline():
    # Given
    model = Mock()
    model.p.theta = 0.20
    firm = Firm(model)
    firm.expected_sales = 150
    firm.inventories = 30
    firm.productivity = 3
    firm.p.theta = 0.20

    # When
    firm.plan_production()

    # Then
    assert firm.desired_output == 150
    assert firm.desired_labor == 50
