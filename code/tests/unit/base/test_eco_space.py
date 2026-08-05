import pytest
import agentpy as ap
from unittest.mock import Mock
from mcabsfc.base import EcoSpace


def test_is_agentpy_network():
    # Assert
    assert issubclass(EcoSpace, ap.Network)


def test_contains_roles_collection():
    # Given
    model = Mock()
    space = EcoSpace(model)

    # Assert
    assert isinstance(space.roles, dict)
