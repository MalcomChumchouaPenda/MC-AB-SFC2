import pytest
from agentpy import AgentDList
from unittest.mock import Mock
from model.spaces.monetary_union import MonetaryUnion

# ---------------------------------------------------
# ARCHITECTURE TESTS
# ----------------------------------------------------


def test_is_eco_env():
    # Given
    from model.base import EcoEnv

    # Assert
    assert issubclass(MonetaryUnion, EcoEnv)


FakeGoodMarket = Mock()
FakeCreditMarket = Mock()
FakeBondMarket = Mock()
FakeCountry = Mock()


@pytest.fixture
def union_before_setup(monkeypatch):
    # Given
    monkeypatch.setattr("model.spaces.monetary_union.GoodsMarket", FakeGoodMarket)
    monkeypatch.setattr("model.spaces.monetary_union.CreditMarket", FakeCreditMarket)
    monkeypatch.setattr("model.spaces.monetary_union.BondMarket", FakeBondMarket)
    monkeypatch.setattr("model.spaces.monetary_union.Country", FakeCountry)
    model = Mock()
    model.p.K = 0
    union = MonetaryUnion(model)
    union.add_space = Mock()
    return union


def test_has_policy_maker_ref(union_before_setup):
    # Given
    union = union_before_setup

    # When
    union.setup()

    # Then
    assert union.policy_maker is None


def test_has_policy_implementer_dlist(union_before_setup):
    # Given
    union = union_before_setup

    # When
    union.setup()

    # Then
    assert isinstance(union.policy_implementers, AgentDList)


# ---------------------------------------------------
# SPACES
# ----------------------------------------------------


def test_setup_add_tradable_good_market(union_before_setup):
    # Given
    union = union_before_setup

    # When
    union.setup()

    # Then
    union.add_space.assert_any_call(FakeGoodMarket, "good_market", tradable=True)
    

def test_setup_creates_credit_market(union_before_setup):
    # Given
    union = union_before_setup

    # When
    union.setup()

    # Then
    union.add_space.assert_any_call(FakeCreditMarket, "credit_market")


def test_setup_creates_bond_market(union_before_setup):
    # Given
    union = union_before_setup

    # When
    union.setup()

    # Then
    assert union.bond_market is FakeBondMarket.return_value
    assert union.bond_market.setup.called


def test_setup_creates_countries(union_before_setup):
    # Given
    union = union_before_setup
    union.p.K = 2

    # When
    union.setup()

    # Then
    assert len(union.countries) == 2
    for i in range(2):
        assert union.countries[i] is FakeCountry.return_value
        assert union.countries[i].setup.called


def test_setup_create_links_with_countries(union_before_setup):
    # Given
    country = Mock()
    FakeCountry.return_value = country
    union = union_before_setup
    union.p.K = 1

    # When
    union.setup()

    # Then
    assert union is country.union


# ---------------------------------------------------
# DYNAMIC STATE TESTS
# ----------------------------------------------------


def test_has_average_inflation_prop(union_before_setup):
    # Given
    union = union_before_setup

    # When
    union.setup()

    # Then
    assert union.average_inflation == 0.0


# ---------------------------------------------------
# ROLES / ACCOUNT MANAGEMENT TESTS
# ----------------------------------------------------


FakeMaker = Mock()


@pytest.fixture
def union_without_policy_maker(monkeypatch, union_before_setup):
    # Given
    monkeypatch.setattr("model.spaces.monetary_union.PolicyMaker", FakeMaker)
    union = union_before_setup
    union.add_role = Mock()
    return union


def test_add_policy_maker_add_appropriate_role(union_without_policy_maker):
    # Given
    cb = Mock()
    union = union_without_policy_maker

    # When
    role = union.add_policy_maker(cb)

    # Then
    union.add_role.assert_called_with(FakeMaker, cb, "policy_maker")
    assert role == union.add_role.return_value


def test_add_policy_maker_registers_role(union_without_policy_maker):
    # Given
    cb = Mock()
    union = union_without_policy_maker

    # When
    role = union.add_policy_maker(cb)

    # Then
    assert union.policy_maker is role


FakeImplementer = Mock()


@pytest.fixture
def union_without_policy_impl(monkeypatch, union_before_setup):
    # Given
    monkeypatch.setattr(
        "model.spaces.monetary_union.PolicyImplementer", FakeImplementer
    )
    union = union_before_setup
    union.policy_implementers = []
    union.add_role = Mock()
    return union


def test_add_policy_implementer_add_appropriate_role(union_without_policy_impl):
    # Given
    cb = Mock()
    union = union_without_policy_impl

    # When
    role = union.add_policy_implementer(cb)

    # Then
    union.add_role.assert_called_with(FakeImplementer, cb, "policy_implementer")
    assert role == union.add_role.return_value


def test_add_policy_implementer_registers_role(union_without_policy_impl):
    # Given
    cb = Mock()
    union = union_without_policy_impl

    # When
    role = union.add_policy_implementer(cb)

    # Then
    assert union.policy_implementers == [role]


# ---------------------------------------------------
# FIRM CREATION TESTS
# ----------------------------------------------------


@pytest.fixture
def union_before_creation(union_before_setup):
    # Given
    union = union_before_setup
    union.add_company = Mock()
    union.fund_company = Mock()
    union.spaces["good_market"] = Mock()
    union.bond_market = Mock()
    union.spaces["credit_market"] = Mock()
    return union


def test_place_trad_firm_in_goods_market(union_before_creation):
    # Given
    firm = Mock()
    union = union_before_creation

    # When
    union.place_firm(firm, tradable=True)

    # Then
    union.spaces["good_market"].add_producer.assert_called_with(firm)


def test_dont_place_non_trad_firm_in_goods_market(union_before_creation):
    # Given
    firm = Mock()
    union = union_before_creation

    # When
    union.place_firm(firm, tradable=False)

    # Then
    union.spaces["good_market"].add_producer.assert_not_called()


@pytest.mark.parametrize("tradable", [True, False])
def test_place_firm_add_borrower_role(union_before_creation, tradable):
    # Given
    firm = Mock()
    union = union_before_creation
    market = union.spaces["credit_market"]

    # When
    union.place_firm(firm, tradable=tradable)

    # Then
    market.add_borrower.assert_called_with(firm)


# ---------------------------------------------------
# BANK CREATION TESTS
# ----------------------------------------------------


def test_place_bank_add_bond_buyer(union_before_creation):
    # Given
    bank = Mock()
    union = union_before_creation

    # When
    union.place_bank(bank)

    # Then
    union.bond_market.add_buyer.assert_called_with(bank)


def test_place_bank_add_lender_role(union_before_creation):
    # Given
    bank = Mock()
    union = union_before_creation
    market = union.spaces["credit_market"]

    # When
    union.place_bank(bank)

    # Then
    market.add_lender.assert_called_with(bank)


# ---------------------------------------------------
# CASH TRANSFER
# ----------------------------------------------------


@pytest.fixture
def union_with_policy_maker(union_without_policy_maker):
    # Given
    authority = Mock()
    union = union_without_policy_maker
    union.monetary_authority = authority
    return union, authority


def test_transfer_cash_between_agents_updates_accounts(union_with_policy_maker):
    # Given
    source, target = Mock(), Mock()
    union, _ = union_with_policy_maker

    # When
    union.transfer_cash(source, target, 100)

    # Then
    source.account.debit_stock.assert_any_call("cash", 100)
    target.account.credit_stock.assert_any_call("cash", 100)


# ---------------------------------------------------
# INFLATION
# ----------------------------------------------------


def test_update_average_inflation(union_before_setup):
    # Given
    union = union_before_setup
    union.countries = {i: Mock(inflation=0.05, gdp=100) for i in range(5)}

    # When
    union.update_average_inflation()

    # Then
    assert union.average_inflation == pytest.approx(0.05)
