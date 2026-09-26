import pytest
from model.tools import EcoModel

# ---------------------------------------------------
# ARCHITECTURE
# ----------------------------------------------------

def test_inherits_from_agentpy_model():
    # Given
    from agentpy import Model

    # When
    is_derived = issubclass(EcoModel, Model)

    # Then
    assert is_derived


@pytest.fixture
def model():
    # Given
    return EcoModel()


def test_contains_agents_collection(model):
    # Assert
    assert isinstance(model.agents, dict)


def test_contains_spaces_collection(model):
    # Assert
    assert isinstance(model.spaces, dict)
