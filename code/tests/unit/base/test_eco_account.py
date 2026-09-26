import pytest
from model.base import EcoAccount

# ---------------------------------------------------
# ARCHITECTURE TESTS
# ----------------------------------------------------


def test_doesnt_inherit_from_agentpy_object():
    # Given
    from agentpy.objects import Object

    # When
    is_derived = issubclass(EcoAccount, Object)

    # Then
    assert not is_derived


@pytest.fixture
def stock_and_flow_names(monkeypatch):
    # Given
    stock_names = ["x", "y"]
    flow_names = ["a", "b"]
    monkeypatch.setattr("model.base.STOCK_NAMES", stock_names)
    monkeypatch.setattr("model.base.FLOW_NAMES", flow_names)
    return stock_names, flow_names


def test_creates_default_stocks(stock_and_flow_names):
    # Given
    stock_names, _ = stock_and_flow_names

    # When
    account = EcoAccount()

    # Then
    for name in stock_names:
        assert account.stocks[name] == 0.0


def test_creates_default_flows(stock_and_flow_names):
    # Given
    _, flow_names = stock_and_flow_names

    # When
    account = EcoAccount()

    # Then
    for name in flow_names:
        assert account.flows[name] == 0.0


# ---------------------------------------------------
# STOCKS ACCOUNTING
# ----------------------------------------------------


@pytest.fixture
def account_with_nothing(monkeypatch):
    # Given
    monkeypatch.setattr("model.base.STOCK_NAMES", [])
    monkeypatch.setattr("model.base.FLOW_NAMES", [])
    return EcoAccount()


@pytest.fixture
def account_with_stocks(account_with_nothing):
    # Given
    stocks = {"x": 0}
    account = account_with_nothing
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
def account_with_flows(account_with_nothing):
    # Given
    flows = {"a": 0}
    account = account_with_nothing
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
