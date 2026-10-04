import pytest
from unittest.mock import Mock
from model.roles.company import Company

# ---------------------------------------------------
# ARCHITECTURE
# ----------------------------------------------------


def test_inherits_from_eco_role():
    # Given
    from model.base import EcoRole

    # When
    is_derived = issubclass(Company, EcoRole)

    # Then
    assert is_derived


def test_initializes_sector():
    # Given
    agent, env = Mock(), Mock()

    # When
    role = Company(agent, env)

    # Then
    assert role.sector == ""


def test_initializes_net_worth():
    # Given
    agent, env = Mock(), Mock()

    # When
    role = Company(agent, env)

    # Then
    assert role.net_worth == 0


def test_initializes_defaulted():
    # Given
    agent, env = Mock(), Mock()

    # When
    role = Company(agent, env)

    # Then
    assert role.defaulted is False


# ---------------------------------------------------
#  PERCEPTIONS
# ----------------------------------------------------


@pytest.fixture
def role():
    # Given
    agent, env = Mock(), Mock()
    return Company(agent, env)


def test_get_average_wage(role):
    # Given
    env = role.env
    env.average_wage = 15.0

    # When
    perceived = role.get_average_wage()

    # Then
    assert perceived == 15.0


def test_get_equity_shares_from_env(role):
    # Given
    env = role.env

    # When
    found = role.get_equity_shares()

    # Then
    env.find_links.assert_called_with(role, "founder")
    assert found == env.find_links.return_value


def test_get_tax_rate(role):
    # Given
    env = role.env
    env.tax_rate = 0.2

    # When
    perceived = role.get_tax_rate()

    # Then
    assert perceived == 0.2


def test_get_discount_rate(role):
    # Given
    env = role.env
    env.discount_rate = 0.05

    # When
    perceived = role.get_discount_rate()

    # Then
    assert perceived == 0.05


# ---------------------------------------------------
# ACTIONS
# ----------------------------------------------------


def test_pay_dividends(role):
    # Given
    env = role.env
    founder = Mock()

    # When
    role.pay_dividends(founder, 50)

    # Then
    env.pay_dividends.assert_called_with(role, founder, 50)


def test_pay_taxes_uses_env_method(role):
    # Given
    env = role.env

    # When
    role.pay_taxes(50)

    # Then
    env.pay_taxes.assert_called_with(role, 50)


def test_update_equity_share_uses_env_method(role):
    # Given
    env = role.env
    founder = Mock()

    # When
    role.update_equity_share(founder, -50)

    # Then
    env.update_equity_share.assert_called_with(role, founder, -50)


def test_transfer_residual_cash_uses_env_method(role):
    # Given
    env = role.env
    founder = Mock()

    # When
    role.transfer_residual_cash(founder, 50)

    # Then
    env.transfer_residual_cash.assert_called_with(role, founder, 50)


def test_request_advances_uses_env_method(role):
    # Given
    env = role.env

    # When
    role.request_advances(100)

    # Then
    env.request_advances.assert_called_with(role, 100)


def test_repay_advances_uses_env_method(role):
    # Given
    env = role.env

    # When
    role.repay_advances(100, 10)

    # Then
    env.repay_advances.assert_called_with(role, 100, 10)
