import pytest
from unittest.mock import Mock, call
from model.spaces.goods_market import GoodsMarket

# ---------------------------------------------------
# ARCHITECTURE
# ----------------------------------------------------


def test_inherits_from_eco_space():
    # Given
    from model.extensions import EcoSpace

    # When
    is_derived = issubclass(GoodsMarket, EcoSpace)

    # Then
    assert is_derived


@pytest.mark.parametrize("arg", [True, False])
def test_initializes_tradable_arg(arg):
    # Given
    model = Mock()

    # When
    market = GoodsMarket(model, tradable=arg)

    # Then
    assert market.tradable is arg


def test_initializes_average_price(fake_model):
    # Given
    model = fake_model

    # When
    market = GoodsMarket(model)

    # Then
    assert market.average_price == 0


def test_initializes_previous_average_price(fake_model):
    # Given
    model = fake_model

    # When
    market = GoodsMarket(model)

    # Then
    assert market.average_price_prev == 0


def test_initializes_average_productivity(fake_model):
    # Given
    model = fake_model

    # When
    market = GoodsMarket(model)

    # Then
    assert market.average_prod == 0


# ---------------------------------------------------
# ROLES MANAGEMENT TESTS
# ----------------------------------------------------


FakeConsumer = Mock()
FakeProducer = Mock()


@pytest.fixture
def market_without_roles(monkeypatch, fake_model):
    # Given
    monkeypatch.setattr("model.spaces.goods_market.Consumer", FakeConsumer)
    monkeypatch.setattr("model.spaces.goods_market.Producer", FakeProducer)
    market = GoodsMarket(fake_model)
    market.add_role = Mock()
    return market


@pytest.mark.parametrize("tradable, prefix", [(True, "trad"), (False, "non_trad")])
def test_add_household_adds_consumer_role(market_without_roles, tradable, prefix):
    # Given
    market = market_without_roles
    market.tradable = tradable
    household = Mock()

    # When
    market.add_household(household)

    # Then
    market.add_role.assert_called_with(FakeConsumer, household, prefix=prefix)


@pytest.mark.parametrize("tradable", [True, False])
def test_add_firm_adds_producer_role_for_compliers(market_without_roles, tradable):
    # Given
    firm = Mock(tradable=tradable)
    market = market_without_roles
    market.tradable = tradable

    # When
    market.add_firm(firm)

    # Then
    market.add_role.assert_called_with(FakeProducer, firm)


@pytest.mark.parametrize("tradable", [True, False])
def test_add_firm_doesnt_add_role_for_no_compliers(market_without_roles, tradable):
    # Given
    firm = Mock(tradable=tradable)
    market = market_without_roles
    market.tradable = not tradable

    # When
    market.add_firm(firm)

    # Then
    market.add_role.assert_not_called()


# ---------------------------------------------------
# MATCHING / TRANSACTIONS TESTS
# ----------------------------------------------------


@pytest.fixture
def market_before_transaction(market_without_roles):
    # Given
    market = market_without_roles
    market.transfer_stock = Mock()
    market.make_transaction = Mock()
    random = market.model.random
    random.sample = Mock(side_effect=lambda pop, k: pop[:k])
    return market


def test_buy_goods_updates_accounts(market_before_transaction):
    # Given
    consumer = Mock()
    producer = Mock(price=10, inventories=100, sales=0)
    market = market_before_transaction

    # When
    market.buy_goods(consumer, producer, 5)

    # Then
    market.transfer_stock.assert_any_call("cash", consumer.id, producer.id, 50)
    market.make_transaction.assert_any_call("consumption", consumer.id, producer.id, 50)


def test_buy_goods_decrease_inventories(market_before_transaction):
    # Given
    consumer = Mock()
    producer = Mock(price=10, inventories=100, sales=0)
    market = market_before_transaction

    # When
    market.buy_goods(consumer, producer, 5)

    # Then
    assert producer.inventories == 95.0


def test_buy_goods_increases_sales(market_before_transaction):
    # Given
    consumer = Mock()
    producer = Mock(price=10, inventories=100, sales=0)
    market = market_before_transaction

    # When
    market.buy_goods(consumer, producer, 5)

    # Then
    assert producer.sales == 50.0


# ---------------------------------------------------
#  STATISTICS TESTS
# ----------------------------------------------------


@pytest.fixture
def producers(make_dlist):
    # Given
    producers = [Mock(id=i) for i in range(5)]
    producers = make_dlist(producers)
    producers.name = "producer"
    producers.price = 0
    producers.productivity = 0
    return producers


@pytest.fixture
def market_without_producers(market_without_roles, make_dlist):
    # Given
    others = make_dlist([Mock(id=i) for i in range(5)])
    others.name = "other"
    market = market_without_roles
    market.roles = {r.id: r for r in others}
    return market


@pytest.fixture
def market_with_producers(market_without_producers, producers):
    # Given
    market = market_without_producers
    market.roles.update({r.id: r for r in producers})
    return market, producers


def test_calc_inflation(market_without_producers):
    # Given
    market = market_without_producers
    market.average_price_prev = 10
    market.average_price = 12

    # When
    inflation = market.calc_inflation()

    # Then
    assert inflation == pytest.approx(0.2)


def test_calc_gdp(market_with_producers):
    # Given
    market, producers = market_with_producers
    market.get_stock = lambda x, y: 100 if x == "consumption" else 0

    # When
    gdp = market.calc_gdp()

    # Then
    assert gdp == 100 * len(producers)


def test_calc_productivity_range_for_all_producers(market_with_producers):
    # Given
    market, producers = market_with_producers
    producers.productivity = 1.0
    producers[2].productivity = 2.0

    # When
    range_ = market.calc_productivity_range()

    # Then
    assert range_ == (1.0, 2.0)


def test_calc_productivity_range_if_no_producers(market_without_producers):
    # Given
    market = market_without_producers

    # When
    range_ = market.calc_productivity_range()

    # Then
    assert range_ is None


def test_calc_price_range_for_all_producers(market_with_producers):
    # Given
    market, producers = market_with_producers
    producers.price = 10.0
    producers[1].price = 15.0

    # When
    range_ = market.calc_price_range()

    # Then
    assert range_ == (10.0, 15.0)


def test_calc_price_range_if_no_producers(market_without_producers):
    # Given
    market = market_without_producers

    # When
    range_ = market.calc_price_range()

    # Then
    assert range_ is None


def test_calc_sales_range_for_all_producers(market_with_producers):
    # Given
    market, producers = market_with_producers
    producers.sales = 100.0
    producers[1].sales = 150.0

    # When
    range_ = market.calc_sales_range()

    # Then
    assert range_ == (100.0, 150.0)


def test_calc_sales_range_if_no_producers(market_without_producers):
    # Given
    market = market_without_producers

    # When
    range_ = market.calc_sales_range()

    # Then
    assert range_ is None


# ---------------------------------------------------
# EVOLUTION
# ----------------------------------------------------


def test_clear_transactions_resets_each_producer_sales(market_with_producers):
    # Given
    market, producers = market_with_producers
    producers.sales = 100.0

    # When
    market.clear_transactions()

    # Then
    for producer in producers:
        assert producer.sales == 0


def test_clear_transactions_resets_each_producer_output(market_with_producers):
    # Given
    market, producers = market_with_producers
    producers.output = 50.0

    # When
    market.clear_transactions()

    # Then
    for producer in producers:
        assert producer.output == 0


@pytest.fixture
def market_before_update(market_with_producers):
    # Given
    market, _ = market_with_producers
    return market


def test_update_state_recalc_average_price(market_before_update, producers):
    # Given
    market = market_before_update
    market.average_price_prev = 0
    market.average_price = 0
    market.average_prod = 0
    producers.price = 5

    # When
    market.update_state()

    # Then
    assert market.average_price == pytest.approx(5.0)


def test_update_state_store_previous_average_price(market_before_update, producers):
    # Given
    market = market_before_update
    market.average_price_prev = 0
    market.average_price = 6.0
    market.average_prod = 0
    producers.price = 5

    # When
    market.update_state()

    # Then
    assert market.average_price_prev == 6.0


def test_update_state_recalc_average_productivity(market_before_update, producers):
    # Given
    market = market_before_update
    market.average_price_prev = 0
    market.average_price = 0
    market.average_prod = 0
    producers.productivity = 10

    # When
    market.update_state()

    # Then
    assert market.average_prod == pytest.approx(10.0)


@pytest.fixture
def market_with_defaults(market_without_roles):
    producers = [Mock(defaulted=val) for val in [True, False]]
    market = market_without_roles
    for role in producers:
        role.name = "producer"
        market.roles[role.agent.id] = role
    market.remove_role = Mock()
    return market, producers


def test_clear_defaults_removes_defaulted_producers(market_with_defaults):
    # Given
    market, producers = market_with_defaults

    # When
    market.clear_defaults()

    # Then
    assert call(producers[0]) in market.remove_role.call_args_list
    assert call(producers[1]) not in market.remove_role.call_args_list
    assert market.remove_role.call_count == 1
