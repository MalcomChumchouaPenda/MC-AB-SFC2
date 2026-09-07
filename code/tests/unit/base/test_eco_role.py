import pytest
from agentpy.objects import Object
from unittest.mock import Mock
from model.base import EcoRole

# ---------------------------------------------------
# ARCHITECTURE TESTS
# ----------------------------------------------------


def test_is_agentpy_object():
    # Assert
    assert issubclass(EcoRole, Object)


@pytest.fixture
def role_before_setup():
    # Given
    model = Mock()
    role = EcoRole(model)
    return role


def test_has_name_attr(role_before_setup):
    # Given
    role = role_before_setup

    # When
    role.setup()

    # Then
    assert role.name == ""


def test_has_agent_ref(role_before_setup):
    # Given
    role = role_before_setup

    # When
    role.setup()

    # Then
    assert role.agent is None


def test_has_space_ref(role_before_setup):
    # Given
    role = role_before_setup

    # When
    role.setup()

    # Then
    assert role.space is None


# ---------------------------------------------------
# ROLE ACCOUNT ACCESS TESTS
# ----------------------------------------------------


@pytest.fixture
def role_with_agent(role_before_setup):
    # Given
    agent = Mock()
    role = role_before_setup
    role.agent = agent
    return role, agent


def test_expose_agent_account(role_with_agent):
    # Given
    role, agent = role_with_agent

    # When
    exposed = role.account

    # Then
    assert exposed is agent.account


def test_expose_agent_central_bank_account(role_with_agent):
    # Given
    role, agent = role_with_agent

    # When
    exposed = role.cb_account

    # Then
    assert exposed is agent.cb_account


def test_expose_agent_deposit_bank_account(role_with_agent):
    # Given
    role, agent = role_with_agent

    # When
    exposed = role.bank_account

    # Then
    assert exposed is agent.bank_account


def test_change_agent_deposit_bank_account(role_with_agent):
    # Given
    role, agent = role_with_agent
    new_account = Mock()

    # When
    role.bank_account = new_account

    # Then
    assert agent.bank_account is new_account


def test_expose_agent_country(role_with_agent):
    # Given
    role, agent = role_with_agent

    # When
    agent.country = 2

    # Then
    assert role.country == 2


# ---------------------------------------------------
# ACCOUNTING TESTS
# ----------------------------------------------------


@pytest.fixture
def role_with_account(role_before_setup):
    # Given
    account = Mock()
    role = role_before_setup
    role.agent = Mock(account=account)
    return role, account


def test_debit_stock_decrease_amount(role_with_account):
    # Given
    role, account = role_with_account

    # When
    role.debit_stock("cash", 100)

    # Then
    account.debit_stock.assert_called_with("cash", 100)


def test_credit_stock_increase_amount(role_with_account):
    # Given
    role, account = role_with_account

    # When
    role.credit_stock("cash", 100)

    # Then
    account.credit_stock.assert_called_with("cash", 100)


def test_debit_flow_decrease_amount(role_with_account):
    # Given
    role, account = role_with_account

    # When
    role.debit_flow("consumption", 100)

    # Then
    account.debit_flow.assert_called_with("consumption", 100)


def test_credit_flow_increase_amount(role_with_account):
    # Given
    role, account = role_with_account

    # When
    role.credit_flow("consumption", 100)

    # Then
    account.credit_flow.assert_called_with("consumption", 100)


def test_clear_flows_clear_all_keys(role_with_account):
    # Given
    role, account = role_with_account

    # When
    role.clear_flows()

    # Then
    account.clear_flows.assert_called_with()
