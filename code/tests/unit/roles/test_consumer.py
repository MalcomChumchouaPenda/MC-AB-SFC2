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
def role_with_env():
    # Given
    agent, env = Mock(), Mock()
    role = Consumer(agent, env)
    return role, env


def test_expose_preference_attr(role_with_env):
    # Given
    role, _ = role_with_env

    # When
    role.agent = Mock(preference=0.1)

    # Then
    assert role.preference == 0.1


# ---------------------------------------------------
# PERCEPTION TESTS
# ----------------------------------------------------


def test_get_average_price(role_with_env):
    # Given
    role, env = role_with_env
    env.average_price = 25

    # When
    average_price = role.get_average_price()

    # Then
    assert average_price == 25


def test_find_suppliers_get_random_founders(role_with_env, make_dlist):
    # Given
    suppliers = [Mock() for _ in range(2)]
    suppliers = make_dlist(suppliers)
    role, env = role_with_env
    env.find_random_roles.return_value = suppliers

    # When
    found = role.find_suppliers(5)

    # Then
    env.find_random_roles.assert_called_with("producer", 5)
    assert found == suppliers


# ---------------------------------------------------
# ACTION TESTS
# ----------------------------------------------------


def test_buy_goods_uses_env_method(role_with_env):
    # Given
    supplier = Mock()
    role, env = role_with_env

    # When
    role.buy_goods(supplier, 10)

    # Then
    env.buy_goods.assert_called_with(role, supplier, 10)
