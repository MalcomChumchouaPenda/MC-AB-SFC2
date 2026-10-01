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


FakeGoodMarket = Mock()
FakeCreditMarket = Mock()
FakeBondMarket = Mock()
FakeCountry = Mock()


@pytest.fixture
def model_before_union_creation(fake_model, monkeypatch):
    # Given
    monkeypatch.setattr("model.spaces.monetary_union.GoodsMarket", FakeGoodMarket)
    monkeypatch.setattr("model.spaces.monetary_union.CreditMarket", FakeCreditMarket)
    monkeypatch.setattr("model.spaces.monetary_union.BondMarket", FakeBondMarket)
    monkeypatch.setattr("model.spaces.monetary_union.Country", FakeCountry)
    monkeypatch.setattr(MonetaryUnion, "add_space", Mock())
    model = fake_model
    model.p.K = 0
    return model


def test_initializes_average_inflation(model_before_union_creation):
    # Given
    model = model_before_union_creation

    # When
    union = MonetaryUnion(model)

    # Then
    assert union.average_inflation == 0.0


def test_initializes_discount_rate(model_before_union_creation):
    # Given
    model = model_before_union_creation

    # When
    union = MonetaryUnion(model)

    # Then
    assert union.discount_rate == 0.0


def test_creates_tradable_good_market(model_before_union_creation):
    # Given
    model = model_before_union_creation

    # When
    union = MonetaryUnion(model)

    # Then
    union.add_space.assert_any_call(FakeGoodMarket, "good_market", tradable=True)


def test_creates_credit_market(model_before_union_creation):
    # Given
    model = model_before_union_creation

    # When
    union = MonetaryUnion(model)

    # Then
    union.add_space.assert_any_call(FakeCreditMarket, "credit_market")


def test_creates_bond_market(model_before_union_creation):
    # Given
    model = model_before_union_creation

    # When
    union = MonetaryUnion(model)

    # Then
    union.add_space.assert_any_call(FakeBondMarket, "bond_market")


def test_creates_countries(model_before_union_creation):
    # Given
    model = model_before_union_creation
    model.p.K = 2

    # When
    union = MonetaryUnion(model)

    # Then
    union.add_space.assert_any_call(FakeCountry, "country_0")
    union.add_space.assert_any_call(FakeCountry, "country_1")


# ---------------------------------------------------
# ROLES MANAGEMENT
# ----------------------------------------------------

FakeMaker = Mock()


@pytest.fixture
def union_without_roles(monkeypatch, model_before_union_creation):
    # Given
    monkeypatch.setattr("model.spaces.monetary_union.PolicyMaker", FakeMaker)
    model = model_before_union_creation
    union = MonetaryUnion(model)
    union.add_role = Mock()
    union.spaces["good_market"] = Mock()
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
    market = union.spaces["good_market"]

    # When
    union.place_firm(firm, tradable=True)

    # Then
    market.add_producer.assert_called_with(firm)


def test_dont_place_non_trad_firm_in_goods_market(union_without_roles):
    # Given
    firm = Mock()
    union = union_without_roles
    market = union.spaces["good_market"] 

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


def test_update_average_inflation(model_before_union_creation):
    # Given
    countries = {f"country_{i}": Mock(inflation=0.05, gdp=100) for i in range(5)}
    model = model_before_union_creation
    union = MonetaryUnion(model)
    union.spaces = countries

    # When
    union.update_average_inflation()

    # Then
    assert union.average_inflation == pytest.approx(0.05)
