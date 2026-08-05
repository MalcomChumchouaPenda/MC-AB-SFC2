import pytest
import agentpy as ap
from mcabsfc.model import EcoModel


def test_is_agentpy_model():
    # Assert
    assert issubclass(EcoModel, ap.Model)


# Given
@pytest.fixture
def model():
    return EcoModel()


def test_contains_agents_collection(model):
    # Assert
    assert isinstance(model.agents, dict)


def test_contains_spaces_collection(model):
    # Assert
    assert isinstance(model.spaces, dict)
