
import pytest
import agentpy as ap
from unittest.mock import Mock
from mcabsfc.base import EcoSpace


@pytest.fixture
def model():
    return Mock()


def test_is_agentpy_network(model):
    # When
    space = EcoSpace(model)

    # Then
    assert isinstance(space, ap.Network)


def test_contains_roles_collection(model):
    # When
    space = EcoSpace(model)

    # Then
    assert isinstance(space.roles, dict)
