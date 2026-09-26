import pytest
from unittest.mock import Mock
from model.spaces.labor_market import LaborMarket

# ---------------------------------------------------
# ARCHITECTURE
# ----------------------------------------------------


def test_inherits_from_eco_space():
    # Given
    from model.base import EcoSpace

    # When
    is_derived = issubclass(LaborMarket, EcoSpace)

    # Then
    assert is_derived


@pytest.fixture
def market():
    # Given
    model = Mock()
    return LaborMarket(model)


def test_has_average_wage_prop(market):
    # Assert
    assert market.average_wage == 0


def test_has_unemployment_prop(market):
    # Assert
    assert market.unemployment == 0.0


# ---------------------------------------------------
# ROLES MANAGEMENT
# ----------------------------------------------------


FakeWorker = Mock()
FakeEmployer = Mock()


@pytest.fixture
def market_without_roles(monkeypatch, market):
    # Given
    monkeypatch.setattr("model.spaces.labor_market.Employer", FakeEmployer)
    monkeypatch.setattr("model.spaces.labor_market.Worker", FakeWorker)
    market.add_role = Mock()
    market.workers = []
    return market


def test_add_worker_add_appropriate_role(market_without_roles):
    # Given
    agent = Mock()
    market = market_without_roles

    # When
    role = market.add_worker(agent)

    # Then
    market.add_role.assert_called_with(FakeWorker, agent, "worker")
    assert role == market.add_role.return_value


def test_add_employer_add_appropriate_role(market_without_roles):
    # Given
    agent = Mock()
    market = market_without_roles

    # When
    role = market.add_employer(agent)

    # Then
    market.add_role.assert_called_with(FakeEmployer, agent, "employer")
    assert role == market.add_role.return_value


# ---------------------------------------------------
# LABOR MATCHING
# ----------------------------------------------------


def test_hire_worker_add_edge(market):
    # Given
    employer = Mock(wage=20, labor_demand=10)
    worker = Mock(labor_supply=1.0)
    graph = market.graph
    graph.add_nodes_from([employer, worker])

    # When
    market.hire_worker(worker, employer, 0.9)

    # Then
    assert len(graph.edges) == 1
    assert graph.has_edge(worker, employer)
    assert graph[worker][employer]["wage"] == 20
    assert graph[worker][employer]["quantity"] == 0.9


def test_hire_worker_reduces_labor_demand(market):
    # Given
    worker = Mock(labor_supply=1.0)
    employer = Mock(wage=20, labor_demand=10)
    market.graph.add_nodes_from([employer, worker])

    # When
    market.hire_worker(worker, employer, 0.9)

    # Then
    assert employer.labor_demand == pytest.approx(9.1)


def test_hire_worker_reduces_labor_supply(market):
    # Given
    worker = Mock(labor_supply=1.0)
    employer = Mock(wage=20, labor_demand=10)
    market.graph.add_nodes_from([employer, worker])

    # When
    market.hire_worker(worker, employer, 0.9)

    # Then
    assert worker.labor_supply == pytest.approx(0.1)


# ---------------------------------------------------
# WAGES PAYMENT
# ----------------------------------------------------


@pytest.fixture
def market_with_participants(market):
    # Given
    employer, worker = Mock(), Mock()
    market.graph.add_nodes_from([employer, worker])
    return market, employer, worker


# ---------------------------------------------------
# EVOLUTION
# ----------------------------------------------------


@pytest.fixture
def market_before_update(market, make_dlist):
    # Given
    market.average_wage = 0
    market.unemployment = 0
    market.roles = {
        "employer": make_dlist(),
        "worker": make_dlist(),
    }
    return market


def test_update_state_updates_average_wage(market_before_update):
    # Given
    market = market_before_update
    roles = market.roles["employer"]
    roles.extend([Mock(wage=5) for _ in range(5)])

    # When
    market.update_state()

    # Then
    assert market.average_wage == pytest.approx(5.0)


def test_update_state_updates_unemployment_rate(market_before_update):
    # Given
    market = market_before_update
    roles = market.roles["worker"]
    roles.extend([Mock(labor_supply=1.0) for _ in range(5)])
    roles.extend([Mock(labor_supply=0.5) for _ in range(5)])

    # When
    market.update_state()

    # Then
    assert market.unemployment == pytest.approx(0.5)
