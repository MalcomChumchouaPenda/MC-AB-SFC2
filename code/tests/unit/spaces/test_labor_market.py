import pytest
import agentpy as ap
from unittest.mock import Mock
from networkx import DiGraph
from dataclasses import dataclass
from mcabsfc.spaces import LaborMarket

# ---------------------------------------------------
# ARCHITECTURAL TESTS
# ----------------------------------------------------


def test_is_ecospace():
    # Given
    from mcabsfc.base import EcoSpace

    # Assert
    assert issubclass(LaborMarket, EcoSpace)


def test_has_directed_graph():
    # Given
    model = Mock()
    market = LaborMarket(model)

    # Assert
    assert isinstance(market.graph, DiGraph)


# ---------------------------------------------------
# BEHAVIORAL TESTS
# ----------------------------------------------------


@dataclass(frozen=True)
class FakeWorkerRole:
    owner: object = None
    space: object = None
    label: int = 1


@dataclass(frozen=True)
class FakeEmployerRole:
    owner: object = None
    space: object = None
    label: int = 2


@pytest.fixture
def market(monkeypatch):
    # Given a market and fake role class
    model = Mock()
    market = LaborMarket(model)
    monkeypatch.setattr("mcabsfc.spaces.WorkerRole", FakeWorkerRole)
    monkeypatch.setattr("mcabsfc.spaces.EmployerRole", FakeEmployerRole)
    return market


def test_add_worker_creates_and_registers_worker_role(market):
    # Given
    household = Mock(id=1, roles={})

    # When
    worker = market.add_worker(household)

    # Then
    assert isinstance(worker, FakeWorkerRole)
    assert worker.owner is household
    assert worker.space is market
    assert worker in market.nodes
    assert worker is household.roles["worker"]


def test_add_employer_creates_and_registers_employer_role(market):
    # Given
    firm = Mock(id=1, roles={})

    # When
    employer = market.add_employer(firm)

    # Then
    assert isinstance(employer, FakeEmployerRole)
    assert employer.owner is firm
    assert employer.space is market
    assert employer in market.nodes
    assert employer is firm.roles["employer"]


def test_search_employers_returns_psi_employers(market):
    # Given
    employers = [FakeEmployerRole(label=i) for i in range(5)]
    market.model.random.sample.return_value = employers[:3]
    market.graph.add_nodes_from(employers)

    # When
    sample = market.search_employers(psi=3)

    # Then
    market.model.random.sample.sample(employers, k=3)
    assert sample == employers[:3]


def test_get_labor_sold_by_worker(market):
    # Given
    worker = Mock(label=1)
    employer1 = Mock(label=2)
    employer2 = Mock(label=3)
    market.graph.add_nodes_from([worker, employer1, employer2])
    market.graph.add_edge(worker, employer1, quantity=0.4, wage=10)

    # When
    labor_sold = market.get_labor_sold(worker)

    # Then
    assert labor_sold == 0.4


def test_create_job_by_adding_graph_edge(market):
    # Given
    worker = Mock(label=1)
    employer = Mock(label=2, wage=20)
    market.graph.add_nodes_from([employer, worker])

    # When
    market.create_job(worker, employer, 0.9)

    # Then
    edges = list(market.graph.edges(data=True))
    source, target, data = edges[0]
    assert len(edges) == 1
    assert source is worker
    assert target is employer
    assert data["wage"] == 20
    assert data["quantity"] == 0.9
