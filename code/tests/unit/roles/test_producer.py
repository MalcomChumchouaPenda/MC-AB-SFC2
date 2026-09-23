import pytest
from unittest.mock import Mock
from model.roles.producer import Producer

# ---------------------------------------------------
# ARCHITECTURE TESTS
# ----------------------------------------------------


def test_is_eco_role():
    # Given
    from model.base import EcoRole

    # Assert
    assert issubclass(Producer, EcoRole)


@pytest.fixture
def role_with_env():
    # Given
    agent, env = Mock(), Mock()
    role = Producer(agent, env)
    return role, env


def test_has_price_attr(role_with_env):
    # Given
    role, _ = role_with_env

    # Assert
    assert role.price == 0


def test_has_productivity_attr(role_with_env):
    # Given
    role, _ = role_with_env

    # Assert
    assert role.productivity == 0


def test_has_inventories_attr(role_with_env):
    # Given
    role, _ = role_with_env

    # Assert
    assert role.inventories == 0


def test_expose_variety_attr(role_with_env):
    # Given
    role, _ = role_with_env

    # When
    role.agent = Mock(variety=0.5)

    # Assert
    assert role.variety == 0.5


# ---------------------------------------------------
# PERCEPTIONS TESTS
# ----------------------------------------------------


def test_get_average_price(role_with_env):
    # Given
    role, env = role_with_env
    env.average_price = 15

    # When
    average_price = role.get_average_price()

    # Then
    assert average_price == 15


def test_get_average_productivity(role_with_env):
    # Given
    role, env = role_with_env
    env.average_prod = 2.5

    # When
    average_productiviy = role.get_average_productivity()

    # Then
    assert average_productiviy == 2.5


# ---------------------------------------------------
# ACTIONS TESTS
# ----------------------------------------------------


def test_get_produce_goods_increases_inventories(role_with_env):
    # Given
    role, _ = role_with_env
    role.productivity = 2.0
    role.inventories = 5.0

    # When
    role.produce_goods(10)

    # Then
    assert role.inventories == 25.0
