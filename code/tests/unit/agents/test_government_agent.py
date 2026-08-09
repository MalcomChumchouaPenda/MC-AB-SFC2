import pytest
from unittest.mock import Mock
from mc_ab_sfc.agents import GovernmentAgent

# ---------------------------------------------------
# ARCHITECTURE TESTS
# ----------------------------------------------------


def test_is_eco_agent():
    # Given
    from mc_ab_sfc.base import EcoAgent

    # Assert
    assert issubclass(GovernmentAgent, EcoAgent)


@pytest.fixture
def government():
    # Given
    model = Mock()
    return GovernmentAgent(model)


def test_has_default_stocks(government):
    # Assert
    assert government.reserves == 0
    assert government.bonds == 0


def test_has_default_memory(government):
    # Assert
    assert government.gdp == 0
