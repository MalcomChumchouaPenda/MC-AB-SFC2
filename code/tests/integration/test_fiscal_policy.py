import pytest
from unittest.mock import Mock
from mc_ab_sfc.spaces import CountrySpace
from mc_ab_sfc.agents import GovernmentAgent, CentralBank, Household


@pytest.fixture
def model():
    # Given
    model = Mock()
    model.p.dmax = 0.05
    model.p.tax_min = 0.10
    model.p.tax_max = 0.50
    model.p.g_min = 0.05
    model.p.g_max = 0.20
    model.p.delta = 0.10
    model.random.uniform.return_value = 0.05
    return model


@pytest.fixture
def govt(model):
    # Given
    govt = GovernmentAgent(model)
    govt.prev_public_spending = 10
    govt.public_spending = 100
    govt.budget_deficit = 100
    govt.tax_rate = 0.20
    govt.gdp = 1000
    return govt


@pytest.fixture
def country(model):
    # Given
    country = CountrySpace(model)
    country.markets["goods"] = Mock(average_price=2, average_productivity=3)
    return country


def test_government_updates_fiscal_policy(govt, country):
    # Given
    country.add_government(govt)

    # When
    govt.update_fiscal_policy()

    # Then
    assert govt.desired_public_spending == pytest.approx(60)
    assert govt.public_spending == pytest.approx(95)
    assert govt.tax_rate == pytest.approx(0.21)
