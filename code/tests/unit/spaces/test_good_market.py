import pytest
from unittest.mock import Mock, MagicMock
from agentpy import AgentDList
from model.spaces.good_market import GoodsMarket

# ---------------------------------------------------
# ARCHITECTURE TESTS
# ----------------------------------------------------


def test_is_eco_space():
    # Given
    from model.base import EcoSpace

    # Assert
    assert issubclass(GoodsMarket, EcoSpace)


@pytest.fixture
def market_before_setup():
    # Given
    model = Mock()
    market = GoodsMarket(model)
    return market


def test_has_tradable_attr(market_before_setup):
    # Given
    market = market_before_setup

    # When
    market.setup()

    # Then
    assert market.tradable is False


def test_has_average_price_attr(market_before_setup):
    # Given
    market = market_before_setup

    # When
    market.setup()

    # Then
    assert market.average_price == 0


def test_has_previous_average_price_attr(market_before_setup):
    # Given
    market = market_before_setup

    # When
    market.setup()

    # Then
    assert market.average_price_prev == 0


def test_has_average_productivity_attr(market_before_setup):
    # Given
    market = market_before_setup

    # When
    market.setup()

    # Then
    assert market.average_prod == 0


# ---------------------------------------------------
# ROLES SET/REF TESTS
# ----------------------------------------------------


def test_has_consumers_list(market_before_setup):
    # Given
    market = market_before_setup

    # When
    market.setup()

    # Then
    assert isinstance(market.consumers, AgentDList)


def test_has_producers_list(market_before_setup):
    # Given
    market = market_before_setup

    # When
    market.setup()

    # Then
    assert isinstance(market.producers, AgentDList)


# ---------------------------------------------------
# ROLES MANAGEMENT TESTS
# ----------------------------------------------------


FakeConsumer = Mock()


@pytest.fixture
def market_without_consumers(monkeypatch, market_before_setup):
    # Given
    monkeypatch.setattr("model.spaces.good_market.Consumer", FakeConsumer)
    market = market_before_setup
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
def market_without_producers(monkeypatch, market_before_setup):
    # Given
    monkeypatch.setattr("model.spaces.good_market.Producer", FakeProducer)
    market = market_before_setup
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
def market_with_producers(market_before_setup):
    # Given
    producers = MagicMock()
    producers.__len__.return_value = 1
    producers.random.return_value = []
    market = market_before_setup
    market.producers = producers
    return market, producers


def test_find_suppliers_get_random_founders(market_with_producers):
    # Given
    expected = [Mock() for _ in range(10)]
    market, producers = market_with_producers
    producers.random.return_value = expected

    # When
    found = market.find_suppliers(5)

    # Then
    assert found == expected


@pytest.mark.parametrize("psi, expected", [(5, 5), (15, 10)])
def test_find_suppliers_with_psi_params(market_with_producers, psi, expected):
    # Given
    market, producers = market_with_producers
    producers.__len__.return_value = 10

    # When
    market.find_suppliers(psi)

    # Then
    producers.random.assert_called_with(expected)


def test_buy_goods_updates_accounts(market_before_setup):
    # Given
    market = market_before_setup
    producer = Mock(price=10, inventories=100)
    consumer = Mock()

    # When
    market.buy_goods(consumer, producer, 5)

    # Then
    consumer.debit_stock.assert_any_call("cash", 50)
    consumer.debit_flow.assert_any_call("consumption", 50)
    producer.credit_stock.assert_any_call("cash", 50)
    producer.credit_flow.assert_any_call("consumption", 50)


def test_buy_goods_decrease_inventories(market_before_setup):
    # Given
    market = market_before_setup
    producer = Mock(price=10, inventories=100)
    consumer = Mock()

    # When
    market.buy_goods(consumer, producer, 5)

    # Then
    assert producer.inventories == 95.0


# ---------------------------------------------------
# EVOLUTION TESTS
# ----------------------------------------------------


@pytest.fixture
def market_before_update(market_before_setup, make_dlist):
    # Given
    producers = [Mock(price=0, productivity=0) for _ in range(5)]
    market = market_before_setup
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
