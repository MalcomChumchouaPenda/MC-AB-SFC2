import pytest
from unittest.mock import Mock
from model.base import EcoRole
from model.roles.producer import Producer

# ---------------------------------------------------
# ARCHITECTURE TESTS
# ----------------------------------------------------


def test_inherits_from_eco_role():
    # Assert
    assert issubclass(Producer, EcoRole)


@pytest.fixture
def role():
    # Given
    agent, env = Mock(), Mock()
    return Producer(agent, env)


def test_has_price_attr(role):
    # Assert
    assert role.price == 0


def test_has_productivity_attr(role):
    # Assert
    assert role.productivity == 0


def test_has_inventories_attr(role):
    # Assert
    assert role.inventories == 0


def test_expose_variety_attr(role):
    # Given
    role.agent.variety = 0.5

    # When
    exposed = role.variety

    # Then
    assert exposed == 0.5


# ---------------------------------------------------
# PERCEPTIONS TESTS
# ----------------------------------------------------


def test_get_average_price(role):
    # Given
    env = role.env
    env.average_price = 15

    # When
    average_price = role.get_average_price()

    # Then
    assert average_price == 15


def test_get_average_productivity(role):
    # Given
    env = role.env
    env.average_prod = 2.5

    # When
    average_productiviy = role.get_average_productivity()

    # Then
    assert average_productiviy == 2.5


# ---------------------------------------------------
# ACTIONS TESTS
# ----------------------------------------------------


def test_get_produce_goods_increases_inventories(role):
    # Given
    role.productivity = 2.0
    role.inventories = 5.0

    # When
    role.produce_goods(10)

    # Then
    assert role.inventories == 25.0
