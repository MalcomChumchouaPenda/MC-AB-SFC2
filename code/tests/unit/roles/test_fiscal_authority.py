import pytest
from unittest.mock import Mock
from model.roles.fiscal_authority import FiscalAuthority

# ---------------------------------------------------
# ARCHITECTURE TESTS
# ----------------------------------------------------


def test_is_eco_role():
    # Given
    from model.base import EcoRole

    # Assert
    assert issubclass(FiscalAuthority, EcoRole)


@pytest.fixture
def authority_before_setup():
    # Given
    model = Mock()
    authority = FiscalAuthority(model)
    return authority


def test_expose_tax_rate_from_agent(authority_before_setup):
    # Given
    agent = Mock()
    authority = authority_before_setup
    authority.agent = agent

    # When
    agent.tax_rate = 0.02

    # Then
    assert authority.tax_rate == 0.02


# ---------------------------------------------------
# PERCEPTION TESTS
# ----------------------------------------------------


@pytest.fixture
def authority_with_space(authority_before_setup):
    # Given
    space = Mock()
    authority = authority_before_setup
    authority.space = space
    return authority, space


def test_get_gdp_from_space(authority_with_space):
    # Given
    authority, space = authority_with_space
    space.gdp = 500

    # When
    perceived = authority.get_gdp()

    # Then
    assert perceived == 500


def test_get_average_price_from_space(authority_with_space):
    # Given
    authority, space = authority_with_space
    space.good_market.average_price = 1.5

    # When
    perceived = authority.get_average_price()

    # Then
    assert perceived == 1.5


def test_get_average_productivity_from_space(authority_with_space):
    # Given
    authority, space = authority_with_space
    space.good_market.average_prod = 1.0

    # When
    perceived = authority.get_average_productivity()

    # Then
    assert perceived == 1.0


def test_find_citizens_from_space(authority_with_space):
    # Given
    authority, space = authority_with_space

    # When
    perceived = authority.find_citizens()

    # Then
    assert perceived == space.find_citizens.return_value


# ---------------------------------------------------
# ACTION TESTS
# ----------------------------------------------------

def test_pay_public_transfers_from_space(authority_with_space):
    # Given
    citizen = Mock()
    authority, space = authority_with_space

    # When
    authority.pay_public_transfers(citizen, 100)

    # Then
    space.pay_public_transfers(authority, citizen, 100)
    