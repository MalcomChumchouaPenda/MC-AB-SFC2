import pytest
from unittest.mock import Mock
from model.base import EcoRole
from model.roles.fiscal_authority import FiscalAuthority

# ---------------------------------------------------
# ARCHITECTURE TESTS
# ----------------------------------------------------


def test_is_eco_role():
    # Assert
    assert issubclass(FiscalAuthority, EcoRole)


@pytest.fixture
def role():
    # Given
    agent, env = Mock(), Mock()
    return FiscalAuthority(agent, env)


def test_expose_tax_rate_from_agent(role):
    # Given
    role.agent.tax_rate = 0.02

    # When
    exposed = role.tax_rate

    # Then
    assert exposed == 0.02


# ---------------------------------------------------
# PERCEPTION TESTS
# ----------------------------------------------------


def test_get_gdp_from_env(role):
    # Given
    env = role.env
    env.gdp = 500

    # When
    perceived = role.get_gdp()

    # Then
    assert perceived == 500


@pytest.fixture
def role_with_good_market(role):
    # Given
    market = Mock()
    env = role.env
    env.spaces = {"good_market": market}
    return role, market


def test_get_average_price_from_env(role_with_good_market):
    # Given
    role, market = role_with_good_market
    market.average_price = 1.5

    # When
    perceived = role.get_average_price()

    # Then
    assert perceived == 1.5


def test_get_average_productivity_from_env(role_with_good_market):
    # Given
    role, market = role_with_good_market
    market.average_prod = 1.0

    # When
    perceived = role.get_average_productivity()

    # Then
    assert perceived == 1.0


def test_find_citizens_from_env(role):
    # Given
    env = role.env

    # When
    perceived = role.find_citizens()

    # Then
    env.find_all_roles.assert_called_with("citizen")
    assert perceived == env.find_all_roles.return_value


# ---------------------------------------------------
# ACTION TESTS
# ----------------------------------------------------


def test_pay_public_transfers_from_env(role):
    # Given
    citizen = Mock()
    env = role.env

    # When
    role.pay_public_transfers(citizen, 100)

    # Then
    env.pay_public_transfers(role, citizen, 100)
