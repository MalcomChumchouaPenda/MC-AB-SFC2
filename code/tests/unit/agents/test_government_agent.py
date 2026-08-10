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
def govt():
    # Given
    model = Mock()
    return GovernmentAgent(model)


def test_has_default_stocks(govt):
    # Assert
    assert govt.reserves == 0
    assert govt.bonds == 0


def test_has_default_flows(govt):
    # Assert
    assert govt.taxes == 0


def test_has_default_choices(govt):
    # Assert
    assert govt.tax_rate == 0


def test_has_default_indicators(govt):
    # Assert
    assert govt.gdp == 0
