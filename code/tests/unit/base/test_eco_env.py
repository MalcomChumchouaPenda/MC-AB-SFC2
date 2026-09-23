import pytest
from unittest.mock import Mock
from agentpy import AgentDList
from model.base import EcoSpace, EcoEnv


# ---------------------------------------------------
# ARCHITECTURE TESTS
# ---------------------------------------------------


def test_is_ecospace():
    # Assert
    assert issubclass(EcoEnv, EcoSpace)


@pytest.fixture
def env_before_setup():
    # Given
    model = Mock()
    env = EcoEnv(model)
    return env


def test_has_accounts_dlist(env_before_setup):
    # Given
    env = env_before_setup

    # When
    env.setup()

    # Then
    assert isinstance(env.accounts, AgentDList)


# ---------------------------------------------------
# ACCOUNT MANAGEMENT TESTS
# ----------------------------------------------------

FakeAccount = Mock()


@pytest.fixture
def env_with_accounts(monkeypatch, env_before_setup):
    # Given
    monkeypatch.setattr("model.base.EcoAccount", FakeAccount)
    env = env_before_setup
    env.accounts = []
    return env


def test_add_account_create_new_account(env_with_accounts):
    # Given
    agent = Mock()
    env = env_with_accounts

    # When
    account = env.add_account(agent)

    # Then
    FakeAccount.assert_called_with(agent.model)
    assert account is FakeAccount.return_value


def test_add_account_register_new_account(env_with_accounts):
    # Given
    agent = Mock()
    env = env_with_accounts

    # When
    account = env.add_account(agent)

    # Then
    assert account in env.accounts
    assert account is agent.account
    assert account.agent == agent


def test_add_account_setup_new_account(env_with_accounts):
    # Given
    agent = Mock()
    env = env_with_accounts

    # When
    account = env.add_account(agent)

    # Then
    assert account.setup.called