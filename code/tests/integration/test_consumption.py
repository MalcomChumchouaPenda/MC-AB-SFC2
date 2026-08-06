from dataclasses import dataclass, field
import pytest
from agentpy import Model
from mc_ab_sfc.agents import HouseholdAgent
from mc_ab_sfc.spaces import GoodsMarket


@pytest.fixture
def model():
    # Given
    return Model(
        {
            "psi": 2,
            "beta": 1,
        }
    )


@pytest.fixture
def household(model):
    # Given
    household = HouseholdAgent(model)
    household.position = 0
    household.cash = 100
    household.tradable_cons = 0
    household.non_tradable_cons = 0
    household.desired_trad_cons = 60
    household.desired_non_trad_cons = 40
    return household


@dataclass
class FakeFirm:
    id: int
    position: float = 0.5
    price: float = 10
    inventories: float = 10
    cash: float = 0
    sales: float = 0
    roles: object = field(default_factory=dict)


def test_consumer_buy_tradable_goods(model, household):
    # Given
    firm = FakeFirm(2)
    market = GoodsMarket(model, tradable=True)
    consumer = market.add_consumer(household)
    producer = market.add_producer(firm)

    # When
    consumer.buy_goods([producer])

    # Then
    assert household.cash == pytest.approx(40)
    assert household.tradable_cons == pytest.approx(60)
    assert household.non_tradable_cons == 0
    assert firm.cash == pytest.approx(60)
    assert firm.sales == pytest.approx(60)
    assert firm.inventories == pytest.approx(4)


def test_consumer_buy_non_tradable_goods(model, household):
    # Given
    firm = FakeFirm(2)
    market = GoodsMarket(model, tradable=False)
    consumer = market.add_consumer(household)
    producer = market.add_producer(firm)

    # When
    consumer.buy_goods([producer])

    # Then
    assert household.cash == pytest.approx(60)
    assert household.non_tradable_cons == pytest.approx(40)
    assert household.tradable_cons == 0
    assert firm.cash == pytest.approx(40)
    assert firm.sales == pytest.approx(40)
    assert firm.inventories == pytest.approx(6)


def test_household_consumes_tradable_and_non_tradable_goods(model, household):
    # Given
    firm1, firm2 = FakeFirm(2), FakeFirm(3)
    trad_market = GoodsMarket(model, tradable=True)
    trad_market.add_consumer(household)
    trad_market.add_producer(firm1)
    trad_market.average_price = 10
    non_trad_market = GoodsMarket(model, tradable=False)
    non_trad_market.add_consumer(household)
    non_trad_market.add_producer(firm2)
    non_trad_market.average_price = 15

    # When
    household.consume()

    # Then
    assert firm1.sales > 0
    assert firm2.sales > 0
