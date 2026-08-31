import pytest
from unittest.mock import Mock
from mc_ab_sfc2.roles.equity_issuer import EquityIssuerRole

# ---------------------------------------------------
# ARCHITECTURE TESTS
# ----------------------------------------------------


def test_is_eco_role():
    # Given
    from mc_ab_sfc2.base import EcoRole

    # Assert
    assert issubclass(EquityIssuerRole, EcoRole)


@pytest.fixture
def issuer():
    # Given
    space = Mock()
    agent = Mock(id=1)
    return EquityIssuerRole(agent, space)


def test_exposes_equity(issuer):
    # Given
    agent = issuer.agent
    agent.equity = 10

    # Assert
    assert issuer.equity == 10


def test_exposes_net_worth(issuer):
    # Given
    agent = issuer.agent
    agent.net_worth = 10

    # Assert
    assert issuer.net_worth == 10


# ---------------------------------------------------
# BEHAVIORAL TESTS
# ----------------------------------------------------


def test_get_average_wage(issuer):
    # Given
    country = issuer.space
    country.average_wage = 15.0

    # When
    wage = issuer.get_average_wage()

    # Assert
    assert wage == 15.0


def test_update_equity_holdings(issuer):
    # Given
    country = issuer.space

    # When
    issuer.update_equity_holdings()

    # Then
    country.update_equity_holdings.assert_called_with(issuer)


def test_distribute_dividends(issuer):
    # Given
    country = issuer.space

    # When
    issuer.distribute_dividends(100)

    # Then
    country.distribute_dividends.assert_called_with(issuer, 100)


def test_closes_firm_through_country(issuer):
    # Given
    country = issuer.space
    firm = Mock()

    # When
    issuer.close_firm(firm)

    # Then
    country.close_firm.assert_called_once_with(firm)


def test_closes_bank_through_country(issuer):
    # Given
    country = issuer.space
    bank = Mock()

    # When
    issuer.close_bank(bank)

    # Then
    country.close_bank.assert_called_once_with(bank)
