import pytest
from unittest.mock import Mock
from mc_ab_sfc.agents import HouseholdAgent, FirmAgent
from mc_ab_sfc.spaces import LaborMarket


@pytest.fixture
def model():
    # Given
    model = Mock()
    model.p.psi = 2
    return model


@pytest.fixture
def market(model):
    # Given
    market = LaborMarket(model)
    return market


@pytest.fixture
def household(model):
    # Given
    household = HouseholdAgent(model)
    household.reservation_wage = 10
    return household


@pytest.fixture
def employers(model, market):
    # Given
    employers = []
    wages = [20, 15, 16]
    demands = [0.4, 0.8, 0.8]
    for wage, demand in zip(wages, demands):
        firm = FirmAgent(model)
        firm.wage_offer = wage
        employer = market.add_employer(firm)
        employer.labor_demand = demand
        employers.append(employer)
    return employers


def test_household_search_jobs_on_labor_market(household, employers, market):
    # Given
    market.add_worker(household)
    random = market.model.random
    random.sample = Mock(side_effect=lambda pop, k: pop[:k])

    # When
    household.search_jobs()

    # Then
    edges = list(market.graph.edges)
    assert len(edges) == 2
    for source, target in edges:
        assert target in employers
        assert source is household.roles["worker"]


def test_household_sells_total_labor_supply(household, employers, market):
    # Given
    market.add_worker(household)
    random = market.model.random
    random.sample = Mock(side_effect=lambda pop, k: pop[:k])

    # When
    household.search_jobs()

    # Then
    edges = market.graph.edges(data=True)
    labor_sold = [data["quantity"] for u, v, data in edges]
    assert sum(labor_sold) == pytest.approx(1.0)
    assert len(labor_sold) < len(employers)
