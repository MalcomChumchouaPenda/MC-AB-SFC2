import pytest
import agentpy as ap
from unittest.mock import Mock
from mcabsfc.base import EcoRole


def test_is_agentnode():
    # Assert
    assert issubclass(EcoRole, ap.AgentNode)


def test_has_owner_reference():
    # Given
    agent = Mock(id=1)
    role = EcoRole(agent)

    # Assert
    assert role.owner is agent


def test_has_space_reference():
    # Given
    agent = Mock(id=1)
    role = EcoRole(agent)

    # Assert
    assert role.space is None


def test_has_generated_label():
    # Given
    agent = Mock(id=1)
    role = EcoRole(agent)

    # Assert
    assert role.label == agent.id
