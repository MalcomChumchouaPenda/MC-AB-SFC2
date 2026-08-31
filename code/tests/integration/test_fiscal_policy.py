import pytest
from unittest.mock import Mock
from model.spaces.real import GoodsMarket
from model.agents.public import Government


@pytest.fixture
def model():
    # Given
    model = Mock()
    model.p.dmax = 0.05
    model.p.tax_min = 0.10
    model.p.tax_max = 0.50
    model.p.g_min = 0.05
    model.p.g_max = 0.20
    model.p.delta = 0.10
    model.random.uniform.return_value = 0.05
    return model


@pytest.fixture
def govt(model):
    # Given
    govt = Government(model)
    govt.setup()
    govt.country = "any"
    govt.prev_public_spending = 10
    govt.public_spending = 100
    govt.budget_deficit = 100
    govt.tax_rate = 0.20
    govt.gdp = 1000
    return govt


@pytest.fixture
def goods_market(model):
    # Given
    goods_market = GoodsMarket(model)
    goods_market.setup()
    model.goods_markets = {"any": goods_market}
    return goods_market


def test_government_updates_fiscal_policy(govt, goods_market):
    # Given
    goods_market.average_price = 2
    goods_market.average_productivity = 3

    # When
    govt.update_fiscal_policy()

    # Then
    assert govt.desired_public_spending == pytest.approx(60)
    assert govt.public_spending == pytest.approx(95)
    assert govt.tax_rate == pytest.approx(0.21)
