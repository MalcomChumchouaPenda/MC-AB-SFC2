import pytest
from unittest.mock import Mock
from model.agents.private import Household, Firm
from model.spaces.real import LaborMarket


@pytest.fixture
def model():
    # Given
    model = Mock()
    model.p.psi = 2
    random = model.random
    random.sample = Mock(side_effect=lambda pop, k: pop[:k])
    return model


@pytest.fixture
def market(model):
    # Given
    market = LaborMarket(model)
    return market


@pytest.fixture
def household(model, market):
    # Given
    household = Household(model)
    market.add_worker(household)
    return household


@pytest.fixture
def employers(model, market):
    # Given
    employers = []
    wages = [20, 15, 16]
    demands = [0.4, 0.8, 0.8]
    for wage, demand in zip(wages, demands):
        firm = Firm(model)
        firm.wage_offer = wage
        employer = market.add_employer(firm)
        employer.labor_demand = demand
        employers.append(employer)
    return employers


def test_household_search_jobs_on_labor_market(household, employers, market):
    # Given
    graph = market.graph
    worker = household.roles["worker"]
    household.reservation_wage = 10

    # When
    household.search_jobs()

    # Then
    assert len(graph.edges) == 2
    for employer in employers[:2]:
        assert graph.has_edge(worker, employer)


def test_household_sells_total_labor_supply(household, employers, market):
    # Given
    household.reservation_wage = 10

    # When
    household.search_jobs()

    # Then
    edges = market.graph.edges(data=True)
    labor_sold = [data["quantity"] for u, v, data in edges]
    assert sum(labor_sold) == pytest.approx(1.0)
    assert len(labor_sold) < len(employers)
