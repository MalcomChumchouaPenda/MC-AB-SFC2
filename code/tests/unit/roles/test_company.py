import pytest
from unittest.mock import Mock
from model.base import EcoRole
from model.roles.company import Company

# ---------------------------------------------------
# ARCHITECTURE TESTS
# ----------------------------------------------------


def test_inherits_from_eco_role():
    # Assert
    assert issubclass(Company, EcoRole)


@pytest.fixture
def role():
    # Given
    agent, env = Mock(), Mock()
    return Company(agent, env)


def test_has_sector(role):
    # Assert
    assert role.sector == ""


def test_has_net_worth(role):
    # Assert
    assert role.net_worth == 0


def test_has_defaulted(role):
    # Assert
    assert role.defaulted is False


# ---------------------------------------------------
#  PERCEPTIONS
# ----------------------------------------------------


def test_get_average_wage(role):
    # Given
    env = role.env
    env.average_wage = 15.0

    # When
    perceived = role.get_average_wage()

    # Assert
    assert perceived == 15.0


def test_get_equity_shares_from_env(role):
    # Given
    env = role.env

    # When
    found = role.get_equity_shares()

    # Assert
    env.find_links.assert_called_with(role, "founder")
    assert found == env.find_links.return_value


def test_get_tax_rate(role):
    # Given
    env = role.env
    env.fiscal_authority.tax_rate = 0.2

    # When
    perceived = role.get_tax_rate()

    # Assert
    assert perceived == 0.2


def test_get_discount_rate(role):
    # Given
    env = role.env
    env.monetary_authority.discount_rate = 0.05

    # When
    perceived = role.get_discount_rate()

    # Assert
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
