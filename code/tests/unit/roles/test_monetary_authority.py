import pytest
from unittest.mock import Mock
from model.roles.monetary_authority import MonetaryAuthority

# ---------------------------------------------------
# ARCHITECTURE
# ----------------------------------------------------


def test_inherits_from_eco_role():
    # Given
    from model.extensions import EcoRole

    # When
    is_derived = issubclass(MonetaryAuthority, EcoRole)

    # Then
    assert is_derived


# ---------------------------------------------------
#  PERCEPTIONS
# ----------------------------------------------------


@pytest.fixture
def cash():
    # Given
    return {i: Mock(amount=100.0, interests=10.0) for i in range(5)}


def test_get_cash_amount(role, cash):
    # Given
    env = role.env
    env.cash = cash

    # When
    perceived = role.get_cash_amount()

    # Then
    assert perceived == pytest.approx(500.0)


def test_get_cash_interests(role, cash):
    # Given
    env = role.env
    env.cash = cash

    # When
    perceived = role.get_cash_interests()

    # Then
    assert perceived == pytest.approx(50.0)


# ---------------------------------------------------
# ACTIONS TESTS
# ----------------------------------------------------


@pytest.fixture
def role():
    # Given
    agent, env = Mock(), Mock()
    return MonetaryAuthority(agent, env)


def test_transfer_profits_with_env(role):
    # Given
    env = role.env

    # When
    role.transfer_profit(200)

    # Then
    env.transfer_central_bank_profits.assert_called_with(200)


def test_set_discount_rate_into_env(role):
    # Given
    env = role.env
    env.discount_rate = 0.0

    # When
    role.set_discount_rate(0.05)

    # Then
    assert env.discount_rate == 0.05
