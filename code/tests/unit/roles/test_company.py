import pytest
from unittest.mock import Mock
from model.roles.company import Company

# ---------------------------------------------------
# ARCHITECTURE TESTS
# ----------------------------------------------------


def test_is_eco_role():
    # Given
    from model.base import EcoRole

    # Assert
    assert issubclass(Company, EcoRole)


@pytest.fixture
def role_with_env():
    # Given
    agent, env = Mock(), Mock()
    role = Company(agent, env)
    return role, env


def test_has_sector(role_with_env):
    # Given
    role, _ = role_with_env

    # Assert
    assert role.sector == ""


def test_has_net_worth(role_with_env):
    # Given
    role, _ = role_with_env

    # Assert
    assert role.net_worth == 0


def test_has_defaulted(role_with_env):
    # Given
    role, _ = role_with_env

    # Assert
    assert role.defaulted is False


# ---------------------------------------------------
#  PERCEPTIONS
# ----------------------------------------------------


def test_get_average_wage(role_with_env):
    # Given
    role, env = role_with_env
    env.average_wage = 15.0

    # When
    perceived = role.get_average_wage()

    # Assert
    assert perceived == 15.0


def test_get_equity_shares_from_env(role_with_env):
    # Given
    role, env = role_with_env

    # When
    found = role.get_equity_shares()

    # Assert
    env.find_equity_shares.assert_called_with(role)
    assert found == env.find_equity_shares.return_value


def test_get_tax_rate(role_with_env):
    # Given
    role, env = role_with_env
    env.fiscal_authority.tax_rate = 0.2

    # When
    perceived = role.get_tax_rate()

    # Assert
    assert perceived == 0.2


def test_get_discount_rate(role_with_env):
    # Given
    role, env = role_with_env
    env.monetary_authority.discount_rate = 0.05

    # When
    perceived = role.get_discount_rate()

    # Assert
    assert perceived == 0.05


# ---------------------------------------------------
# ACTIONS
# ----------------------------------------------------


def test_pay_dividends(role_with_env):
    # Given
    role, env = role_with_env
    founder = Mock()

    # When
    role.pay_dividends(founder, 50)

    # Then
    env.pay_dividends.assert_called_with(role, founder, 50)


def test_pay_taxes_uses_env_method(role_with_env):
    # Given
    role, env = role_with_env

    # When
    role.pay_taxes(50)

    # Then
    env.pay_taxes.assert_called_with(role, 50)


def test_update_equity_share_uses_env_method(role_with_env):
    # Given
    role, env = role_with_env
    founder = Mock()

    # When
    role.update_equity_share(founder, -50)

    # Then
    env.update_equity_share.assert_called_with(role, founder, -50)


def test_transfer_residual_cash_uses_env_method(role_with_env):
    # Given
    role, env = role_with_env
    founder = Mock()

    # When
    role.transfer_residual_cash(founder, 50)

    # Then
    env.transfer_residual_cash.assert_called_with(role, founder, 50)
