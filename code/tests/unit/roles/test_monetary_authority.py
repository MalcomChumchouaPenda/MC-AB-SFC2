import pytest
from unittest.mock import Mock
from model.roles.monetary_authority import MonetaryAuthority

# ---------------------------------------------------
# ARCHITECTURE TESTS
# ----------------------------------------------------


def test_is_eco_role():
    # Given
    from model.base import EcoRole

    # Assert
    assert issubclass(MonetaryAuthority, EcoRole)


@pytest.fixture
def authority_before_setup():
    # Given
    model = Mock()
    authority = MonetaryAuthority(model)
    return authority


def test_expose_discount_rate_from_agent(authority_before_setup):
    # Given
    agent = Mock(discount_rate=0.02)
    authority = authority_before_setup
    authority.agent = agent

    # When
    perceived = authority.discount_rate

    # Then
    assert perceived == 0.02


# ---------------------------------------------------
# PERCEPTION TESTS
# ----------------------------------------------------


# ---------------------------------------------------
# ACTIONS TESTS
# ----------------------------------------------------


@pytest.fixture
def authority_with_env(authority_before_setup):
    # Given
    env = Mock()
    authority = authority_before_setup
    authority.env = env
    return authority, env


def test_transfer_profits_with_env(authority_with_env):
    # Given
    authority, env = authority_with_env

    # When
    authority.transfer_profit(200)

    # Then
    env.transfer_central_bank_profits.assert_called_with(200)
