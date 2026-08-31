import pytest
from unittest.mock import Mock
from model.agents.private import Household, Firm
from model.spaces.real import GoodsMarket


@pytest.fixture
def model():
    # Given
    model = Mock()
    model.p.psi = 2
    model.p.beta = 1
    random = model.random
    random.sample = Mock(side_effect=lambda pop, k: pop[:k])
    return model


@pytest.fixture
def household(model):
    # Given
    household = Household(model)
    household.cash = 100
    household.desired_trad_cons = 60
    household.desired_non_trad_cons = 40
    return household


@pytest.fixture
def firm(model):
    # Given
    firm = Firm(model)
    firm.price = 10
    firm.position = 0.5
    firm.inventories = 10
    return firm


def test_consumer_buy_tradable_goods(model, household, firm):
    # Given
    market = GoodsMarket(model, tradable=True)
    market.average_price = 10
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
    market.average_price = 10
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


@pytest.fixture
def firms(model):
    # Given
    firms = []
    for _ in range(2):
        firm = Firm(model)
        firm.price = 10
        firm.position = 0.5
        firm.inventories = 10
        firms.append(firm)
    return firms


@pytest.fixture
def markets(model):
    markets = []
    for tradable in [True, False]:
        market = GoodsMarket(model, tradable=tradable)
        market.average_price = 10
        markets.append(market)
    return markets


def test_household_consumes_trad_and_non_trad_goods(household, firms, markets):
    # Given
    for firm, market in zip(firms, markets):
        market.add_consumer(household)
        market.add_supplier(firm)

    # When
    household.consume()

    # Then
    assert firms[0].sales > 0
    assert firms[1].sales > 0
