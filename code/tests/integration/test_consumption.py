
import pytest
from agentpy import Model
from mc_ab_sfc.agents import HouseholdAgent, FirmAgent
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


@pytest.fixture
def firm(model):
    # Given
    firm = FirmAgent(model)    
    firm.price = 10
    firm.position = 0.5
    firm.inventories = 10
    return firm


def test_consumer_buy_tradable_goods(model, household, firm):
    # Given
    market = GoodsMarket(model, tradable=True)
    consumer = market.add_consumer(household)
    producer = market.add_supplier(firm)

    # When
    consumer.buy_goods([producer])

    # Then
    assert household.cash == pytest.approx(40)
    assert household.tradable_cons == pytest.approx(60)
    assert household.non_tradable_cons == 0
    assert firm.cash == pytest.approx(60)
    assert firm.sales == pytest.approx(60)
    assert firm.inventories == pytest.approx(4)


def test_consumer_buy_non_tradable_goods(model, household, firm):
    # Given
    market = GoodsMarket(model, tradable=False)
    consumer = market.add_consumer(household)
    producer = market.add_supplier(firm)

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
    firms = []
    for i, tradable in enumerate([True, False]):
        firm = FirmAgent(model)
        firm.price = 10
        firm.position = 0.5
        firm.inventories = 10
        market = GoodsMarket(model, tradable=tradable)
        market.add_consumer(household)
        market.average_price = 10
        market.add_supplier(firm)
        firms.append(firm)

    # When
    household.consume()

    # Then
    assert firms[0].sales > 0
    assert firms[1].sales > 0
