import pytest
from unittest.mock import Mock
from agentpy.objects import Object
from model.base import EcoAccount

# ---------------------------------------------------
# ARCHITECTURE TESTS
# ----------------------------------------------------


def test_is_not_agentpy_object():
    # Assert
    assert not issubclass(EcoAccount, Object)


@pytest.fixture
def account():
    # Given
    return EcoAccount()


def test_has_stock_names_constant(account):
    # Assert
    assert account.stocks == {
        "deposits": 0.0,
        "loans": 0.0,
        "inventories": 0.0,
        "bonds": 0.0,
        "cash": 0.0,
        "advances": 0.0,
        "equities": 0.0,
    }


def test_has_flow_names_constant(account):
    # Assert
    assert account.flows == {
        "consumption": 0.0,
        "wages": 0.0,
        "public_transfers": 0.0,
        "taxes": 0.0,
        "dep_interests": 0.0,
        "loan_interests": 0.0,
        "loan_defaults": 0.0,
        "bond_interests": 0.0,
        "cash_interests": 0.0,
        "adv_interests": 0.0,
        "dividends": 0.0,
        "profit_transfers": 0.0,
    }


# ---------------------------------------------------
# STOCKS ACCOUNTING
# ----------------------------------------------------


@pytest.fixture
def account_with_stocks(account):
    # Given
    stocks = {"cash": 0}
    account.stocks = stocks
    return account, stocks


def test_incr_stock_increases_amount(account_with_stocks):
    # Given
    account, stocks = account_with_stocks

    # When
    account.incr_stock("cash", 100)

    # Then
    assert stocks["cash"] == 100


def test_decr_stock_decreases_amount(account_with_stocks):
    # Given
    account, stocks = account_with_stocks

    # When
    account.decr_stock("cash", 100)

    # Then
    assert stocks["cash"] == -100


# ---------------------------------------------------
# FLOWS ACCOUNTING
# ----------------------------------------------------


@pytest.fixture
def account_with_flows(account):
    # Given
    flows = {"consumption": 0}
    account.flows = flows
    return account, flows


def test_incr_flow_increases_amount(account_with_flows):
    # Given
    account, flows = account_with_flows

    # When
    account.incr_flow("consumption", 100)

    # Then
    assert flows["consumption"] == 100


def test_decr_flow_decreases_amount(account_with_flows):
    # Given
    account, flows = account_with_flows

    # When
    account.decr_flow("consumption", 100)

    # Then
    assert flows["consumption"] == -100


def test_clear_flows_reset_amount(account_with_flows):
    # Given
    account, flows = account_with_flows
    flows["consumption"] = 500

    # When
    account.clear_flows()

    # Then
    assert flows["consumption"] == 0
