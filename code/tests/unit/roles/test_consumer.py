import pytest
from unittest.mock import Mock
from model.spaces.good_market import Consumer

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
def consumer_with_space(consumer_before_setup):
    # Given
    space = Mock()
    consumer = consumer_before_setup
    consumer.space = space
    return consumer, space


def test_get_average_price(consumer_with_space):
    # Given
    consumer, space = consumer_with_space
    space.average_price = 25

    # When
    average_price = consumer.get_average_price()

    # Then
    assert average_price == 25


def test_find_suppliers_uses_space_method(consumer_with_space):
    # Given
    suppliers = [Mock() for _ in range(2)]
    consumer, space = consumer_with_space
    space.find_suppliers.return_value = suppliers

    # When
    found = consumer.find_suppliers(5)

    # Then
    space.find_suppliers.assert_called_with(5)
    assert found == suppliers


# ---------------------------------------------------
# ACTION TESTS
# ----------------------------------------------------


def test_buy_goods_uses_space_method(consumer_with_space):
    # Given
    supplier = Mock()
    consumer, space = consumer_with_space

    # When
    consumer.buy_goods(supplier, 10)

    # Then
    space.buy_goods.assert_called_with(consumer, supplier, 10)


# def test_get_tradable_demand(consumer):
#     # Given
#     space = consumer.space
#     space.tradable = True
#     household = consumer.agent
#     household.desired_trad_cons = 40
#     household.desired_non_trad_cons = 60

#     # Assert
#     assert consumer.demand == 40


# def test_get_non_tradable_demand(consumer):
#     # Given
#     space = consumer.space
#     space.tradable = False
#     household = consumer.agent
#     household.desired_trad_cons = 40
#     household.desired_non_trad_cons = 60

#     # Assert
#     assert consumer.demand == 60


# @pytest.fixture
# def consumer_with_demand(monkeypatch):
#     # Given
#     demand = PropertyMock(return_value=500)
#     monkeypatch.setattr(Consumer, "demand", demand)
#     space = Mock()
#     household = Mock(id=1)
#     return Consumer(household, space)


# TODO
# def test_buy_goods_respects_desired_consumption(consumer_with_demand):
#     # Given
#     consumer = consumer_with_demand
#     household = consumer.agent
#     household.cash = 1000
#     suppliers = [Mock(price=10, available_quantity=25) for _ in range(3)]

#     # When
#     consumer.buy_goods(suppliers)

#     # Then
#     space = consumer.space
#     space.buy_goods.assert_any_call(consumer, suppliers[0], pytest.approx(25))
#     space.buy_goods.assert_any_call(consumer, suppliers[1], pytest.approx(25))
#     assert space.buy_goods.call_count == 2


# def test_buy_goods_respects_supply_constraints(consumer_with_demand):
#     # Given
#     consumer = consumer_with_demand
#     household = consumer.agent
#     household.cash = 1000
#     suppliers = [Mock(price=10, available_quantity=10) for _ in range(2)]

#     # When
#     consumer.buy_goods(suppliers)

#     # Then
#     space = consumer.space
#     space.buy_goods.assert_any_call(consumer, suppliers[0], pytest.approx(10))
#     space.buy_goods.assert_any_call(consumer, suppliers[1], pytest.approx(10))


# def test_buy_goods_respects_monetary_constraints(consumer_with_demand):
#     # Given
#     consumer = consumer_with_demand
#     household = consumer.agent
#     household.cash = 300
#     suppliers = [Mock(price=10, available_quantity=25) for _ in range(2)]

#     # When
#     consumer.buy_goods(suppliers)

#     # Then
#     space = consumer.space
#     space.buy_goods.assert_any_call(consumer, suppliers[0], pytest.approx(25))
#     space.buy_goods.assert_any_call(consumer, suppliers[1], pytest.approx(5))
#     assert space.buy_goods.call_count == 2
