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

    

def test_has_owner():
    # Given
    owner = Mock(id=1)

    # When
    role = Role(owner)

    # Then
    assert role.owner == owner



def test_has_label_generated_from_owner_id():
    # Given
    owner = Mock(id=2)

    # When
    role = Role(owner)

    # Then
    assert role.label == owner.id



# ---------------------------------------------------
# BEHAVIORAL TESTS
# ----------------------------------------------------

def test_access_owner_stocks():
    # Given
    agent = Mock()
    agent.stocks = {"deposit": 100}
    role = Role(agent)

    # When
    stock = role.get_stock("deposit")

    # Then
    assert stock == 100


def test_access_owner_flows():
    # Given
    agent = Mock()
    agent.flows = {"wage_income": 50}
    role = Role(agent)

    # When
    flow = role.get_flow("wage_income")

    # Then
    assert flow == 50

