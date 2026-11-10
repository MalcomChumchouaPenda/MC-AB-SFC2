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


@pytest.fixture
def market(fake_model):
    # Given
    return GoodsMarket(fake_model)


def test_initializes_average_price(market):
    # When
    default_value = market.average_price

    # Then
    assert default_value == 0


def test_initializes_previous_average_price(market):
    # When
    default_value = market.average_price_prev

    # Then
    assert default_value == 0


def test_initializes_average_phi(market):
    # When
    default_value = market.average_phi

    # Then
    assert default_value == 0


# ---------------------------------------------------
# ROLES MANAGEMENT TESTS
# ----------------------------------------------------


@pytest.fixture
def market_without_roles(market):
    # Given
    market.env = Mock()
    market.add_role = Mock()
    return market


@pytest.fixture
def tradable_market(market_without_roles):
    # Given
    market = market_without_roles
    market.tradable = True
    return market


@pytest.fixture
def local_market(market_without_roles):
    # Given
    market = market_without_roles
    market.tradable = False
    market.env.pos = 2
    return market


def test_add_household_adds_any_consumer_if_tradable(tradable_market, monkeypatch):
    # Given
    role_cls = Mock(name="Consumer")
    monkeypatch.setattr("model.spaces.goods_market.Consumer", role_cls)
    market = tradable_market
    household = Mock()

    # When
    market.add_household(household)

    # Then
    market.add_role.assert_called_with(role_cls, household, prefix="trad")


def test_add_household_add_domestic_consumer_if_non_tradable(local_market, monkeypatch):
    # Given
    household = Mock(country_pos=2)
    role_cls = Mock(name="Consumer")
    monkeypatch.setattr("model.spaces.goods_market.Consumer", role_cls)
    market = local_market

    # When
    market.add_household(household)

    # Then
    market.add_role.assert_called_with(role_cls, household, prefix="non_trad")


def test_add_household_does_nothing_for_foreigners_if_non_tradable(local_market):
    # Given
    household = Mock(country_pos=3)
    market = local_market

    # When
    market.add_household(household)

    # Then
    market.add_role.assert_not_called()


def test_add_firm_adds_producer_for_complier_if_tradable(tradable_market, monkeypatch):
    # Given
    firm = Mock(tradable=True)
    role_cls = Mock(name="Producer")
    monkeypatch.setattr("model.spaces.goods_market.Producer", role_cls)
    market = tradable_market

    # When
    market.add_firm(firm)

    # Then
    market.add_role.assert_called_with(role_cls, firm)


def test_add_firm_doesnt_add_role_for_non_complier_if_tradable(tradable_market):
    # Given
    firm = Mock(tradable=False)
    market = tradable_market

    # When
    market.add_firm(firm)

    # Then
    market.add_role.assert_not_called()


def test_add_firm_adds_domestic_producer_if_non_tradable(local_market, monkeypatch):
    # Given
    role_cls = Mock(name="Producer")
    monkeypatch.setattr("model.spaces.goods_market.Producer", role_cls)
    firm = Mock(tradable=False, country_pos=2)
    market = local_market

    # When
    market.add_firm(firm)

    # Then
    market.add_role.assert_called_with(role_cls, firm)


def test_add_firm_doesnt_add_role_for_foreigners_if_non_tradable(local_market):
    # Given
    firm = Mock(tradable=False, country_pos=3)
    market = local_market

    # When
    market.add_firm(firm)

    # Then
    market.add_role.assert_not_called()


# ---------------------------------------------------
# MATCHING / TRANSACTIONS TESTS
# ----------------------------------------------------


@pytest.fixture
def consumer():
    # Given
    return Mock()


@pytest.fixture
def producer():
    # Given
    return Mock(price=10, inventories=100, sales=0)


@pytest.fixture
def market_before_transact(market):
    # Given
    market.env = Mock()
    market.transfer_stock = Mock()
    market.make_transaction = Mock()
    random = market.model.random
    random.sample = Mock(side_effect=lambda pop, k: pop[:k])
    return market


def test_buy_goods_transfers_cash(market_before_transact, consumer, producer):
    # Given
    market = market_before_transact

    # When
    market.buy_goods(consumer, producer, 5)

    # Then
    market.transfer_stock.assert_any_call("cash", consumer.id, producer.id, 50)


def test_buy_goods_updates_accounts(market_before_transact, consumer, producer):
    # Given
    market = market_before_transact

    # When
    market.buy_goods(consumer, producer, 5)

    # Then
    market.make_transaction.assert_any_call("consumption", consumer.id, producer.id, 50)


def test_buy_goods_decrease_inventories(market_before_transact, consumer, producer):
    # Given
    market = market_before_transact

    # When
    market.buy_goods(consumer, producer, 5)

    # Then
    assert producer.inventories == 95.0


def test_buy_goods_increases_sales(market_before_transact, consumer, producer):
    # Given
    market = market_before_transact

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
    producers = [Mock(id=i) for i in range(2)]
    producers = make_dlist(producers)
    producers.name = "producer"
    producers.price = 0
    producers.phi = 0
    return producers


@pytest.fixture
def others(make_dlist):
    # Given
    others = make_dlist([Mock(id=i) for i in range(5)])
    others.name = "other"
    return others


@pytest.fixture
def market_without_producers(market, others):
    # Given
    market.roles = {r.id: r for r in others}
    return market


def test_calc_inflation(market_without_producers):
    # Given
    market = market_without_producers
    market.average_price_prev = 10
    market.average_price = 12

    # When
    inflation = market.calc_inflation()

    # Then
    assert inflation == pytest.approx(0.2)


@pytest.fixture
def market_with_producers(market_without_producers, producers):
    # Given
    market = market_without_producers
    market.roles.update({r.id: r for r in producers})
    return market


def test_calc_gdp(market_with_producers, producers):
    # Given
    market = market_with_producers
    market.get_stock = lambda x, y: 100 if x == "consumption" else 0

    # When
    gdp = market.calc_gdp()

    # Then
    assert gdp == 100 * len(producers)


def test_calc_phi_range_for_all_producers(market_with_producers, producers):
    # Given
    market = market_with_producers
    producers[0].phi = 1.0
    producers[1].phi = 2.0

    # When
    range_ = market.calc_phi_range()

    # Then
    assert range_ == (1.0, 2.0)


def test_calc_phi_range_if_no_producers(market_without_producers):
    # Given
    market = market_without_producers

    # When
    range_ = market.calc_phi_range()

    # Then
    assert range_ is None


def test_calc_price_range_for_all_producers(market_with_producers, producers):
    # Given
    market = market_with_producers
    producers[0].price = 10.0
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


def test_calc_sales_range_for_all_producers(market_with_producers, producers):
    # Given
    market = market_with_producers
    producers[0].sales = 100.0
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


def test_clear_transactions_resets_producer_sales(market_with_producers, producers):
    # Given
    market = market_with_producers
    producers.sales = 100.0

    # When
    market.clear_transactions()

    # Then
    for producer in producers:
        assert producer.sales == 0


def test_clear_transactions_resets_producer_output(market_with_producers, producers):
    # Given
    market = market_with_producers
    producers.output = 50.0

    # When
    market.clear_transactions()

    # Then
    for producer in producers:
        assert producer.output == 0


def test_update_state_recalc_average_price(market_with_producers, producers):
    # Given
    market = market_with_producers
    market.average_price_prev = 0
    market.average_price = 0
    market.average_phi = 0
    producers.price = 5

    # When
    market.update_state()

    # Then
    assert market.average_price == pytest.approx(5.0)


def test_update_state_store_previous_average_price(market_with_producers, producers):
    # Given
    market = market_with_producers
    market.average_price_prev = 0
    market.average_price = 6.0
    market.average_phi = 0
    producers.price = 5

    # When
    market.update_state()

    # Then
    assert market.average_price_prev == 6.0


def test_update_state_recalc_average_phi(market_with_producers, producers):
    # Given
    market = market_with_producers
    market.average_price_prev = 0
    market.average_price = 0
    market.average_phi = 0
    producers.phi = 10

    # When
    market.update_state()

    # Then
    assert market.average_phi == pytest.approx(10.0)


@pytest.fixture
def market_with_defaults(market, producers):
    producers[0].defaulted = True
    producers[1].defaulted = False
    for role in producers:
        market.roles[role.id] = role
    market.remove_role = Mock()
    return market


def test_clear_defaults_removes_defaulted_producers(market_with_defaults, producers):
    # Given
    market = market_with_defaults

    # When
    market.clear_defaults()

    # Then
    assert call(producers[0]) in market.remove_role.call_args_list
    assert call(producers[1]) not in market.remove_role.call_args_list
    assert market.remove_role.call_count == 1
