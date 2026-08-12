import pytest
from unittest.mock import Mock
from mc_ab_sfc.agents import GovernmentAgent

# ---------------------------------------------------
# ARCHITECTURE TESTS
# ----------------------------------------------------


def test_is_eco_agent():
    # Given
    from mc_ab_sfc.base import EcoAgent

    # Assert
    assert issubclass(GovernmentAgent, EcoAgent)


@pytest.fixture
def govt():
    # Given
    model = Mock()
    return GovernmentAgent(model)


def test_has_default_stocks(govt):
    # Assert
    assert govt.reserves == 0
    assert govt.bonds == 0


def test_has_default_flows(govt):
    # Assert
    assert govt.taxes == 0
    assert govt.profit == 0
    assert govt.public_transfers == 0


def test_has_default_choices(govt):
    # Assert
    assert govt.tax_rate == 0
    assert govt.public_spending == 0
    assert govt.desired_public_spending == 0


def test_has_default_indicators(govt):
    # Assert
    assert govt.gdp == 0
    assert govt.budget_deficit == 0
    assert govt.budget_surplus == 0
    assert govt.prev_public_spending == 0


def test_pays_public_transfers(govt):
    # Given
    households = [Mock() for _ in range(3)]
    govt_role = Mock()
    govt_role.get_households.return_value = households
    govt.roles["government"] = govt_role
    govt.public_spending = 300

    # When
    govt.pay_public_transfers()

    # Then
    action = govt_role.pay_public_transfers
    for household in households:
        action.assert_any_call(household, 100)


def test_calc_budget_balance(govt):
    # Given
    govt.taxes = 1000
    govt.public_spending = 700
    govt.bond_interest = 100

    # When
    balance = govt.calc_budget_balance()

    # Then
    assert balance == 200


def test_calc_and_records_budget_deficit(govt):
    # Given
    govt.taxes = 500
    govt.public_spending = 600
    govt.bond_interest = 100

    # When
    govt.calc_budget_balance()

    # Then
    assert govt.budget_deficit == 200
    assert govt.budget_surplus == 0


def test_calc_and_records_budget_surplus(govt):
    # Given
    govt.taxes = 1000
    govt.public_spending = 700
    govt.bond_interest = 100

    # When
    govt.calc_budget_balance()

    # Then
    assert govt.budget_surplus == 200
    assert govt.budget_deficit == 0


def test_calc_and_records_with_no_deficit_or_surplus(govt):
    # Given
    govt.taxes = 800
    govt.public_spending = 700
    govt.bond_interest = 100

    # When
    govt.calc_budget_balance()

    # Then
    assert govt.budget_deficit == 0
    assert govt.budget_surplus == 0


def test_calc_and_records_desired_public_spending(govt):
    # Given
    govt_role = Mock()
    govt_role.get_average_price.return_value = 2
    govt_role.get_average_productivity.return_value = 3
    govt.roles["government"] = govt_role
    govt.prev_public_spending = 10

    # When
    desired = govt.calc_desired_public_spending()

    # Then
    assert desired == 60
    assert govt.desired_public_spending == desired


@pytest.mark.parametrize("tax_rate, expected", [(0.38, 0.40), (0.58, 0.50)])
def test_tax_rate_is_bounded(govt, tax_rate, expected):
    # Given
    govt.tax_rate = tax_rate
    govt.p.tax_min = 0.40
    govt.p.tax_max = 0.50

    # When
    govt.apply_tax_rate_bounds()

    # Then
    assert govt.tax_rate == expected


@pytest.mark.parametrize("spending, expected", [(80, 100), (150, 120)])
def test_public_spending_is_bounded_by_gdp(govt, spending, expected):
    # Given
    govt.public_spending = spending
    govt.gdp = 1000
    govt.p.g_min = 0.10
    govt.p.g_max = 0.12

    # When
    govt.apply_public_spending_bounds()

    # Then
    assert govt.public_spending == expected


@pytest.fixture
def govt_for_policy():
    # Given
    model = Mock()
    model.p.delta = 0.10
    govt = GovernmentAgent(model)
    govt.tax_rate = 0.20
    govt.gdp = 1000
    govt.public_spending = 100
    govt.desired_public_spending = 0
    govt.apply_tax_rate_bounds = Mock()
    govt.apply_public_spending_bounds = Mock()
    govt.calc_desired_public_spending = Mock(return_value=0)
    govt.model.random.uniform.return_value = 0.05
    return govt


def test_update_fiscal_policy_with_random_variation(govt_for_policy):
    # Given
    govt = govt_for_policy
    govt.budget_deficit = 100
    govt.dmax = 0.05
    govt.desired_public_spending = 80
    random = govt.model.random

    # When
    govt.update_fiscal_policy()

    # Then
    random.uniform.assert_called_with(0, 0.10)


def test_update_fiscal_policy_with_multi_steps(govt_for_policy):
    # Given
    govt = govt_for_policy
    govt.budget_deficit = 100
    govt.dmax = 0.05
    govt.desired_public_spending = 80

    # When
    govt.update_fiscal_policy()

    # Then
    govt.calc_desired_public_spending.assert_called_with()
    govt.apply_public_spending_bounds.assert_called_with()
    govt.apply_tax_rate_bounds.assert_called_with()


def test_reduce_spending_and_increase_tax_when_deficit_high(govt_for_policy):
    # Given
    govt = govt_for_policy
    govt.dmax = 0.05
    govt.budget_deficit = 100
    govt.calc_desired_public_spending.return_value = 80

    # When
    govt.update_fiscal_policy()

    # Then
    assert govt.public_spending == pytest.approx(95)
    assert govt.tax_rate == pytest.approx(0.21)


def test_keep_spending_and_increase_tax_when_deficit_high(govt_for_policy):
    # Given
    govt = govt_for_policy
    govt.dmax = 0.05
    govt.budget_deficit = 100
    govt.calc_desired_public_spending.return_value = 120

    # When
    govt.update_fiscal_policy()

    # Then
    assert govt.public_spending == pytest.approx(100)
    assert govt.tax_rate == pytest.approx(0.21)


def test_reduce_spending_and_tax_when_deficit_low(govt_for_policy):
    # Given
    govt = govt_for_policy
    govt.dmax = 0.05
    govt.budget_deficit = 20
    govt.calc_desired_public_spending.return_value = 80

    # When
    govt.update_fiscal_policy()

    # Then
    assert govt.public_spending == pytest.approx(95)
    assert govt.tax_rate == pytest.approx(0.19)


def test_increase_spending_and_keep_tax_when_deficit_low(govt_for_policy):
    # Given
    govt = govt_for_policy
    govt.dmax = 0.05
    govt.budget_deficit = 20
    govt.calc_desired_public_spending.return_value = 120

    # When
    govt.update_fiscal_policy()

    # Then
    assert govt.public_spending == pytest.approx(105)
    assert govt.tax_rate == pytest.approx(0.20)


def test_update_history(govt):
    # Given
    govt_role = Mock()
    govt_role.get_gdp.return_value = 120
    govt.roles["government"] = govt_role
    govt.gdp = 100
    govt.public_spending = 200
    govt.prev_public_spending = 150

    # When
    govt.update_history()

    # Then
    assert govt.gdp == 120
    assert govt.prev_public_spending == 200
