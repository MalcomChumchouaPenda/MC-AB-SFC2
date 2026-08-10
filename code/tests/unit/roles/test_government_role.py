import pytest
from unittest.mock import Mock
from mc_ab_sfc.roles import GovernmentRole

# ---------------------------------------------------
# ARCHITECTURE TESTS
# ----------------------------------------------------


def test_is_eco_role():
    # Given
    from mc_ab_sfc.base import EcoRole

    # Assert
    assert issubclass(GovernmentRole, EcoRole)


@pytest.fixture
def govt_role():
    # Given
    market = Mock()
    agent = Mock(id=1)
    return GovernmentRole(agent, market)


def test_exposes_tax_rate(govt_role):
    # Given
    govt = govt_role.agent
    govt.tax_rate = 0.15

    # Assert
    assert govt_role.tax_rate == 0.15


def test_get_gdp(govt_role):
    # Given
    country = govt_role.space
    country.gdp = 100

    # When
    gdp = govt_role.get_gdp()

    # Assert
    assert gdp == 100
