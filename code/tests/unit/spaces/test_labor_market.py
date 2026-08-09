import pytest
from unittest.mock import Mock
from mc_ab_sfc.spaces import LaborMarket

# ---------------------------------------------------
# ARCHITECTURE TESTS
# ----------------------------------------------------


def test_is_eco_space():
    # Given
    from mc_ab_sfc.base import EcoSpace

    # Assert
    assert issubclass(LaborMarket, EcoSpace)


# ---------------------------------------------------
# BEHAVIORAL TESTS
# ----------------------------------------------------


@pytest.fixture
def market():
    # Given
    model = Mock()
    random = model.random
    random.sample = Mock(side_effect=lambda pop, k: pop[:k])
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


@pytest.fixture
def employer_with_demand():
    return Mock(wage_offer=20, labor_demand=10)


def test_create_job_add_edge(market, employer_with_demand):
    # Given
    employer = employer_with_demand
    worker = Mock()
    graph = market.graph
    graph.add_nodes_from([employer, worker])

    # When
    market.create_job(worker, employer, 0.9)

    # Then
    assert len(graph.edges) == 1
    assert graph.has_edge(worker, employer)
    assert graph[worker][employer]["wage"] == 20
    assert graph[worker][employer]["quantity"] == 0.9


def test_create_job_reduces_labor_demand(market, employer_with_demand):
    # Given
    worker = Mock()
    employer = employer_with_demand
    market.graph.add_nodes_from([employer, worker])

    # When
    market.create_job(worker, employer, 0.9)

    # Then
    assert employer.labor_demand == pytest.approx(9.1)
