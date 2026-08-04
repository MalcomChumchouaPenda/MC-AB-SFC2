import pytest
import agentpy as ap
from unittest.mock import Mock
from mcabsfc.roles import ConsumerRole, Role

# ---------------------------------------------------
# ARCHITECTURAL TESTS
# ----------------------------------------------------


def test_is_role():
    # Given
    market = Mock()
    owner = Mock(id=1)

    # When
    consumer = ConsumerRole(owner, market)

    # Then
    assert isinstance(consumer, Role)


def test_has_market():
    # Given
    market = Mock()
    owner = Mock(id=1)

    # When
    consumer = ConsumerRole(owner, market)

    # Then
    assert consumer.market == market
