import pytest
from unittest.mock import Mock
from model.spaces.monetary_union import MonetaryUnion

# ---------------------------------------------------
# ARCHITECTURE
# ----------------------------------------------------


def test_inherits_from_eco_space():
    # Given
    from model.base import EcoSpace

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

    # When
    union.create_countries(2)

    # Then
    union.add_space.assert_any_call(FakeCountry, "country_0")
    union.add_space.assert_any_call(FakeCountry, "country_1")
    assert union.add_space.call_count == 2


def test_create_countries_creates_national_markets(union_without_countries):
    # Given
    country = Mock()
    union = union_without_countries
    union.add_space.return_value = country

    # When
    union.create_countries(1)

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
def union_without_roles(monkeypatch, fake_model):
    # Given
    monkeypatch.setattr("model.spaces.monetary_union.PolicyMaker", FakeMaker)
    union = MonetaryUnion(fake_model)
    union.add_role = Mock()
    union.spaces["goods_market"] = Mock()
    union.spaces["bond_market"] = Mock()
    union.spaces["credit_market"] = Mock()
    return union


def test_add_policy_maker_creates_proper_role(union_without_roles):
    # Given
    cb = Mock()
    union = union_without_roles

    # When
    union.add_policy_maker(cb)

    # Then
    union.add_role.assert_called_with(FakeMaker, cb, "policy_maker")


def test_add_policy_maker_returns_created_role(union_without_roles):
    # Given
    cb = Mock()
    union = union_without_roles

    # When
    role = union.add_policy_maker(cb)

    # Then
    assert role == union.add_role.return_value


def test_place_trad_firm_in_goods_market(union_without_roles):
    # Given
    firm = Mock()
    union = union_without_roles
    market = union.spaces["goods_market"]

    # When
    union.place_firm(firm, tradable=True)

    # Then
    market.add_producer.assert_called_with(firm)


def test_dont_place_non_trad_firm_in_goods_market(union_without_roles):
    # Given
    firm = Mock()
    union = union_without_roles
    market = union.spaces["goods_market"]

    # When
    union.place_firm(firm, tradable=False)

    # Then
    market.add_producer.assert_not_called()


@pytest.mark.parametrize("tradable", [True, False])
def test_place_firm_add_borrower_role(union_without_roles, tradable):
    # Given
    firm = Mock()
    union = union_without_roles
    market = union.spaces["credit_market"]

    # When
    union.place_firm(firm, tradable=tradable)

    # Then
    market.add_borrower.assert_called_with(firm)


def test_place_bank_add_bond_buyer(union_without_roles):
    # Given
    bank = Mock()
    union = union_without_roles
    market = union.spaces["bond_market"]

    # When
    union.place_bank(bank)

    # Then
    market.add_buyer.assert_called_with(bank)


def test_place_bank_add_lender_role(union_without_roles):
    # Given
    bank = Mock()
    union = union_without_roles
    market = union.spaces["credit_market"]

    # When
    union.place_bank(bank)

    # Then
    market.add_lender.assert_called_with(bank)


# ---------------------------------------------------
# INFLATION
# ----------------------------------------------------


def test_update_average_inflation(fake_model):
    # Given
    countries = {f"country_{i}": Mock(inflation=0.05, gdp=100) for i in range(5)}
    union = MonetaryUnion(fake_model)
    union.spaces = countries

    # When
    union.update_average_inflation()

    # Then
    assert union.average_inflation == pytest.approx(0.05)
