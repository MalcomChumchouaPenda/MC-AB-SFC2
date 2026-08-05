import agentpy as ap
from mcabsfc.model import EcoModel


def test_is_agentpy_model():
    # When
    model = EcoModel()

    # Then
    assert isinstance(model, ap.Model)


def test_contains_agents_collection():
    # When
    model = EcoModel()

    # Then
    assert isinstance(model.agents, dict)


def test_contains_spaces_collection():
    # When
    model = EcoModel()

    # Then
    assert isinstance(model.spaces, dict)
