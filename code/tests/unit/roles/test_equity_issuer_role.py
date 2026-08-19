import pytest
from unittest.mock import Mock
from mc_ab_sfc.roles import EquityIssuerRole

# ---------------------------------------------------
# ARCHITECTURE TESTS
# ----------------------------------------------------


def test_is_eco_role():
    # Given
    from mc_ab_sfc.base import EcoRole

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
