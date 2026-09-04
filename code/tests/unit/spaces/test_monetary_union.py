import pytest
from agentpy import AgentDList
from unittest.mock import Mock
from model.spaces.monetary_union import MonetaryUnion

# ---------------------------------------------------
# ARCHITECTURE TESTS
# ----------------------------------------------------


def test_is_eco_space():
    # Given
    from model.base import EcoSpace

    # Assert
    assert issubclass(MonetaryUnion, EcoSpace)


@pytest.fixture
def union_before_setup():
    # Given
    model = Mock()
    union = MonetaryUnion(model)
    return union


def test_has_accounts_dlist(union_before_setup):
    # Given
    union = union_before_setup

    # When
    union.setup()

    # Then
    assert isinstance(union.accounts, AgentDList)


# ---------------------------------------------------
# ROLES SET/REF TESTS
# ----------------------------------------------------


def test_has_monetary_authority_ref(union_before_setup):
    # Given
    union = union_before_setup

    # When
    union.setup()

    # Then
    assert union.monetary_authority is None


# ---------------------------------------------------
# SPACES SET/REF TESTS
# ----------------------------------------------------


def test_has_good_market_ref(union_before_setup):
    # Given
    union = union_before_setup

    # When
    union.setup()

    # Then
    assert union.good_market is None


def test_has_bond_market_ref(union_before_setup):
    # Given
    union = union_before_setup

    # When
    union.setup()

    # Then
    assert union.bond_market is None


def test_has_credit_market_ref(union_before_setup):
    # Given
    union = union_before_setup

    # When
    union.setup()

    # Then
    assert union.credit_market is None


# ---------------------------------------------------
# DYNAMIC STATE TESTS
# ----------------------------------------------------


def test_has_inflation_prop(union_before_setup):
    # Given
    union = union_before_setup

    # When
    union.setup()

    # Then
    assert union.inflation == 0.0


# ---------------------------------------------------
# ROLES / ACCOUNT MANAGEMENT TESTS
# ----------------------------------------------------


FakeAuthority = Mock()
FakeAccount = Mock()


@pytest.fixture
def union_without_authority(monkeypatch, union_before_setup):
    # Given
    monkeypatch.setattr("model.spaces.monetary_union.MonetaryAuthority", FakeAuthority)
    monkeypatch.setattr("model.spaces.monetary_union.EcoAccount", FakeAccount)
    union = union_before_setup
    union.add_role = Mock()
    union.accounts = []
    return union


def test_add_monetary_authority_add_appropriate_role(union_without_authority):
    # Given
    cb = Mock()
    union = union_without_authority

    # When
    role = union.add_monetary_authority(cb)

    # Then
    union.add_role.assert_called_with(FakeAuthority, cb, "monetary_authority")
    assert role == union.add_role.return_value


def test_add_monetary_authority_registers_role(union_without_authority):
    # Given
    cb = Mock()
    union = union_without_authority

    # When
    role = union.add_monetary_authority(cb)

    # Then
    assert union.monetary_authority is role


def test_add_monetary_authority_create_new_account(union_without_authority):
    # Given
    cb = Mock()
    union = union_without_authority

    # When
    union.add_monetary_authority(cb)

    # Then
    FakeAccount.assert_called_with(cb.model)


def test_add_account_register_new_account(union_without_authority):
    # Given
    cb = Mock()
    union = union_without_authority

    # When
    role = union.add_monetary_authority(cb)

    # Then
    assert role.account in union.accounts
    assert role.account is cb.account
    assert role.account.agent == cb


@pytest.fixture
def union_with_authority(union_without_authority):
    # Given
    authority = Mock()
    union = union_without_authority
    union.monetary_authority = authority
    return union, authority


def test_add_account_create_new_account(union_with_authority):
    # Given
    agent = Mock()
    union, _ = union_with_authority

    # When
    account = union.add_account(agent)

    # Then
    FakeAccount.assert_called_with(agent.model)
    assert account is FakeAccount.return_value


def test_add_account_register_new_account(union_with_authority):
    # Given
    agent = Mock()
    union, _ = union_with_authority

    # When
    account = union.add_account(agent)

    # Then
    assert account in union.accounts
    assert account is agent.account
    assert account.agent == agent


def test_add_account_links_to_authority(union_with_authority):
    # Given
    agent = Mock()
    union, authority = union_with_authority

    # When
    union.add_account(agent)

    # Then
    assert agent.cb_account is authority.account


# ---------------------------------------------------
# FIRM CREATION TESTS
# ----------------------------------------------------


@pytest.fixture
def union_before_creation(union_before_setup):
    # Given
    union = union_before_setup
    union.add_company = Mock()
    union.fund_company = Mock()
    union.good_market = Mock()
    union.bond_market = Mock()
    union.credit_market = Mock()
    return union


def test_place_trad_firm_in_goods_market(union_before_creation):
    # Given
    firm = Mock()
    union = union_before_creation

    # When
    union.place_firm(firm, tradable=True)

    # Then
    union.good_market.add_supplier.assert_called_with(firm)


def test_dont_place_non_trad_firm_in_goods_market(union_before_creation):
    # Given
    firm = Mock()
    union = union_before_creation

    # When
    union.place_firm(firm, tradable=False)

    # Then
    union.good_market.add_supplier.assert_not_called()


@pytest.mark.parametrize("tradable", [True, False])
def test_place_firm_add_borrower_role(union_before_creation, tradable):
    # Given
    firm = Mock()
    union = union_before_creation

    # When
    union.place_firm(firm, tradable=tradable)

    # Then
    union.credit_market.add_borrower.assert_called_with(firm)


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

    # When
    union.place_bank(bank)

    # Then
    union.credit_market.add_lender.assert_called_with(bank)
