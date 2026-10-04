import pytest
from unittest.mock import Mock
from model.roles.producer import Producer

# ---------------------------------------------------
# ARCHITECTURE
# ----------------------------------------------------


def test_inherits_from_eco_role():
    # Given
    from model.extensions import EcoRole

    # When
    is_derived = issubclass(Producer, EcoRole)

    # Then
    assert is_derived


def test_initializes_price():
    # Given
    agent, env = Mock(), Mock()

    # When
    role = Producer(agent, env)

    # Then
    assert role.price == 0


def test_initializes_productivity():
    # Given
    agent, env = Mock(), Mock()

    # When
    role = Producer(agent, env)

    # Then
    assert role.productivity == 0


def test_initializes_inventories():
    # Given
    agent, env = Mock(), Mock()

    # When
    role = Producer(agent, env)

    # Then
    assert role.inventories == 0


def test_initializes_variety():
    # Given
    agent, env = Mock(), Mock()

    # When
    role = Producer(agent, env)

    # Then
    assert role.variety is None


# ---------------------------------------------------
# PERCEPTIONS TESTS
# ----------------------------------------------------


@pytest.fixture
def role():
    # Given
    agent, env = Mock(), Mock()
    return Producer(agent, env)


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
