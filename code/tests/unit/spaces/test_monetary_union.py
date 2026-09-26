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
def before_union_creation(monkeypatch):
    # Given
    monkeypatch.setattr("model.spaces.monetary_union.GoodsMarket", FakeGoodMarket)
    monkeypatch.setattr("model.spaces.monetary_union.CreditMarket", FakeCreditMarket)
    monkeypatch.setattr("model.spaces.monetary_union.BondMarket", FakeBondMarket)
    monkeypatch.setattr("model.spaces.monetary_union.Country", FakeCountry)
    monkeypatch.setattr(MonetaryUnion, "add_space", Mock())


@pytest.fixture
def model(fake_model):
    # Given
    model = fake_model
    model.p.K = 0
    return model


@pytest.mark.usefixtures("before_union_creation")
def test_initializes_average_inflation(model):
    # When
    union = MonetaryUnion(model)

    # Then
    assert union.average_inflation == 0.0


@pytest.mark.usefixtures("before_union_creation")
def test_initializes_discount_rate(model):
    # When
    union = MonetaryUnion(model)

    # Then
    assert union.discount_rate == 0.0


@pytest.mark.usefixtures("before_union_creation")
def test_creates_tradable_good_market(model):
    # When
    union = MonetaryUnion(model)

    # Then
    union.add_space.assert_any_call(FakeGoodMarket, "good_market", tradable=True)


@pytest.mark.usefixtures("before_union_creation")
def test_creates_credit_market(model):
    # When
    union = MonetaryUnion(model)

    # Then
    union.add_space.assert_any_call(FakeCreditMarket, "credit_market")


@pytest.mark.usefixtures("before_union_creation")
def test_creates_bond_market(model):
    # When
    union = MonetaryUnion(model)

    # Then
    union.add_space.assert_any_call(FakeBondMarket, "bond_market")


@pytest.mark.usefixtures("before_union_creation")
def test_creates_countries(model):
    # Given
    model.p.K = 2

    # When
    union = MonetaryUnion(model)

    # Then
    union.add_space.assert_any_call(FakeCountry, "country_0")
    union.add_space.assert_any_call(FakeCountry, "country_1")


# ---------------------------------------------------
# ROLES MANAGEMENT
# ----------------------------------------------------


@pytest.fixture
def union(model, before_union_creation):
    # Given
    _ = before_union_creation
    return MonetaryUnion(model)


FakeMaker = Mock()


@pytest.fixture
def before_role_creation(monkeypatch, union):
    # Given
    monkeypatch.setattr("model.spaces.monetary_union.PolicyMaker", FakeMaker)
    union.add_role = Mock()


@pytest.mark.usefixtures("before_role_creation")
def test_add_policy_maker_add_appropriate_role(union):
    # Given
    cb = Mock()

    # When
    role = union.add_policy_maker(cb)

    # Then
    union.add_role.assert_called_with(FakeMaker, cb, "policy_maker")
    assert role == union.add_role.return_value


# ---------------------------------------------------
# FIRM CREATION TESTS
# ----------------------------------------------------


@pytest.fixture
def before_firm_creation(union):
    # Given
    union.add_company = Mock()
    union.fund_company = Mock()
    union.spaces["good_market"] = Mock()
    union.spaces["credit_market"] = Mock()


@pytest.mark.usefixtures("before_firm_creation")
def test_place_trad_firm_in_goods_market(union):
    # Given
    firm = Mock()
    market = union.spaces["good_market"]

    # When
    union.place_firm(firm, tradable=True)

    # Then
    market.add_producer.assert_called_with(firm)


@pytest.mark.usefixtures("before_firm_creation")
def test_dont_place_non_trad_firm_in_goods_market(union):
    # Given
    firm = Mock()
    market = union.spaces["good_market"]

    # When
    union.place_firm(firm, tradable=False)

    # Then
    market.add_producer.assert_not_called()


@pytest.mark.usefixtures("before_firm_creation")
@pytest.mark.parametrize("tradable", [True, False])
def test_place_firm_add_borrower_role(union, tradable):
    # Given
    firm = Mock()
    market = union.spaces["credit_market"]

    # When
    union.place_firm(firm, tradable=tradable)

    # Then
    market.add_borrower.assert_called_with(firm)


# ---------------------------------------------------
# BANK CREATION TESTS
# ----------------------------------------------------


@pytest.fixture
def before_bank_creation(union):
    # Given
    union.add_company = Mock()
    union.fund_company = Mock()
    union.spaces["bond_market"] = Mock()
    union.spaces["credit_market"] = Mock()


@pytest.mark.usefixtures("before_bank_creation")
def test_place_bank_add_bond_buyer(union):
    # Given
    bank = Mock()
    market = union.spaces["bond_market"]

    # When
    union.place_bank(bank)

    # Then
    market.add_buyer.assert_called_with(bank)


@pytest.mark.usefixtures("before_bank_creation")
def test_place_bank_add_lender_role(union):
    # Given
    bank = Mock()
    market = union.spaces["credit_market"]

    # When
    union.place_bank(bank)

    # Then
    market.add_lender.assert_called_with(bank)


# ---------------------------------------------------
# INFLATION
# ----------------------------------------------------


def test_update_average_inflation(union):
    # Given
    union.spaces = {f"country_{i}": Mock(inflation=0.05, gdp=100) for i in range(5)}

    # When
    union.update_average_inflation()

    # Then
    assert union.average_inflation == pytest.approx(0.05)
