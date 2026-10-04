import pytest
from unittest.mock import Mock
from model.roles.citizen import Citizen

# ---------------------------------------------------
# ARCHITECTURE
# ----------------------------------------------------


def test_inherits_from_eco_role():
    # Given
    from model.base import EcoRole

    # When
    is_derived = issubclass(Citizen, EcoRole)

    # Then
    assert is_derived


def test_initializes_residual_equity():
    # Given
    agent, env = Mock(), Mock()

    # When
    role = Citizen(agent, env)

    # Then
    assert role.resid_equity == 0


# ---------------------------------------------------
# PERCEPTION TESTS
# ----------------------------------------------------


@pytest.fixture
def role():
    # Given
    agent, env = Mock(), Mock()
    return Citizen(agent, env)


def test_get_prob_failure(role):
    # Given
    env = role.env
    env.prob_failure = 0.12

    # When
    perceived = role.get_prob_failure()

    # Then
    assert perceived == 0.12


def test_find_investors_with_residual_equity(role, make_dlist):
    # Given
    eligible = Mock(resid_equity=10)
    ineligible = Mock(resid_equity=0)
    citizens = make_dlist([eligible, ineligible])
    env = role.env
    env.find_all_roles = Mock(return_value=citizens)

    # When
    investors = role.find_investors()

    # Then
    env.find_all_roles.assert_called_with("citizen")
    assert list(investors) == [eligible]


def test_find_investors_excludes_initiator(role, make_dlist):
    # Given
    eligible = Mock(resid_equity=10)
    citizens = make_dlist([eligible, role])
    env = role.env
    env.find_all_roles = Mock(return_value=citizens)

    # When
    investors = role.find_investors()

    # Then
    assert list(investors) == [eligible]


def test_get_bank_number_ratio_from_env(role):
    # Given
    env = role.env
    env.calc_bank_number_ratio.return_value = 0.5

    # When
    ratio = role.get_bank_number_ratio()

    # Then
    assert ratio == 0.5


def test_get_bank_equity_ratio_from_env(role):
    # Given
    env = role.env
    env.calc_bank_equity_ratio.return_value = 0.6

    # When
    ratio = role.get_bank_equity_ratio()

    # Then
    assert ratio == 0.6


def test_get_sector_equity_range_from_env(role):
    # Given
    env = role.env
    env.calc_sector_equity_range.return_value = (100, 200)

    # When
    range_ = role.get_sector_equity_range("X")

    # Then
    assert range_ == (100, 200)


def test_get_tax_rate(role):
    # Given
    env = role.env
    env.tax_rate = 0.2

    # When
    perceived = role.get_tax_rate()

    # Then
    assert perceived == 0.2


# ---------------------------------------------------
# ACTION TESTS
# ----------------------------------------------------


def test_fund_company_uses_env_method(role):
    # Given
    company = Mock(id=2)
    env = role.env
    env.roles = {2: company}

    # When
    role.fund_company(2, 200)

    # Then
    env.fund_company.assert_called_with(company, role, 200)


def test_pay_taxes_uses_env_method(role):
    # Given
    env = role.env

    # When
    role.pay_taxes(100)

    # Then
    env.pay_taxes.assert_called_with(role, 100)
