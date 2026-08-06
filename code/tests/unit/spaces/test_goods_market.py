import pytest
from unittest.mock import Mock
from dataclasses import dataclass
from mcabsfc.spaces import GoodsMarket

# ---------------------------------------------------
# ARCHITECTURAL TESTS
# ----------------------------------------------------


def test_is_ecospace():
    # Given
    from mcabsfc.base import EcoSpace

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


@dataclass(frozen=True)
class FakeConsumerRole:
    owner: object = None
    space: object = None
    label: int = 1


@dataclass(frozen=True)
class FakeProducerRole:
    owner: object = None
    space: object = None
    label: int = 2


@pytest.fixture
def market(monkeypatch):
    # Given a market and fake role class
    model = Mock()
    market = GoodsMarket(model)
    monkeypatch.setattr("mcabsfc.spaces.ConsumerRole", FakeConsumerRole)
    monkeypatch.setattr("mcabsfc.spaces.ProducerRole", FakeProducerRole)
    return market


def test_add_consumer_creates_tradable_consumer_role(market):
    # Given
    household = Mock(id=1, roles={})

    # When
    consumer = market.add_consumer(household)

    # Then
    assert isinstance(consumer, FakeConsumerRole)
    assert consumer.owner is household
    assert consumer.space is market
    assert consumer in market.nodes
    assert consumer is household.roles["consumer_tradable"]


def test_add_consumer_creates_non_tradable_consumer_role(market):
    # Given
    household = Mock(id=1, roles={})
    market.tradable = False

    # When
    consumer = market.add_consumer(household)

    # Then
    assert isinstance(consumer, FakeConsumerRole)
    assert consumer.owner is household
    assert consumer.space is market
    assert consumer in market.nodes
    assert consumer is household.roles["consumer_non_tradable"]


def test_add_producer_creates_and_registers_producer_role(market):
    # Given
    firm = Mock(id=1, roles={})

    # When
    producer = market.add_producer(firm)

    # Then
    assert isinstance(producer, FakeProducerRole)
    assert producer.owner is firm
    assert producer.space is market
    assert producer in market.nodes
    assert producer is firm.roles["producer"]


def test_search_suppliers_returns_psi_producers(market):
    # Given
    producers = [FakeProducerRole(label=i) for i in range(5)]
    market.model.random.sample.return_value = producers[:3]
    market.graph.add_nodes_from(producers)

    # When
    sample = market.search_suppliers(psi=3)

    # Then
    market.model.random.sample.sample(producers, k=3)
    assert sample == producers[:3]


def test_buy_goods_updates_accounts(market):
    # Given
    consumer = Mock(label=1)
    producer = Mock(label=2)
    producer.get_price.return_value = 10

    # When
    market.buy_goods(consumer, producer, quantity=5)

    # Then
    consumer.decrease_stock("cash", 50)
    consumer.increase_flow("consumption", 50)
    producer.increase_stock("cash", 50)
    producer.increase_flow("sales", 50)
    producer.decrease_stock("inventories", 5)
