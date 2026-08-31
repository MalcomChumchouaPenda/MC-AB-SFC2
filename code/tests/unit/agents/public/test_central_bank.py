import pytest
from unittest.mock import Mock
from model.agents.public import CentralBank

# ---------------------------------------------------
# ARCHITECTURE TESTS
# ----------------------------------------------------


def test_is_eco_agent():
    # Given
    from model.base import EcoAgent

    # Assert
    assert issubclass(CentralBank, EcoAgent)
