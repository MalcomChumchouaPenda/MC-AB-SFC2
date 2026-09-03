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
# ACCOUNT MANAGEMENT TESTS
# ----------------------------------------------------

FakeAccount = Mock()


@pytest.fixture
def union_with_accounts(monkeypatch, union_before_setup):
    # Given
    accounts = []
    union = union_before_setup
    union.accounts = accounts
    monkeypatch.setattr("model.spaces.monetary_union.EcoAccount", FakeAccount)
    return union, accounts


def test_add_account_create_new_account(union_with_accounts):
    # Given
    agent = Mock()
    union, _ = union_with_accounts

    # When
    account = union.add_account(agent)

    # Then
    FakeAccount.assert_called_with(agent.model)
    assert account is FakeAccount.return_value


def test_add_account_register_new_account(union_with_accounts):
    # Given
    agent = Mock()
    union, accounts = union_with_accounts

    # When
    account = union.add_account(agent)

    # Then
    assert account in accounts
    assert account is agent.account
    assert account.agent_id == agent.id


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
