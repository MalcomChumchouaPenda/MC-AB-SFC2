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
    assert govt.public_spending == 0


def test_has_default_choices(govt):
    # Assert
    assert govt.tax_rate == 0
    assert govt.desired_public_spending == 0


def test_has_default_indicators(govt):
    # Assert
    assert govt.gdp == 0
    assert govt.budget_deficit == 0
    assert govt.budget_surplus == 0


def test_pays_public_transfers(govt):
    # Given
    households = [Mock() for _ in range(3)]
    govt_role = Mock()
    govt_role.get_households.return_value = households
    govt.roles["government"] = govt_role
    govt.desired_public_spending = 300

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


def test_update_history(govt):
    # Given
    govt_role = Mock()
    govt_role.get_gdp.return_value = 120
    govt.roles["government"] = govt_role
    govt.gdp = 100

    # When
    govt.update_history()

    # Then
    assert govt.gdp == 120
