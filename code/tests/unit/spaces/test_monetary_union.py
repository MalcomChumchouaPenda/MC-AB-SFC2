import pytest
from unittest.mock import Mock
from model.spaces.monetary_union import MonetaryUnion

# ---------------------------------------------------
# ARCHITECTURE
# ----------------------------------------------------


def test_inherits_from_eco_space():
    # Given
    from model.extensions import EcoSpace

    # When
    is_derived = issubclass(MonetaryUnion, EcoSpace)

    # Then
    assert is_derived


@pytest.fixture
def union(fake_model):
    # Given
    return MonetaryUnion(fake_model)


def test_initializes_average_inflation(union):
    # When
    default_value = union.average_inflation

    # Then
    assert default_value == 0.0


def test_initializes_discount_rate(union):
    # When
    default_value = union.discount_rate

    # Then
    assert default_value == 0.0


# ---------------------------------------------------
# SUB SPACES MANAGEMENT
# ----------------------------------------------------


@pytest.fixture
def union_without_spaces(union):
    # Given
    union.add_space = Mock()
    return union


def test_create_countries_adds_countries(union_without_spaces, monkeypatch):
    # Given
    country_cls = Mock(name="Country")
    monkeypatch.setattr("model.spaces.monetary_union.Country", country_cls)
    union = union_without_spaces
    union.p.country_number = 2

    # When
    union.create_countries()

    # Then
    union.add_space.assert_any_call(country_cls, "country_0")
    union.add_space.assert_any_call(country_cls, "country_1")
    assert union.add_space.call_count == 2


def test_create_countries_sets_countries_pos(union_without_spaces):
    # Given
    space = Mock()
    union = union_without_spaces
    union.add_space.return_value = space
    union.p.country_number = 1

    # When
    union.create_countries()

    # Then
    assert space.pos == 0


def test_create_countries_creates_national_markets(union_without_spaces):
    # Given
    country = Mock()
    union = union_without_spaces
    union.add_space.return_value = country
    union.p.country_number = 1

    # When
    union.create_countries()

    # Then
    country.create_markets.assert_called_once_with()


@pytest.fixture
def market_types(monkeypatch):
    # Given
    types = {}
    for name in ("GoodsMarket", "CreditMarket", "BondMarket"):
        market_cls = Mock(name=name)
        monkeypatch.setattr(f"model.spaces.country.{name}", market_cls)
        types[name] = market_cls
    return types


def test_create_markets_adds_tradable_goods_market(union_without_spaces, monkeypatch):
    # Given
    union = union_without_spaces
    market_cls = Mock(name="GoodsMarket")
    monkeypatch.setattr("model.spaces.monetary_union.GoodsMarket", market_cls)

    # When
    union.create_markets()

    # Then
    union.add_space.assert_any_call(market_cls, "goods_market", tradable=True)


def test_create_markets_adds_credit_market(union_without_spaces, monkeypatch):
    # Given
    union = union_without_spaces
    market_cls = Mock(name="CreditMarket")
    monkeypatch.setattr("model.spaces.monetary_union.CreditMarket", market_cls)

    # When
    union.create_markets()

    # Then
    union.add_space.assert_any_call(market_cls, "credit_market")


def test_create_markets_adds_bond_market(union_without_spaces, monkeypatch):
    # Given
    union = union_without_spaces
    market_cls = Mock(name="BondMarket")
    monkeypatch.setattr("model.spaces.monetary_union.BondMarket", market_cls)

    # When
    union.create_markets()

    # Then
    union.add_space.assert_any_call(market_cls, "bond_market")


# ---------------------------------------------------
# ROLES MANAGEMENT
# ----------------------------------------------------


@pytest.fixture
def union_without_cb(union):
    # Given
    union.add_role = Mock()
    return union


@pytest.mark.parametrize("national", [True, False])
def test_add_central_bank_adds_policy_maker(union_without_cb, monkeypatch, national):
    # Given
    role_cls = Mock(name="PolicyMaker")
    monkeypatch.setattr("model.spaces.monetary_union.PolicyMaker", role_cls)
    cb = Mock(national=national, country_pos=0)
    union = union_without_cb

    # When
    union.add_central_bank(cb)

    # Then
    union.add_role.assert_called_with(role_cls, cb)


# ---------------------------------------------------
# CASH OPERATIONS
# ----------------------------------------------------


@pytest.fixture
def before_cash_operations(union_without_spaces):
    # Given
    union = union_without_spaces
    union.spaces["country_0"] = Mock()
    union.spaces["country_1"] = Mock()
    return union


def test_decrease_cash_calls_country_method(before_cash_operations):
    # Given
    union = before_cash_operations
    country = union.spaces["country_1"]
    agent = Mock(country_pos=1)

    # When
    union.decrease_cash(agent, 10)

    # Then
    country.decrease_cash.assert_called_with(agent, 10)


def test_increase_cash_calls_country_method(before_cash_operations):
    # Given
    union = before_cash_operations
    country = union.spaces["country_0"]
    agent = Mock(country_pos=0)

    # When
    union.increase_cash(agent, 10)

    # Then
    country.increase_cash.assert_called_with(agent, 10)


# ---------------------------------------------------
# CURRENT INDICATORS
# ----------------------------------------------------


def test_calc_phi_range_from_goods_market(union):
    # Given
    market = Mock()
    union.spaces = {"goods_market": market}

    # When
    range_ = union.calc_phi_range()

    # Then
    assert range_ == market.calc_phi_range.return_value


def test_calc_price_range_from_goods_market(union):
    # Given
    market = Mock()
    union.spaces = {"goods_market": market}

    # When
    range_ = union.calc_price_range()

    # Then
    assert range_ == market.calc_price_range.return_value


def test_calc_sales_range_from_goods_market(union):
    # Given
    market = Mock()
    union.spaces = {"goods_market": market}

    # When
    range_ = union.calc_sales_range()

    # Then
    assert range_ == market.calc_sales_range.return_value


# ---------------------------------------------------
# INFLATION
# ----------------------------------------------------


@pytest.fixture
def countries():
    # Given
    return [Mock(pos=i, inflation=0.05, gdp=100) for i in range(5)]


@pytest.fixture
def union_before_update(union, countries):
    # Given
    for country in countries:
        union.spaces[f"country_{country.pos}"] = country
    union.spaces["any"] = Mock()
    return union


def test_update_state_updates_average_inflation(union_before_update):
    # Given
    union = union_before_update

    # When
    union.update_state()

    # Then
    assert union.average_inflation == pytest.approx(0.05)


def test_update_state_updates_each_subspace_state(union_before_update):
    # Given
    union = union_before_update

    # When
    union.update_state()

    # Then
    for subspace in union.spaces.values():
        subspace.update_state.assert_called_with()
