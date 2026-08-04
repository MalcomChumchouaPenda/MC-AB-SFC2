import pytest
import agentpy as ap
from unittest.mock import Mock
from networkx import DiGraph
from dataclasses import dataclass
from mcabsfc.envs import LaborMarket

# ---------------------------------------------------
# ARCHITECTURAL TESTS
# ----------------------------------------------------


def test_is_network():
    assert issubclass(LaborMarket, ap.Network)


def test_has_directed_graph():
    market = LaborMarket(ap.Model())
    assert isinstance(market.graph, DiGraph)


# ---------------------------------------------------
# BEHAVIORAL TESTS
# ----------------------------------------------------


@dataclass(frozen=True)
class FakeEmployerRole:
    label: str


@pytest.fixture
def market():
    model = ap.Model()
    market = LaborMarket(model)
    return market


def test_find_employers_returns_exact_number_of_employers(market, monkeypatch):
    # Given
    monkeypatch.setattr("mcabsfc.envs.EmployerRole", FakeEmployerRole)
    market.graph.add_nodes_from(
        [
            FakeEmployerRole("F1"),
            FakeEmployerRole("F2"),
            FakeEmployerRole("F3"),
            FakeEmployerRole("F4"),
            FakeEmployerRole("F5"),
        ]
    )

    # When
    sample = market.find_employers(3)

    # Then
    assert len(sample) == 3


def test_find_employers_returns_non_redundant_employers(market, monkeypatch):
    # Given
    monkeypatch.setattr("mcabsfc.envs.EmployerRole", FakeEmployerRole)
    market.graph.add_nodes_from(
        [
            FakeEmployerRole("F1"),
            FakeEmployerRole("F2"),
            FakeEmployerRole("F3"),
        ]
    )

    # When
    sample = market.find_employers(3)

    # Then
    labels = [employer.label for employer in sample]
    assert len(labels) == len(set(labels))


def test_create_job_by_adding_graph_edge(market):
    # Given
    worker = Mock(label=1)
    employer = Mock(label=2, wage=20)
    market.graph.add_nodes_from([employer, worker])

    # When
    market.create_job(worker, employer, 0.9)

    # Then
    edges = list(market.graph.edges(data=True))
    *nodes, attrs = edges[0]
    assert len(edges) == 1
    assert worker in nodes
    assert employer in nodes
    assert attrs["wage"] == 20
    assert attrs["quantity"] == 0.9


def test_compute_labor_sold_by_worker(market):
    # Given
    worker = Mock(label=1)
    employer1 = Mock(label=2)
    employer2 = Mock(label=3)
    market.graph.add_nodes_from([worker, employer1, employer2])
    market.graph.add_edge(worker, employer1, quantity=0.4, wage=10)

    # When
    labor_sold = market.labor_sold(worker)

    # Then
    assert labor_sold == 0.4


@dataclass(frozen=True)
class FakeWorkerRole:
    owner: object
    market: object


def test_add_worker_creates_and_registers_worker_role(market, monkeypatch):
    # Given
    monkeypatch.setattr("mcabsfc.envs.WorkerRole", FakeWorkerRole)
    household = Mock(id=1, roles={})

    # When
    worker = market.add_worker(household)

    # Then
    assert isinstance(worker, FakeWorkerRole)
    assert worker.owner is household
    assert worker.market is market
    assert worker in market.nodes
    assert worker is household.roles["worker"]
