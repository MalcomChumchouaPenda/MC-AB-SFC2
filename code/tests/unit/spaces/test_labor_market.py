import pytest
from unittest.mock import Mock
from mc_ab_sfc.spaces import LaborMarket

# ---------------------------------------------------
# ARCHITECTURAL TESTS
# ----------------------------------------------------


def test_is_ecospace():
    # Given
    from mc_ab_sfc.base import EcoSpace

    # Assert
    assert issubclass(LaborMarket, EcoSpace)


# ---------------------------------------------------
# BEHAVIORAL TESTS
# ----------------------------------------------------


@pytest.fixture
def market():
    # Given a market and fake role class
    model = Mock()
    market = LaborMarket(model)
    return market


class FakeRole:
    pass


def test_add_worker_creates_worker_role(market, monkeypatch):
    # Given
    household = Mock()
    market.add_role = Mock()
    monkeypatch.setattr("mc_ab_sfc.spaces.WorkerRole", FakeRole)

    # When
    worker = market.add_worker(household)

    # Then
    market.add_role.assert_called_with(FakeRole, household, "worker")
    assert worker is market.add_role.return_value


def test_add_employer_creates_employer_role(market, monkeypatch):
    # Given
    firm = Mock()
    market.add_role = Mock()
    monkeypatch.setattr("mc_ab_sfc.spaces.EmployerRole", FakeRole)

    # When
    employer = market.add_employer(firm)

    # Then
    market.add_role.assert_called_with(FakeRole, firm, "employer")
    assert employer is market.add_role.return_value


def test_search_employers_returns_psi_employers(market, monkeypatch):
    # Given
    others = [Mock() for _ in range(3)]
    employers = [FakeRole() for _ in range(5)]
    market.graph.add_nodes_from(employers + others)
    monkeypatch.setattr("mc_ab_sfc.spaces.EmployerRole", FakeRole)

    random = market.model.random
    random.sample = Mock(side_effect=lambda pop, k: pop[:k])

    # When
    sample = market.search_employers(psi=3)

    # Then
    assert sample == employers[:3]


def test_get_labor_sold_by_worker(market):
    # Given
    worker = Mock()
    employer1, employer2 = Mock(), Mock()
    market.graph.add_nodes_from([worker, employer1, employer2])
    market.graph.add_edge(worker, employer1, quantity=0.4, wage=10)

    # When
    labor_sold = market.get_labor_sold(worker)

    # Then
    assert labor_sold == 0.4


def test_create_job_by_adding_graph_edge(market):
    # Given
    worker = Mock()
    employer = Mock(wage=20)
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
