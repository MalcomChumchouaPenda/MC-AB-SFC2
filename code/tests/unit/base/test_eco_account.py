import pytest
from unittest.mock import Mock
from agentpy.objects import Object
from model.base import EcoAccount

# ---------------------------------------------------
# ARCHITECTURE TESTS
# ----------------------------------------------------


def test_is_agentpy_object():
    # Assert
    assert issubclass(EcoAccount, Object)


@pytest.fixture
def account_before_setup():
    # Given
    model = Mock()
    account = EcoAccount(model)
    account.setup()
    return account


def test_has_agent_id_ref(account_before_setup):
    # Given
    account = account_before_setup

    # When
    account.setup()

    # Then
    assert account.agent_id is None


def test_has_stocks_dict(account_before_setup):
    # Given
    account = account_before_setup

    # When
    account.setup()

    # Then
    assert account.stocks == {}


def test_has_flows_dict(account_before_setup):
    # Given
    account = account_before_setup

    # When
    account.setup()

    # Then
    assert account.flows == {}


# ---------------------------------------------------
# ACCOUNTING TESTS
# ----------------------------------------------------


@pytest.fixture
def account_with_stocks(account_before_setup):
    # Given
    stocks = {}
    account = account_before_setup
    account.stocks = stocks
    return account, stocks


def test_debit_stock_decrease_amount(account_with_stocks):
    # Given
    account, stocks = account_with_stocks

    # When
    account.debit_stock("cash", 100)

    # Then
    assert stocks["cash"] == -100


def test_credit_stock_increase_amount(account_with_stocks):
    # Given
    account, stocks = account_with_stocks

    # When
    account.credit_stock("cash", 100)

    # Then
    assert stocks["cash"] == 100


@pytest.fixture
def account_with_flows(account_before_setup):
    # Given
    flows = {}
    account = account_before_setup
    account.flows = flows
    return account, flows


def test_debit_flow_decrease_amount(account_with_flows):
    # Given
    account, flows = account_with_flows

    # When
    account.debit_flow("consumption", 100)

    # Then
    assert flows["consumption"] == -100


def test_credit_flow_increase_amount(account_with_flows):
    # Given
    account, flows = account_with_flows

    # When
    account.credit_flow("consumption", 100)

    # Then
    assert flows["consumption"] == 100


def test_clear_flows_clear_all_keys(account_with_flows):
    # Given
    account, flows = account_with_flows
    flows["consumption"] = 500

    # When
    account.clear_flows()

    # Then
    assert len(flows) == 0
