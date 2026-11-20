import pytest
from unittest.mock import Mock
from model.roles.consumer import Consumer

# ---------------------------------------------------
# ARCHITECTURE
# ----------------------------------------------------


def test_inherits_from_eco_role():
    # Given
    from model.extensions import EcoRole

    # Then
    assert issubclass(Consumer, EcoRole)


@pytest.fixture
def agent():
    # Given
    return Mock()


@pytest.fixture
def env():
    # Given
    return Mock()


@pytest.fixture
def role(agent, env):
    # Given
    return Consumer(agent, env)


def test_initializes_preference(role):
    # Then
    assert role.preference is None


def test_initializes_purchases(role):
    # Then
    assert role.purchases == 0.0


# ---------------------------------------------------
# PERCEPTION TESTS
# ----------------------------------------------------


def test_get_average_price(role, env):
    # Given
    env.average_price = 25

    # When
    average_price = role.get_average_price()

    # Then
    assert average_price == 25


def test_find_suppliers_get_random_founders(role, env):
    # Given

    # When
    found = role.find_suppliers(5)

    # Then
    env.find_random_roles.assert_called_with("producer", 5)
    assert found == env.find_random_roles.return_value


# ---------------------------------------------------
# ACTION TESTS
# ----------------------------------------------------


def test_buy_goods_uses_env_method(role, env):
    # Given
    supplier = Mock()

    # When
    role.buy_goods(supplier, 10)

    # Then
    env.buy_goods.assert_called_with(role, supplier, 10)
