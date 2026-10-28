import pytest
from model.extensions import EcoAgent
from unittest.mock import Mock

# ---------------------------------------------------
# ARCHITECTURE
# ----------------------------------------------------


def test_inherits_from_agentpy_agent():
    # Given
    from agentpy import Agent

    # When
    is_derived = issubclass(EcoAgent, Agent)

    # Then
    assert is_derived


@pytest.fixture
def agent():
    # Given
    model = Mock()
    agent = EcoAgent(model)
    return agent


def test_initializes_roles_dict(fake_model):
    # Given
    model = fake_model

    # When
    agent = EcoAgent(model)

    # Then
    assert agent.roles == {}


def test_initializes_account(fake_model):
    # Given
    model = fake_model

    # When
    agent = EcoAgent(model)

    # Then
    assert agent.account is None


def test_initializes_country_pos(fake_model):
    # Given
    model = fake_model

    # When
    agent = EcoAgent(model)

    # Then
    assert agent.country_pos is None


# ---------------------------------------------------
#  OBSERVATION
# ----------------------------------------------------


@pytest.fixture
def agent(fake_model, monkeypatch):
    # Given
    model = fake_model
    agent = EcoAgent(model)
    monkeypatch.setattr("model.extensions.FINANCIAL_ASSETS", ["x"])
    return agent


def test_record_account_does_nothing_if_no_accounts(agent):
    # Given
    agent.account = None

    # When
    agent.record_account()

    # Then
    assert agent.log == {}


def test_record_account_records_each_item(agent):
    # Given
    agent.account = {"x": 20, "y": -20}

    # When
    agent.record_account()

    # Then
    assert agent.log["x"][-1] == 20
    assert agent.log["y"][-1] == -20



def test_record_account_records_financial_asset_changes(agent):
    # Given
    agent.account = {"x": 20, "y": -20}
    agent.record("x", 10)
    agent.model.t = 1

    # When
    agent.record_account()

    # Then
    assert agent.log["delta_x"][-1] == -10


def test_record_account_records_initial_asset_changes(agent):
    # Given
    agent.account = {"x": 20, "y": -20}
    agent.model.t = 0

    # When
    agent.record_account()

    # Then
    assert agent.log["delta_x"][-1] == -20