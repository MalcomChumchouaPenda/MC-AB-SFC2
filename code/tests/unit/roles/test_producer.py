import pytest
from unittest.mock import Mock
from model.spaces.good_market import Producer

# ---------------------------------------------------
# ARCHITECTURE TESTS
# ----------------------------------------------------


def test_is_eco_role():
    # Given
    from model.base import EcoRole

    # Assert
    assert issubclass(Producer, EcoRole)


@pytest.fixture
def producer_before_setup():
    # Given
    model = Mock()
    producer = Producer(model)
    return producer


def test_has_price_attr(producer_before_setup):
    # Given
    producer = producer_before_setup

    # When
    producer.setup()

    # Assert
    assert producer.price == 0


def test_has_productivity_attr(producer_before_setup):
    # Given
    producer = producer_before_setup

    # When
    producer.setup()

    # Assert
    assert producer.productivity == 0


def test_has_inventories_attr(producer_before_setup):
    # Given
    producer = producer_before_setup

    # When
    producer.setup()

    # Assert
    assert producer.inventories == 0


def test_expose_variety_attr(producer_before_setup):
    # Given
    producer = producer_before_setup

    # When
    producer.agent = Mock(variety=0.5)

    # Assert
    assert producer.variety == 0.5


# ---------------------------------------------------
# PERCEPTIONS TESTS
# ----------------------------------------------------


@pytest.fixture
def producer_with_space(producer_before_setup):
    # Given
    space = Mock()
    producer = producer_before_setup
    producer.space = space
    return producer, space


def test_get_average_price(producer_with_space):
    # Given
    producer, space = producer_with_space
    space.average_price = 15

    # When
    average_price = producer.get_average_price()

    # Then
    assert average_price == 15


def test_get_average_productivity(producer_with_space):
    # Given
    producer, space = producer_with_space
    space.average_prod = 2.5

    # When
    average_productiviy = producer.get_average_productivity()

    # Then
    assert average_productiviy == 2.5


# ---------------------------------------------------
# ACTIONS TESTS
# ----------------------------------------------------


def test_get_produce_goods_increases_inventories(producer_before_setup):
    # Given
    producer = producer_before_setup
    producer.productivity = 2.0
    producer.inventories = 5.0

    # When
    producer.produce_goods(10)

    # Then
    assert producer.inventories == 25.0
