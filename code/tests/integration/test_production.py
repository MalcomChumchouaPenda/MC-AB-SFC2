import pytest
from unittest.mock import Mock
from model.base import EcoAccount
from model.agents.firm import Firm


@pytest.fixture
def model():
    # Given
    model = Mock()
    model.p.theta = 0.20
    return model


@pytest.fixture
def firm(model):
    # Given
    firm = Firm(model)
    firm.setup()
    firm.roles["producer"] = Mock()
    return firm


def test_production_planning_pipeline(firm):
    # Given
    firm.expected_sales = 150
    role = firm.roles["producer"]
    role.inventories = 30
    role.productivity = 3

    # When
    firm.plan_production()

    # Then
    assert firm.desired_output == 150
    assert firm.desired_labor == 50
