import pytest
from model.base import EcoAccount

# ---------------------------------------------------
# ARCHITECTURE
# ----------------------------------------------------


def test_doesnt_inherit_from_agentpy_object():
    # Given
    from agentpy.objects import Object

    # When
    is_derived = issubclass(EcoAccount, Object)

    # Then
    assert not is_derived


def test_creates_default_stocks(monkeypatch):
    # Given
    monkeypatch.setattr("model.base.FINANCIAL_ASSETS", ["x", "y"])
    monkeypatch.setattr("model.base.REAL_ASSETS", ["z"])

    # When
    account = EcoAccount()

    # Then
    assert account.stocks == {"x": 0.0, "y": 0.0, "z": 0.0}


def test_creates_default_flows(monkeypatch):
    # Given
    monkeypatch.setattr("model.base.TRANSACTIONS", ["a", "b"])

    # When
    account = EcoAccount()

    # Then
    assert account.flows == {"a": 0.0, "b": 0.0}


# ---------------------------------------------------
# STOCKS ACCOUNTING
# ----------------------------------------------------


@pytest.fixture
def account(monkeypatch):
    # Given
    monkeypatch.setattr("model.base.FINANCIAL_ASSETS", [])
    monkeypatch.setattr("model.base.REAL_ASSETS", [])
    monkeypatch.setattr("model.base.TRANSACTIONS", [])
    return EcoAccount()


@pytest.fixture
def account_with_stocks(account):
    # Given
    stocks = {"x": 0.0}
    account.stocks = stocks
    return account, stocks


def test_incr_stock_increases_amount(account_with_stocks):
    # Given
    account, stocks = account_with_stocks

    # When
    account.incr_stock("x", 100)

    # Then
    assert stocks["x"] == 100


def test_decr_stock_decreases_amount(account_with_stocks):
    # Given
    account, stocks = account_with_stocks

    # When
    account.decr_stock("x", 100)

    # Then
    assert stocks["x"] == -100


# ---------------------------------------------------
# FLOWS ACCOUNTING
# ----------------------------------------------------


@pytest.fixture
def account_with_flows(account):
    # Given
    flows = {"a": 0}
    account.flows = flows
    return account, flows


def test_incr_flow_increases_amount(account_with_flows):
    # Given
    account, flows = account_with_flows

    # When
    account.incr_flow("a", 100)

    # Then
    assert flows["a"] == 100


def test_decr_flow_decreases_amount(account_with_flows):
    # Given
    account, flows = account_with_flows

    # When
    account.decr_flow("a", 100)

    # Then
    assert flows["a"] == -100


def test_clear_flows_reset_amount(account_with_flows):
    # Given
    account, flows = account_with_flows
    flows["a"] = 500

    # When
    account.clear_flows()

    # Then
    assert flows["a"] == 0
