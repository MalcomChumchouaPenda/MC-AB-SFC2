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


def test_initializes_average_inflation(fake_model):
    # Given
    model = fake_model

    # When
    union = MonetaryUnion(model)

    # Then
    assert union.average_inflation == 0.0


def test_initializes_discount_rate(fake_model):
    # Given
    model = fake_model

    # When
    union = MonetaryUnion(model)

    # Then
    assert union.discount_rate == 0.0


# ---------------------------------------------------
# SUB SPACES MANAGEMENT
# ----------------------------------------------------


@pytest.fixture
def union_without_spaces(fake_model, monkeypatch):
    # Given
    monkeypatch.setattr(MonetaryUnion, "add_space", Mock())
    union = MonetaryUnion(fake_model)
    union.spaces = {}
    return union


FakeCountry = Mock()


@pytest.fixture
def union_without_countries(union_without_spaces, monkeypatch):
    # Given
    monkeypatch.setattr("model.spaces.monetary_union.Country", FakeCountry)
    union = union_without_spaces
    return union


def test_create_countries_adds_countries(union_without_countries):
    # Given
    union = union_without_countries
    union.p.country_number = 2

    # When
    union.create_countries()

    # Then
    union.add_space.assert_any_call(FakeCountry, "country_0")
    union.add_space.assert_any_call(FakeCountry, "country_1")
    assert union.add_space.call_count == 2


def test_create_countries_sets_countries_pos(union_without_countries):
    # Given
    space = Mock()
    union = union_without_countries
    union.add_space.return_value = space
    union.p.country_number = 1

    # When
    union.create_countries()

    # Then
    assert space.pos == 0


def test_create_countries_creates_national_markets(union_without_countries):
    # Given
    country = Mock()
    union = union_without_countries
    union.add_space.return_value = country
    union.p.country_number = 1

    # When
    union.create_countries()

    # Then
    country.create_markets.assert_called_once_with()


FakeGoodMarket = Mock()
FakeCreditMarket = Mock()
FakeBondMarket = Mock()


@pytest.fixture
def union_without_markets(union_without_spaces, monkeypatch):
    # Given
    monkeypatch.setattr("model.spaces.monetary_union.GoodsMarket", FakeGoodMarket)
    monkeypatch.setattr("model.spaces.monetary_union.CreditMarket", FakeCreditMarket)
    monkeypatch.setattr("model.spaces.monetary_union.BondMarket", FakeBondMarket)
    union = union_without_spaces
    return union


def test_create_markets_adds_tradable_goods_market(union_without_markets):
    # Given
    union = union_without_markets

    # When
    union.create_markets()

    # Then
    union.add_space.assert_any_call(FakeGoodMarket, "goods_market", tradable=True)


def test_create_markets_adds_credit_market(union_without_markets):
    # Given
    union = union_without_markets

    # When
    union.create_markets()

    # Then
    union.add_space.assert_any_call(FakeCreditMarket, "credit_market")


def test_create_markets_adds_bond_market(union_without_markets):
    # Given
    union = union_without_markets

    # When
    union.create_markets()

    # Then
    union.add_space.assert_any_call(FakeBondMarket, "bond_market")


# ---------------------------------------------------
# ROLES MANAGEMENT
# ----------------------------------------------------

FakeMaker = Mock()


@pytest.fixture
def before_adding_agent(monkeypatch, fake_model):
    # Given
    monkeypatch.setattr("model.spaces.monetary_union.PolicyMaker", FakeMaker)
    union = MonetaryUnion(fake_model)
    union.add_role = Mock()
    return union


@pytest.mark.parametrize("national", [True, False])
def test_add_central_bank_add_policy_maker_role(before_adding_agent, national):
    # Given
    cb = Mock(national=national, country_pos=0)
    union = before_adding_agent

    # When
    union.add_central_bank(cb)

    # Then
    union.add_role.assert_called_with(FakeMaker, cb)


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


def test_calc_phi_range_from_goods_market(union_without_spaces):
    # Given
    market = Mock()
    union = union_without_spaces
    union.spaces = {"goods_market": market}

    # When
    range_ = union.calc_phi_range()

    # Then
    assert range_ == market.calc_phi_range.return_value


def test_calc_price_range_from_goods_market(union_without_spaces):
    # Given
    market = Mock()
    union = union_without_spaces
    union.spaces = {"goods_market": market}

    # When
    range_ = union.calc_price_range()

    # Then
    assert range_ == market.calc_price_range.return_value


def test_calc_sales_range_from_goods_market(union_without_spaces):
    # Given
    market = Mock()
    union = union_without_spaces
    union.spaces = {"goods_market": market}

    # When
    range_ = union.calc_sales_range()

    # Then
    assert range_ == market.calc_sales_range.return_value


# ---------------------------------------------------
# INFLATION
# ----------------------------------------------------


@pytest.fixture
def union_before_update(fake_model):
    # Given
    countries = {f"country_{i}": Mock(inflation=0.05, gdp=100) for i in range(5)}
    union = MonetaryUnion(fake_model)
    union.spaces = {"any": Mock()}
    union.spaces.update(countries)
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
