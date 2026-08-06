import pytest
from unittest.mock import Mock
from mcabsfc.roles import ConsumerRole

# ---------------------------------------------------
# ARCHITECTURAL TESTS
# ----------------------------------------------------


def test_is_ecorole():
    # Given
    from mcabsfc.base import EcoRole

    # Assert
    assert issubclass(ConsumerRole, EcoRole)


# ---------------------------------------------------
# BEHAVIORAL TESTS
# ----------------------------------------------------


@pytest.fixture
def consumer():
    # Given
    market = Mock()
    owner = Mock(id=1)
    return ConsumerRole(owner, market)


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
    market.avg_price = 25

    # When
    avg_price = consumer.get_average_price()

    # Then
    assert avg_price == 25


def test_get_tradable_demand(consumer):
    # Given
    market = consumer.space
    market.tradable = True
    household = consumer.owner
    household.desired_trad_cons = 40
    household.desired_non_trad_cons = 60

    # Assert
    assert consumer.demand == 40


def test_get_non_tradable_demand(consumer):
    # Given
    market = consumer.space
    market.tradable = False
    household = consumer.owner
    household.desired_trad_cons = 40
    household.desired_non_trad_cons = 60

    # Assert
    assert consumer.demand == 60


def test_buy_goods_calls_market(consumer):
    # Given
    market = consumer.space
    producer = Mock()

    # When
    consumer.buy_goods(producer, quantity=10)

    # Then
    market.buy_goods.assert_called_once_with(consumer, producer, 10)
