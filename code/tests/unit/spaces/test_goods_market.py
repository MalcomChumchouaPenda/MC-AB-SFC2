import pytest
from unittest.mock import Mock
from mc_ab_sfc.spaces.goods_market import GoodsMarket

# ---------------------------------------------------
# ARCHITECTURE TESTS
# ----------------------------------------------------


def test_is_eco_space():
    # Given
    from mc_ab_sfc.base import EcoSpace

    # Assert
    assert issubclass(GoodsMarket, EcoSpace)


@pytest.fixture
def market():
    # Given
    model = Mock()
    market = GoodsMarket(model)
    return market


def test_is_tradable_by_default(market):
    # Assert
    assert market.tradable is True


def test_can_be_non_tradable():
    # Given
    model = Mock()
    market = GoodsMarket(model, tradable=False)

    # Assert
    assert market.tradable is False


def test_has_default_statistics(market):
    # Assert
    assert market.average_price == 0
    assert market.average_productivity == 0
    assert market.inflation == 0
    assert market.gdp == 0


# ---------------------------------------------------
# BEHAVIORAL TESTS
# ----------------------------------------------------


@pytest.fixture
def market():
    # Given
    model = Mock()
    random = model.random
    random.sample = Mock(side_effect=lambda pop, k: pop[:k])
    market = GoodsMarket(model)
    return market


class FakeRole:
    pass


def test_add_consumer_creates_tradable_consumer_role(market, monkeypatch):
    # Given
    household = Mock()
    market.add_role = Mock()
    monkeypatch.setattr("mc_ab_sfc.spaces.goods_market.ConsumerRole", FakeRole)

    # When
    consumer = market.add_consumer(household)

    # Then
    action = market.add_role
    action.assert_called_with(FakeRole, household, "consumer_tradable")
    assert consumer is action.return_value


def test_add_consumer_creates_non_tradable_consumer_role(market, monkeypatch):
    # Given
    household = Mock()
    market.add_role = Mock()
    market.tradable = False
    monkeypatch.setattr("mc_ab_sfc.spaces.goods_market.ConsumerRole", FakeRole)

    # When
    consumer = market.add_consumer(household)

    # Then
    action = market.add_role
    action.assert_called_with(FakeRole, household, "consumer_non_tradable")
    assert consumer is action.return_value


def test_add_supplier_creates_producer_role(market, monkeypatch):
    # Given
    firm = Mock()
    market.add_role = Mock()
    monkeypatch.setattr("mc_ab_sfc.spaces.goods_market.ProducerRole", FakeRole)

    # When
    producer = market.add_supplier(firm)

    # Then
    action = market.add_role
    action.assert_called_with(FakeRole, firm, "producer")
    assert producer is action.return_value


def test_search_suppliers_returns_psi_producers(market, monkeypatch):
    # Given
    others = [Mock() for _ in range(5)]
    producers = [FakeRole() for _ in range(5)]
    market.graph.add_nodes_from(others + producers)
    monkeypatch.setattr("mc_ab_sfc.spaces.goods_market.ProducerRole", FakeRole)

    # When
    sample = market.search_suppliers(psi=3)

    # Then
    market.model.random.sample.sample(producers, k=3)
    assert sample == producers[:3]


def test_buy_goods_updates_tradable_flows(market):
    # Given
    market.tradable = True
    consumer = Mock()
    producer = Mock(price=10)

    # When
    market.buy_goods(consumer, producer, quantity=5)

    # Then
    consumer.decrease_stock.assert_called_with("cash", 50)
    consumer.increase_flow.assert_called_with("tradable_cons", 50)
    producer.increase_stock.assert_called_with("cash", 50)
    producer.increase_flow.assert_called_with("sales", 50)
    producer.decrease_stock.assert_called_with("inventories", 5)


def test_buy_goods_updates_non_tradable_flows(market):
    # Given
    market.tradable = False
    consumer = Mock()
    producer = Mock(price=10)

    # When
    market.buy_goods(consumer, producer, quantity=5)

    # Then
    consumer.decrease_stock.assert_called_with("cash", 50)
    consumer.increase_flow.assert_called_with("non_tradable_cons", 50)
    producer.increase_stock.assert_called_with("cash", 50)
    producer.increase_flow.assert_called_with("sales", 50)
    producer.decrease_stock.assert_called_with("inventories", 5)


# ---------------------------------------------------
# STATITICS MANAGEMENT TESTS
# ----------------------------------------------------


@pytest.fixture
def market_for_stats_computation():
    # Given
    model = Mock()
    market = GoodsMarket(model)
    market.average_price = 0
    market.average_productivity = 1
    return market


def test_calc_average_price(market_for_stats_computation):
    # Given
    market = market_for_stats_computation
    producers = [Mock(price=5) for _ in range(5)]

    # When
    average_price = market.calc_average_price(producers)

    # Then
    assert average_price == pytest.approx(5.0)


def test_calc_average_productivity(market_for_stats_computation):
    # Given
    market = market_for_stats_computation
    producers = [Mock(productivity=10) for _ in range(5)]

    # When
    average_prod = market.calc_average_productivity(producers)

    # Then
    assert average_prod == pytest.approx(10.0)


def test_calc_inflation(market_for_stats_computation):
    # Given
    producers = [Mock(price=12) for _ in range(5)]
    market = market_for_stats_computation
    market.average_price = 10

    # When
    inflation = market.calc_inflation(producers)

    # Then
    assert inflation == pytest.approx(0.2)


def test_calc_gdp(market_for_stats_computation):
    # Given
    producers = [Mock(sales=100) for _ in range(5)]
    market = market_for_stats_computation

    # When
    gdp = market.calc_gdp(producers)

    # Then
    assert gdp == pytest.approx(500)


@pytest.fixture
def market_for_stats_updates(monkeypatch):
    # Given
    model = Mock()
    market = GoodsMarket(model)
    market.calc_gdp = Mock()
    market.calc_inflation = Mock()
    market.calc_average_price = Mock()
    market.calc_average_productivity = Mock()
    monkeypatch.setattr("mc_ab_sfc.spaces.goods_market.ProducerRole", FakeRole)
    return market


def test_update_statistics_with_producers(market_for_stats_updates):
    # Given
    producers = [FakeRole() for _ in range(5)]
    others = [Mock() for _ in range(3)]
    market = market_for_stats_updates
    market.graph.add_nodes_from(producers + others)

    # When
    market.update_statistics()

    # Then
    market.calc_gdp.assert_called_with(producers)
    market.calc_inflation.assert_called_with(producers)
    market.calc_average_price.assert_called_with(producers)
    market.calc_average_productivity.assert_called_with(producers)


def test_update_statistics_with_prices(market_for_stats_updates):
    # Given
    market = market_for_stats_updates
    market.calc_average_price.return_value = 15.0
    market.calc_inflation.return_value = 0.05

    # When
    market.update_statistics()

    # Then
    assert market.average_price == pytest.approx(15.0)
    assert market.inflation == pytest.approx(0.05)


def test_update_statistics_with_production(market_for_stats_updates):
    # Given
    market = market_for_stats_updates
    market.calc_average_productivity.return_value = 2.0
    market.calc_gdp.return_value = 150

    # When
    market.update_statistics()

    # Then
    assert market.average_productivity == pytest.approx(2.0)
    assert market.gdp == pytest.approx(150)
