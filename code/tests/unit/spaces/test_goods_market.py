import pytest
from unittest.mock import Mock
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
def test_add_household_add_consumer_role(market_without_roles, tradable, prefix):
    # Given
    market = market_without_roles
    market.tradable = tradable
    household = Mock()

    # When
    market.add_household(household)

    # Then
    market.add_role.assert_called_with(FakeConsumer, household, prefix=prefix)


@pytest.mark.parametrize("tradable", [True, False])
def test_add_household_sets_role_preference(market_without_roles, tradable):
    # Given
    role = Mock()
    market = market_without_roles
    market.add_role.return_value = role
    market.tradable = tradable
    household = Mock()

    # When
    market.add_household(household)

    # Then
    assert role.preference == household.preference


def test_add_firm_add_producer_role(market_without_roles):
    # Given
    firm = Mock()
    market = market_without_roles

    # When
    market.add_firm(firm)

    # Then
    market.add_role.assert_called_with(FakeProducer, firm)


def test_add_firm_sets_role_variety(market_without_roles):
    # Given
    role = Mock()
    firm = Mock()
    market = market_without_roles
    market.add_role.return_value = role

    # When
    market.add_firm(firm)

    # Then
    assert role.variety == firm.variety


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
    producer = Mock(price=10, inventories=100)
    market = market_before_transaction

    # When
    market.buy_goods(consumer, producer, 5)

    # Then
    market.transfer_stock.assert_any_call("cash", consumer.id, producer.id, 50)
    market.make_transaction.assert_any_call("consumption", consumer.id, producer.id, 50)


def test_buy_goods_decrease_inventories(market_before_transaction):
    # Given
    consumer = Mock()
    producer = Mock(price=10, inventories=100)
    market = market_before_transaction

    # When
    market.buy_goods(consumer, producer, 5)

    # Then
    assert producer.inventories == 95.0


# ---------------------------------------------------
# EVOLUTION TESTS
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
def market_before_update(market_without_roles, producers, make_dlist):
    # Given
    others = make_dlist([Mock(id=i) for i in range(5)])
    others.name = "other"
    market = market_without_roles
    market.roles = others + producers
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


# ---------------------------------------------------
#  STATISTICS TESTS
# ----------------------------------------------------


def test_calc_inflation(market_before_update):
    # Given
    market = market_before_update
    market.average_price_prev = 10
    market.average_price = 12

    # When
    inflation = market.calc_inflation()

    # Then
    assert inflation == pytest.approx(0.2)


def test_calc_gdp(market_before_update, producers):
    # Given
    market = market_before_update
    market.get_stock = lambda x, y: 100 if x == "consumption" else 0

    # When
    gdp = market.calc_gdp()

    # Then
    assert gdp == 100 * len(producers)
