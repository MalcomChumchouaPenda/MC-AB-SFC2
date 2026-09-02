import pytest
from unittest.mock import Mock, PropertyMock
from model.spaces.goods_market import ConsumerRole

# ---------------------------------------------------
# ARCHITECTURE TESTS
# ----------------------------------------------------


def test_is_eco_role():
    # Given
    from model.base import EcoRole

    # Assert
    assert issubclass(ConsumerRole, EcoRole)


# ---------------------------------------------------
# BEHAVIORAL TESTS
# ----------------------------------------------------


@pytest.fixture
def consumer():
    # Given
    market = Mock()
    agent = Mock(id=1)
    return ConsumerRole(agent, market)


def test_search_suppliers(consumer):
    # Given
    suppliers = [Mock() for _ in range(2)]
    market = consumer.space
    market.search_suppliers.return_value = suppliers

    # When
    result = consumer.search_suppliers(psi=3)

    # Then
    market.search_suppliers.assert_called_once_with(3)
    assert result == suppliers


def test_get_average_price(consumer):
    # Given
    market = consumer.space
    market.average_price = 25

    # When
    average_price = consumer.get_average_price()

    # Then
    assert average_price == 25


def test_get_tradable_demand(consumer):
    # Given
    market = consumer.space
    market.tradable = True
    household = consumer.agent
    household.desired_trad_cons = 40
    household.desired_non_trad_cons = 60

    # Assert
    assert consumer.demand == 40


def test_get_non_tradable_demand(consumer):
    # Given
    market = consumer.space
    market.tradable = False
    household = consumer.agent
    household.desired_trad_cons = 40
    household.desired_non_trad_cons = 60

    # Assert
    assert consumer.demand == 60


@pytest.fixture
def consumer_with_demand(monkeypatch):
    # Given
    demand = PropertyMock(return_value=500)
    monkeypatch.setattr(ConsumerRole, "demand", demand)
    market = Mock()
    household = Mock(id=1)
    return ConsumerRole(household, market)


def test_buy_goods_respects_desired_consumption(consumer_with_demand):
    # Given
    consumer = consumer_with_demand
    household = consumer.agent
    household.cash = 1000
    suppliers = [Mock(price=10, available_quantity=25) for _ in range(3)]

    # When
    consumer.buy_goods(suppliers)

    # Then
    market = consumer.space
    market.buy_goods.assert_any_call(consumer, suppliers[0], pytest.approx(25))
    market.buy_goods.assert_any_call(consumer, suppliers[1], pytest.approx(25))
    assert market.buy_goods.call_count == 2


def test_buy_goods_respects_supply_constraints(consumer_with_demand):
    # Given
    consumer = consumer_with_demand
    household = consumer.agent
    household.cash = 1000
    suppliers = [Mock(price=10, available_quantity=10) for _ in range(2)]

    # When
    consumer.buy_goods(suppliers)

    # Then
    market = consumer.space
    market.buy_goods.assert_any_call(consumer, suppliers[0], pytest.approx(10))
    market.buy_goods.assert_any_call(consumer, suppliers[1], pytest.approx(10))


def test_buy_goods_respects_monetary_constraints(consumer_with_demand):
    # Given
    consumer = consumer_with_demand
    household = consumer.agent
    household.cash = 300
    suppliers = [Mock(price=10, available_quantity=25) for _ in range(2)]

    # When
    consumer.buy_goods(suppliers)

    # Then
    market = consumer.space
    market.buy_goods.assert_any_call(consumer, suppliers[0], pytest.approx(25))
    market.buy_goods.assert_any_call(consumer, suppliers[1], pytest.approx(5))
    assert market.buy_goods.call_count == 2
