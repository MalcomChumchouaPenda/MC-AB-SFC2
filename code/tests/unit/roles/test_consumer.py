import pytest
from unittest.mock import Mock
from model.roles.consumer import Consumer

# ---------------------------------------------------
# ARCHITECTURE
# ----------------------------------------------------


def test_inherits_from_eco_role():
    # Given
    from model.extensions import EcoRole

    # When
    is_derived = issubclass(Consumer, EcoRole)

    # Then
    assert is_derived


def test_initializes_preference(role):
    # Given
    env = Mock()
    agent_id = 1

    # When
    role = Consumer(agent_id, env)

    # Then
    assert role.preference is None


# ---------------------------------------------------
# PERCEPTION TESTS
# ----------------------------------------------------


@pytest.fixture
def role():
    # Given
    env = Mock()
    agent_id = 1
    return Consumer(agent_id, env)


def test_get_average_price(role):
    # Given
    env = role.env
    env.average_price = 25

    # When
    average_price = role.get_average_price()

    # Then
    assert average_price == 25


def test_find_suppliers_get_random_founders(role):
    # Given
    env = role.env

    # When
    found = role.find_suppliers(5)

    # Then
    env.find_random_roles.assert_called_with("producer", 5)
    assert found == env.find_random_roles.return_value


# ---------------------------------------------------
# ACTION TESTS
# ----------------------------------------------------


def test_buy_goods_uses_env_method(role):
    # Given
    supplier = Mock()
    env = role.env

    # When
    role.buy_goods(supplier, 10)

    # Then
    env.buy_goods.assert_called_with(role, supplier, 10)
