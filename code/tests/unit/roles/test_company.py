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
def company_before_setup():
    # Given
    model = Mock()
    role = Company(model)
    return role


def test_has_sector(company_before_setup):
    # Given
    company = company_before_setup

    # When
    company.setup()

    # Then
    assert company.sector == ""


def test_has_net_worth(company_before_setup):
    # Given
    company = company_before_setup

    # When
    company.setup()

    # Then
    assert company.net_worth == 0


def test_has_defaulted(company_before_setup):
    # Given
    company = company_before_setup

    # When
    company.setup()

    # Then
    assert company.defaulted is False


# ---------------------------------------------------
#  PERCEPTIONS
# ----------------------------------------------------


@pytest.fixture
def company_with_env(company_before_setup):
    # Given
    env = Mock()
    company = company_before_setup
    company.env = env
    return company, env


def test_get_average_wage(company_with_env):
    # Given
    company, env = company_with_env
    env.average_wage = 15.0

    # When
    perceived = company.get_average_wage()

    # Assert
    assert perceived == 15.0


def test_get_equity_shares_from_env(company_with_env):
    # Given
    company, env = company_with_env

    # When
    found = company.get_equity_shares()

    # Assert
    env.find_equity_shares.assert_called_with(company)
    assert found == env.find_equity_shares.return_value


def test_get_tax_rate(company_with_env):
    # Given
    company, env = company_with_env
    env.fiscal_authority.tax_rate = 0.2

    # When
    perceived = company.get_tax_rate()

    # Assert
    assert perceived == 0.2


def test_get_discount_rate(company_with_env):
    # Given
    company, env = company_with_env
    env.monetary_authority.discount_rate = 0.05

    # When
    perceived = company.get_discount_rate()

    # Assert
    assert perceived == 0.05


# ---------------------------------------------------
# ACTIONS
# ----------------------------------------------------


def test_pay_dividends(company_with_env):
    # Given
    company, env = company_with_env
    founder = Mock()

    # When
    company.pay_dividends(founder, 50)

    # Then
    env.pay_dividends.assert_called_with(company, founder, 50)


def test_pay_taxes_uses_env_method(company_with_env):
    # Given
    company, env = company_with_env

    # When
    company.pay_taxes(50)

    # Then
    env.pay_taxes.assert_called_with(company, 50)


def test_update_equity_share_uses_env_method(company_with_env):
    # Given
    company, env = company_with_env
    founder = Mock()

    # When
    company.update_equity_share(founder, -50)

    # Then
    env.update_equity_share.assert_called_with(company, founder, -50)


def test_transfer_residual_cash_uses_env_method(company_with_env):
    # Given
    company, env = company_with_env
    founder = Mock()

    # When
    company.transfer_residual_cash(founder, 50)

    # Then
    env.transfer_residual_cash.assert_called_with(company, founder, 50)
