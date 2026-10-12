import math
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


def test_initializes_sales():
    # Given
    agent, env = Mock(), Mock()

    # When
    role = Producer(agent, env)

    # Then
    assert role.sales == 0


def test_initializes_variety():
    # Given
    agent, env = Mock(), Mock()

    # When
    role = Producer(agent, env)

    # Then
    assert role.variety is None


def test_initializes_defaulted():
    # Given
    agent, env = Mock(), Mock()

    # When
    role = Producer(agent, env)

    # Then
    assert role.defaulted is False


def test_initializes_rd_expenditure():
    # Given
    agent, env = Mock(), Mock()

    # When
    role = Producer(agent, env)

    # Then
    assert role.rd == 0


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


def test_produce_goods_increases_inventories(role):
    # Given
    role.productivity = 2.0
    role.inventories = 5.0

    # When
    role.produce_goods(10)

    # Then
    assert role.inventories == 25.0


@pytest.fixture
def role_before_innovation(role):
    role._innovate = Mock()
    role._imitate = Mock()
    role._calc_rd_success_probability = Mock(return_value=0.0)
    return role


def test_execute_rd_sets_rd(role_before_innovation):
    # Given
    role = role_before_innovation

    # When
    role.execute_rd(100)

    # Then
    assert role.rd == 100


def test_execute_rd_calcs_success_probability(role_before_innovation):
    # Given
    role = role_before_innovation
    role._calc_rd_success_probability.return_value = 0.6
    random = role.env.model.nprandom

    # When
    role.execute_rd(100)

    # Then
    random.choice.assert_called_with([0, 1], p=[1 - 0.6, 0.6])


def test_execute_rd_innovates_if_success(role_before_innovation):
    # Given
    role = role_before_innovation
    role._calc_rd_success_probability.return_value = 0.6
    random = role.env.model.nprandom
    random.choice.return_value = 1

    # When
    role.execute_rd(100)

    # Then
    role._innovate.assert_called_once_with()
    role._imitate.assert_called_once_with()


def test_execute_rd_doesnt_innovate_if_no_success(role_before_innovation):
    # Given
    role = role_before_innovation
    role._calc_rd_success_probability.return_value = 0.6
    random = role.env.model.nprandom
    random.choice.return_value = 0

    # When
    role.execute_rd(100)

    # Then
    role._innovate.assert_not_called()
    role._imitate.assert_not_called()


def test_calc_rd_success_probability(role):
    # Given
    role.rd = 100
    role.env.p.nu = 0.5
    role.env.average_price = 20
    role.env.average_prod = 10
    expected = 1 - math.exp(-0.5 * 100 / (20 * 10))

    # When
    probability = role._calc_rd_success_probability()

    # Then
    assert probability == pytest.approx(expected)


def test_innovate_updates_randomly_productivity(role):
    # Given
    role.productivity = 10
    role.env.p.delta = 0.2
    role.env.average_prod = 10
    random = role.env.model.nprandom
    random.uniform = lambda a, b: b

    # When
    role._innovate()

    # Then
    assert role.productivity == 12


def test_imitate_updates_randomly_productivity(role):
    # Given
    role.productivity = 10
    role.env.average_prod = 20
    random = role.env.model.nprandom
    random.uniform = lambda a, b: b

    # When
    role._imitate()

    # Then
    assert role.productivity == 20
