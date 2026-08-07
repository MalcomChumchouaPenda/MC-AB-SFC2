import pytest
from unittest.mock import Mock
from mc_ab_sfc.spaces import GoodsMarket

# ---------------------------------------------------
# ARCHITECTURAL TESTS
# ----------------------------------------------------


def test_is_ecospace():
    # Given
    from mc_ab_sfc.base import EcoSpace

    # Assert
    assert issubclass(GoodsMarket, EcoSpace)


def test_is_tradable_by_default():
    # Given
    model = Mock()
    market = GoodsMarket(model)

    # Assert
    assert market.tradable is True


def test_goods_market_can_be_non_tradable():
    # Given
    model = Mock()
    market = GoodsMarket(model, tradable=False)

    # Assert
    assert market.tradable is False


# ---------------------------------------------------
# BEHAVIORAL TESTS
# ----------------------------------------------------


@pytest.fixture
def market():
    # Given
    model = Mock()
    market = GoodsMarket(model)
    return market


class FakeRole:
    pass


def test_add_consumer_creates_tradable_consumer_role(market, monkeypatch):
    # Given
    household = Mock()
    market.add_role = Mock()
    monkeypatch.setattr("mc_ab_sfc.spaces.ConsumerRole", FakeRole)

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
    monkeypatch.setattr("mc_ab_sfc.spaces.ConsumerRole", FakeRole)

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
    monkeypatch.setattr("mc_ab_sfc.spaces.ProducerRole", FakeRole)

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
    monkeypatch.setattr("mc_ab_sfc.spaces.ProducerRole", FakeRole)

    random = market.model.random
    random.sample = Mock(side_effect=lambda pop, k: pop[:k])

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


def test_calc_average_productivity(market, monkeypatch):
    # Given
    other = Mock(productivity=10)
    producer1, producer2 = FakeRole(), FakeRole()
    producer1.productivity = 10
    producer2.productivity = 20
    market.graph.add_nodes_from([other, producer1, producer2])
    monkeypatch.setattr("mc_ab_sfc.spaces.ProducerRole", FakeRole)

    # When
    average_productivity = market.calc_average_productivity()

    # Then
    assert average_productivity == 15
