import pytest
from unittest.mock import Mock, MagicMock
from agentpy import AgentDList
from model.base import EcoSpace
from model.spaces.good_market import GoodsMarket

# ---------------------------------------------------
# ARCHITECTURE TESTS
# ----------------------------------------------------


def test_inherits_from_eco_space():
    # Assert
    assert issubclass(GoodsMarket, EcoSpace)


@pytest.mark.parametrize("arg", [True, False])
def test_has_tradable_arg(arg):
    # Given
    model = Mock()

    # When
    market = GoodsMarket(model, tradable=arg)

    # Then
    assert market.tradable is arg


@pytest.fixture
def market():
    # Given
    model = Mock()
    return GoodsMarket(model)


def test_has_average_price_attr(market):
    # Assert
    assert market.average_price == 0


def test_has_previous_average_price_attr(market):
    # Assert
    assert market.average_price_prev == 0


def test_has_average_productivity_attr(market):
    # Assert
    assert market.average_prod == 0


# ---------------------------------------------------
# ROLES SET/REF TESTS
# ----------------------------------------------------


def test_has_consumers_list(market):
    # Assert
    assert isinstance(market.consumers, AgentDList)


def test_has_producers_list(market):
    # Assert
    assert isinstance(market.producers, AgentDList)


# ---------------------------------------------------
# ROLES MANAGEMENT TESTS
# ----------------------------------------------------


FakeConsumer = Mock()


@pytest.fixture
def market_without_consumers(monkeypatch, market):
    # Given
    monkeypatch.setattr("model.spaces.good_market.Consumer", FakeConsumer)
    market.add_role = Mock()
    market.consumers = []
    return market


def test_add_consumer_creates_tradable_consumer_role(market_without_consumers):
    # Given
    agent = Mock()
    market = market_without_consumers
    market.tradable = True

    # When
    role = market.add_consumer(agent)

    # Then
    market.add_role.assert_called_with(FakeConsumer, agent, "trad_consumer")
    assert role is market.add_role.return_value


def test_add_consumer_creates_non_tradable_consumer_role(market_without_consumers):
    # Given
    agent = Mock()
    market = market_without_consumers
    market.tradable = False

    # When
    role = market.add_consumer(agent)

    # Then
    market.add_role.assert_called_with(FakeConsumer, agent, "non_trad_consumer")
    assert role is market.add_role.return_value


@pytest.mark.parametrize("tradable", [True, False])
def test_add_consumer_registers_role(market_without_consumers, tradable):
    # Given
    agent = Mock()
    market = market_without_consumers
    market.tradable = tradable

    # When
    role = market.add_consumer(agent)

    # Then
    assert market.consumers == [role]


FakeProducer = Mock()


@pytest.fixture
def market_without_producers(monkeypatch, market):
    # Given
    monkeypatch.setattr("model.spaces.good_market.Producer", FakeProducer)
    market.add_role = Mock()
    market.producers = []
    return market


def test_add_producer_creates_producer_role(market_without_producers):
    # Given
    agent = Mock()
    market = market_without_producers

    # When
    role = market.add_producer(agent)

    # Then
    market.add_role.assert_called_with(FakeProducer, agent, "producer")
    assert role is market.add_role.return_value


def test_add_producer_registers_role(market_without_producers):
    # Given
    agent = Mock()
    market = market_without_producers

    # When
    role = market.add_producer(agent)

    # Then
    assert market.producers == [role]


# ---------------------------------------------------
# MATCHING / TRANSACTIONS TESTS
# ----------------------------------------------------


@pytest.fixture
def market():
    # Given
    model = Mock()
    random = model.random
    random.sample = Mock(side_effect=lambda pop, k: pop[:k])
    market = GoodsMarket(model)
    return market


@pytest.fixture
def market_before_purchase(market):
    # Given
    market.transfer_stock = Mock()
    market.record_flow = Mock()
    return market


def test_buy_goods_updates_accounts(market_before_purchase):
    # Given
    consumer = Mock()
    producer = Mock(price=10, inventories=100)
    market = market_before_purchase
    transfer_stock = market.transfer_stock
    record_flow = market.record_flow

    # When
    market.buy_goods(consumer, producer, 5)

    # Then
    transfer_stock.assert_any_call("cash", consumer.id, producer.id, 50)
    record_flow.assert_any_call("consumption", consumer.id, producer.id, 50)


def test_buy_goods_decrease_inventories(market_before_purchase):
    # Given
    consumer = Mock()
    producer = Mock(price=10, inventories=100)
    market = market_before_purchase

    # When
    market.buy_goods(consumer, producer, 5)

    # Then
    assert producer.inventories == 95.0


# ---------------------------------------------------
# EVOLUTION TESTS
# ----------------------------------------------------


@pytest.fixture
def market_before_update(market, make_dlist):
    # Given
    producers = [Mock(price=0, productivity=0) for _ in range(5)]
    market.average_price_prev = 0
    market.average_price = 0
    market.average_prod = 0
    market.producers = make_dlist(producers)
    return market


def test_update_state_recalc_average_price(market_before_update):
    # Given
    market = market_before_update
    market.producers.price = 5

    # When
    market.update_state()

    # Then
    assert market.average_price == pytest.approx(5.0)


def test_update_state_store_previous_average_price(market_before_update):
    # Given
    market = market_before_update
    market.producers.price = 5
    market.average_price = 6.0

    # When
    market.update_state()

    # Then
    assert market.average_price_prev == 6.0


def test_update_state_recalc_average_productivity(market_before_update):
    # Given
    market = market_before_update
    market.producers.productivity = 10

    # When
    market.update_state()

    # Then
    assert market.average_prod == pytest.approx(10.0)


# ---------------------------------------------------
#  STATISTICS TESTS
# ----------------------------------------------------


def test_calc_inflation(market_before_update):
    # Given
    market = market_before_update
    market.average_price_prev = 10
    market.average_price = 12

    # When
    inflation = market.calc_inflation()

    # Then
    assert inflation == pytest.approx(0.2)


def test_calc_gdp(market_before_update):
    # Given
    producer = Mock()
    producer.account.stocks = {"consumption": 500}
    market = market_before_update
    market.producers = [producer]

    # When
    gdp = market.calc_gdp()

    # Then
    assert gdp == pytest.approx(500)
