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


def test_get_average_price(govt_role):
    # Given
    country = govt_role.space
    country.average_price = 10

    # When
    average_price = govt_role.get_average_price()

    # Assert
    assert average_price == 10


def test_get_average_productivity(govt_role):
    # Given
    country = govt_role.space
    country.average_productivity = 2

    # When
    average_productivity = govt_role.get_average_productivity()

    # Assert
    assert average_productivity == 2


def test_get_households(govt_role):
    # Given
    households = [Mock() for _ in range(10)]
    country = govt_role.space
    country.get_households.return_value = households

    # When
    result = govt_role.get_households()

    # Assert
    assert result == households


def test_pay_public_transfers(govt_role):
    # Given
    household_role = Mock()
    country = govt_role.space

    # When
    govt_role.pay_public_transfers(household_role, 100)

    # Assert
    action = country.pay_public_transfers
    action.assert_called_with(govt_role, household_role, 100)
