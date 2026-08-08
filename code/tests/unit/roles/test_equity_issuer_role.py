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
    equity_space = issuer.space

    # When
    issuer.update_equity_holdings()

    # Then
    equity_space.update_equity_holdings.assert_called_with(issuer)


def test_distribute_dividends(issuer):
    # Given
    equity_space = issuer.space

    # When
    issuer.distribute_dividends(100)

    # Then
    equity_space.distribute_dividends.assert_called_with(issuer, 100)
