import pytest
import agentpy as ap
from unittest.mock import Mock
from mcabsfc.roles import Role

# ---------------------------------------------------
# ARCHITECTURAL TESTS
# ----------------------------------------------------


def test_is_agent_node():
    # Given
    owner = Mock(id=1)

    # When
    role = Role(owner)

    # Then
    assert isinstance(role, ap.AgentNode)


def test_has_owner_and_label_generated():
    # Given
    owner = Mock(id=1)

    # When
    role = Role(owner)

    # Then
    assert role.owner == owner
    assert role.label == owner.id


# ---------------------------------------------------
# BEHAVIORAL TESTS
# ----------------------------------------------------


def test_access_owner_stocks_and_flows():
    # Given
    agent = Mock()
    agent.stocks = {"deposit": 100}
    agent.flows = {"wage_income": 50}
    role = Role(agent)

    # When
    stock = role.get_stock("deposit")
    flow = role.get_flow("wage_income")

    # Then
    assert stock == 100
    assert flow == 50

def test_role_can_credit_and_debit_stock():
    # Given
    agent = Mock()
    agent.stocks = {"deposit": 100}
    role = Role(agent)

    # When
    role.credit_stock("deposit", 50)
    role.debit_stock("deposit", 20)

    # Then
    assert agent.stocks["deposit"] == 130

    