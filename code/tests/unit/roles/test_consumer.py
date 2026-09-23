import pytest
from unittest.mock import Mock
from model.roles.consumer import Consumer

# ---------------------------------------------------
# ARCHITECTURE TESTS
# ----------------------------------------------------


def test_is_eco_role():
    # Given
    from model.base import EcoRole

    # Assert
    assert issubclass(Consumer, EcoRole)


@pytest.fixture
def consumer_before_setup():
    # Given
    model = Mock()
    consumer = Consumer(model)
    return consumer


def test_expose_preference_attr(consumer_before_setup):
    # Given
    consumer = consumer_before_setup

    # When
    consumer.agent = Mock(preference=0.1)

    # Then
    assert consumer.preference == 0.1


# ---------------------------------------------------
# PERCEPTION TESTS
# ----------------------------------------------------


@pytest.fixture
def consumer_with_env(consumer_before_setup):
    # Given
    env = Mock()
    consumer = consumer_before_setup
    consumer.env = env
    return consumer, env


def test_get_average_price(consumer_with_env):
    # Given
    consumer, env = consumer_with_env
    env.average_price = 25

    # When
    average_price = consumer.get_average_price()

    # Then
    assert average_price == 25


def test_find_suppliers_uses_env_method(consumer_with_env):
    # Given
    suppliers = [Mock() for _ in range(2)]
    consumer, env = consumer_with_env
    env.find_suppliers.return_value = suppliers

    # When
    found = consumer.find_suppliers(5)

    # Then
    env.find_suppliers.assert_called_with(5)
    assert found == suppliers


# ---------------------------------------------------
# ACTION TESTS
# ----------------------------------------------------


def test_buy_goods_uses_env_method(consumer_with_env):
    # Given
    supplier = Mock()
    consumer, env = consumer_with_env

    # When
    consumer.buy_goods(supplier, 10)

    # Then
    env.buy_goods.assert_called_with(consumer, supplier, 10)



