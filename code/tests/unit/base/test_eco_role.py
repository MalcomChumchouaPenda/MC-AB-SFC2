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
