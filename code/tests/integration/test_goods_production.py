from unittest.mock import Mock
import pytest
from model.agents.firm import Firm
from model.spaces.goods_market import GoodsMarket


@pytest.fixture
def market(fake_model):
    # Given
    model = fake_model
    market = GoodsMarket(model)
    return market


@pytest.fixture
def firm(fake_model, market):
    # Given
    model = fake_model
    model.p.theta = 0.20
    firm = Firm(model)
    market.place_firm(firm)
    return firm


def test_production_planning_pipeline(firm):
    # Given
    firm.expected_sales = 150
    firm.roles["producer"].inventories = 30
    firm.roles["producer"].productivity = 3

    # When
    firm.plan_production()

    # Then
    assert firm.desired_output == 150
    assert firm.desired_labor == 50
