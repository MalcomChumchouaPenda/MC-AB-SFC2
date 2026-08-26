import pytest
from unittest.mock import Mock
from mc_ab_sfc.agents import NationalCentralBank, UnionCentralBank
from mc_ab_sfc.spaces import GoodsMarket


@pytest.fixture
def model():
    # Given
    model = Mock()
    model.p.xi = 0.5
    model.p.xi_deltap = 1.5
    model.p.long_run_rate = 0.02
    model.p.inflation_target = 0.02
    return model


@pytest.fixture
def goods_markets(model):
    # Given
    markets = {}
    for n in range(5):
        market = GoodsMarket(model)
        market.setup()
        market.inflation = 0.04
        market.gdp = 100
        markets[n] = market
    model.national_goods_markets = markets
    return markets


@pytest.fixture
def union_cb(model):
    cb = UnionCentralBank(model)
    cb.setup()
    cb.prev_discount_rate = 0.03
    cb.average_inflation = 0.0
    return cb


@pytest.fixture
def national_cb(model):
    cb = NationalCentralBank(model)
    cb.setup()
    return cb


@pytest.mark.usefixtures("goods_markets")
def test_central_banks_updates_discount_rate(union_cb, national_cb):
    # Given
    national_cb.union_bank = union_cb

    # When
    union_cb.update_discount_rate()

    # Then
    assert union_cb.discount_rate == pytest.approx(0.04)
    assert national_cb.discount_rate == pytest.approx(0.04)
