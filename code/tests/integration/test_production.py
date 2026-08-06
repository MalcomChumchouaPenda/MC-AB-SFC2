from agentpy import Model
from mc_ab_sfc.agents import FirmAgent


def test_production_planning_pipeline():
    # Given
    model = Model({"theta": 0.20})
    firm = FirmAgent(model)
    firm.expected_sales = 150
    firm.inventories = 30
    firm.productivity = 3
    firm.p.theta = 0.20

    # When
    firm.plan_production()

    # Then
    assert firm.desired_output == 150
    assert firm.desired_labor == 50
