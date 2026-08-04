import pytest
from agentpy import Model
from dataclasses import dataclass
from mcabsfc.agents import HouseholdAgent
from mcabsfc.roles import WorkerRole
from mcabsfc.envs import LaborMarket


@dataclass(frozen=True)
class FakeEmployerRole:
    label: str
    wage: float
    demand: float


@pytest.fixture
def model():
    return Model()


@pytest.fixture
def market(model):
    return LaborMarket(model)


@pytest.fixture
def household(model):
    household = HouseholdAgent(model)
    household.reservation_wage = 10
    household.search_size = 2
    return household


def test_household_finds_jobs_on_labor_market(monkeypatch, household, market):
    # Given
    monkeypatch.setattr("mcabsfc.envs.EmployerRole", FakeEmployerRole)
    employer1 = FakeEmployerRole("F1", wage=20, demand=0.4)
    employer2 = FakeEmployerRole("F2", wage=15, demand=0.8)
    employer3 = FakeEmployerRole("F3", wage=16, demand=0.8)
    market.graph.add_nodes_from([employer1, employer2, employer3])
    market.add_worker(household)

    # When
    household.search_jobs()

    # Then
    edges = list(market.graph.edges)
    assert len(edges) == 2
    for source, target in edges:
        assert source is household.roles["worker"]
        assert isinstance(source, WorkerRole)
        assert isinstance(target, FakeEmployerRole)


def test_household_sells_total_labor_supply(monkeypatch, household, market):
    # Given
    monkeypatch.setattr("mcabsfc.envs.EmployerRole", FakeEmployerRole)
    employer1 = FakeEmployerRole("F1", wage=20, demand=0.4)
    employer2 = FakeEmployerRole("F2", wage=15, demand=0.8)
    market.graph.add_nodes_from([employer1, employer2])
    market.add_worker(household)

    # When
    household.search_jobs()

    # Then
    labor_sold = [attrs["quantity"] for u, v, attrs in market.graph.edges(data=True)]
    assert labor_sold[0] == pytest.approx(0.4)
    assert labor_sold[1] == pytest.approx(0.6)
    assert sum(labor_sold) == pytest.approx(1.0)
