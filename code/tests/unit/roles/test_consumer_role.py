import pytest
import agentpy as ap
from unittest.mock import Mock
from mcabsfc.roles import ConsumerRole


def test_is_agent_node():
    assert issubclass(ConsumerRole, ap.AgentNode)


def test_has_owner_and_market():
    market = Mock()
    owner = Mock(id=1)

    role = ConsumerRole(owner, market)
    assert role.owner == owner
    assert role.market == market
    assert role.label == owner.id
