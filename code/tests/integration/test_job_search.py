from unittest.mock import Mock
import pytest
from agentpy import AttrIter
from model.spaces.labor_market import LaborMarket
from model.agents.household import Household
from model.agents.firm import Firm


@pytest.fixture
def model(fake_model):
    # Given
    model = fake_model
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
    market.add_household(household)
    return household


@pytest.fixture
def employers(model, market, make_dlist):
    # Given
    employers = make_dlist()
    wages = [20, 15, 16]
    demands = [0.4, 0.8, 0.8]
    for wage, demand in zip(wages, demands):
        firm = Firm(model)
        market.add_firm(firm)
        employer = firm.roles["employer"]
        employer.labor_demand = demand
        employer.wage = wage
        employers.append(employer)
    return employers


def test_creates_link_with_firms_with_higher_wages(household, employers, market):
    # Given
    household.p.psi = 3
    household.reservation_wage = 10
    worker = household.roles["worker"]

    # When
    household.search_jobs()

    # Then
    assert len(market.graph.edges) == 2
    assert market.graph.has_edge(worker, employers[0])
    assert market.graph.has_edge(worker, employers[2])


@pytest.mark.usefixtures("employers")
def test_created_limited_number_of_links(household, market):
    # Given
    household.p.psi = 1
    household.reservation_wage = 10

    # When
    household.search_jobs()

    # Then
    assert len(market.graph.edges) == 1


@pytest.mark.usefixtures("employers")
def test_increases_labor_sold_by_household(household, market):
    # Given
    household.p.psi = 3
    household.reservation_wage = 10
    worker = household.roles["worker"]
    links = lambda: market.links(worker, "employer")

    # When
    household.search_jobs()

    # Then
    assert sum([link["quantity"] for link in links()]) == pytest.approx(1.0)
