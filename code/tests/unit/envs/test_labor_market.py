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
    # Given
    model = ap.Model()

    # When
    market = LaborMarket(model)

    # Then
    assert isinstance(market, ap.Network)


def test_has_directed_graph():
    # Given
    model = ap.Model()

    # When
    market = LaborMarket(model)

    # Then
    assert isinstance(market.graph, DiGraph)


# ---------------------------------------------------
# BEHAVIORAL TESTS
# ----------------------------------------------------


@dataclass(frozen=True)
class FakeWorkerRole:
    owner: object = None
    market: object = None
    label: int = 1


@dataclass(frozen=True)
class FakeEmployerRole:
    owner: object = None
    market: object = None
    label: int = 2


@pytest.fixture
def market(monkeypatch):
    model = ap.Model()
    market = LaborMarket(model)
    monkeypatch.setattr("mcabsfc.envs.WorkerRole", FakeWorkerRole)
    monkeypatch.setattr("mcabsfc.envs.EmployerRole", FakeEmployerRole)
    return market


def test_find_employers_returns_exact_number_of_employers(market):
    # Given
    market.graph.add_nodes_from(
        [
            FakeEmployerRole(label="F1"),
            FakeEmployerRole(label="F2"),
            FakeEmployerRole(label="F3"),
            FakeEmployerRole(label="F4"),
            FakeEmployerRole(label="F5"),
        ]
    )

    # When
    sample = market.find_employers(3)

    # Then
    assert len(sample) == 3


def test_find_employers_returns_non_redundant_employers(market):
    # Given
    market.graph.add_nodes_from(
        [
            FakeEmployerRole(label="F1"),
            FakeEmployerRole(label="F2"),
            FakeEmployerRole(label="F3"),
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


def test_add_worker_creates_and_registers_worker_role(market):
    # Given
    household = Mock(id=1, roles={})

    # When
    worker = market.add_worker(household)

    # Then
    assert isinstance(worker, FakeWorkerRole)
    assert worker.owner is household
    assert worker.market is market
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
    assert employer.market is market
    assert employer in market.nodes
    assert employer is firm.roles["employer"]
