
import pytest
import agentpy as ap
from unittest.mock import Mock
from mcabsfc.base import EcoRole


@pytest.fixture
def agent():
    return Mock(id=1)


def test_is_agentnode(agent):
    # When
    role = EcoRole(agent)

    # Then
    assert isinstance(role, ap.AgentNode)


def test_has_owner_reference(agent):
    # When
    role = EcoRole(agent)

    # Then
    assert role.owner is agent


def test_has_space_reference(agent):
    # When
    role = EcoRole(agent)

    # Then
    assert role.space is None

    
def test_has_generated_label(agent):
    # When
    role = EcoRole(agent)

    # Then
    assert role.label == agent.id
    