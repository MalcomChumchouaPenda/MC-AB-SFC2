import pytest
import agentpy as ap
from unittest.mock import Mock
from mcabsfc.roles import ConsumerRole

# ---------------------------------------------------
# ARCHITECTURAL TESTS
# ----------------------------------------------------


def test_is_agent_node():
    # Given
    market = Mock()
    owner = Mock(id=1)

    # When
    consumer = ConsumerRole(owner, market)

    # Then
    assert isinstance(consumer, ap.AgentNode)


def test_has_owner_and_market():
    # Given
    market = Mock()
    owner = Mock(id=1)

    # When
    consumer = ConsumerRole(owner, market)

    # Then
    assert consumer.market == market
    assert consumer.owner == owner
    assert consumer.label == owner.id
