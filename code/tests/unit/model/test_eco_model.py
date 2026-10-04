import pytest
from unittest.mock import Mock
from model.model import EcoModel

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
