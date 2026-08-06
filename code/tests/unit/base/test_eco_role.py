import pytest
import agentpy as ap
from unittest.mock import Mock
from mcabsfc.base import EcoRole


def test_is_agentnode():
    # Assert
    assert issubclass(EcoRole, ap.AgentNode)


def test_requires_owner_and_space():
    # Assert
    expected = "required positional arguments: 'owner' and 'space'"
    with pytest.raises(TypeError, match=expected):
        EcoRole()


def test_has_owner_and_space_reference():
    # Given
    agent = Mock(id=1)
    space = Mock()
    role = EcoRole(agent, space)

    # Assert
    assert role.owner is agent
    assert role.space is space


def test_has_generated_label():
    # Given
    agent = Mock(id=1)
    space = Mock()
    role = EcoRole(agent, space)

    # Assert
    assert role.label == agent.id


class DummyAgent:
    def __init__(self):
        self.id = 1
        self.deposits = 100
        self.equity = 50
        self.labor_income = 0
        self.interest_income = 0


def test_increase_stock_increases_agent_stock():
    # Given
    space = Mock()
    agent = DummyAgent()
    role = EcoRole(agent, space)

    # When
    role.increase_stock("deposits", 25)

    # Then
    assert agent.deposits == 125


def test_decrease_stock_decreases_agent_stock():
    # Given
    space = Mock()
    agent = DummyAgent()
    role = EcoRole(agent, space)

    # When
    role.decrease_stock("deposits", 40)

    # Then
    assert agent.deposits == 60


def test_increase_flow_increases_agent_flow():
    # Given
    space = Mock()
    agent = DummyAgent()
    role = EcoRole(agent, space)

    # When
    role.increase_flow("labor_income", 100)

    # Then
    assert agent.labor_income == 100


def test_decrease_flow_decreases_agent_flow():
    # Given
    space = Mock()
    agent = DummyAgent()
    role = EcoRole(agent, space)

    # When
    role.increase_flow("labor_income", 100)
    role.decrease_flow("labor_income", 30)

    # Then
    assert agent.labor_income == 70


def test_accounting_methods_use_existing_attributes_only():
    # Given
    space = Mock()
    agent = DummyAgent()
    role = EcoRole(agent, space)

    # Assert
    expected = "has no attribute 'unknown'"
    with pytest.raises(AttributeError, match=expected):
        role.increase_stock("unknown", 10)
    with pytest.raises(AttributeError, match=expected):
        role.decrease_stock("unknown", 10)
    with pytest.raises(AttributeError, match=expected):
        role.increase_flow("unknown", 10)
    with pytest.raises(AttributeError, match=expected):
        role.decrease_flow("unknown", 10)
