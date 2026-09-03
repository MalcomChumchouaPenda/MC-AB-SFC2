import pytest
from unittest.mock import Mock
from agentpy import AgentDList
from model.spaces.labor_market import LaborMarket

# ---------------------------------------------------
# ARCHITECTURE TESTS
# ----------------------------------------------------


def test_is_eco_space():
    # Given
    from model.base import EcoSpace

    # Assert
    assert issubclass(LaborMarket, EcoSpace)


@pytest.fixture
def market_without_setup():
    # Given
    model = Mock()
    market = LaborMarket(model)
    return market


def test_has_average_wage_prop(market_without_setup):
    # Given
    market = market_without_setup

    # When
    market.setup()

    # Then
    assert market.average_wage == 0


def test_has_unemployment_prop(market_without_setup):
    # Given
    market = market_without_setup

    # When
    market.setup()

    # Then
    assert market.unemployment == 0.0


# ---------------------------------------------------
# ROLES SET/REF TESTS
# ----------------------------------------------------


def test_has_workers_list(market_without_setup):
    # Given
    market = market_without_setup

    # When
    market.setup()

    # Then
    assert isinstance(market.workers, AgentDList)


def test_has_employers_list(market_without_setup):
    # Given
    market = market_without_setup

    # When
    market.setup()

    # Then
    assert isinstance(market.employers, AgentDList)


# ---------------------------------------------------
# ROLES MANAGEMENT TESTS
# ----------------------------------------------------


class FakeWorker(Mock):
    pass


@pytest.fixture
def market_without_workers(monkeypatch, market_without_setup):
    # Given
    monkeypatch.setattr("model.spaces.labor_market.Worker", FakeWorker)
    market = market_without_setup
    market.add_role = Mock()
    market.workers = []
    return market


def test_add_worker_add_appropriate_role(market_without_workers):
    # Given
    agent = Mock()
    market = market_without_workers

    # When
    role = market.add_worker(agent)

    # Then
    market.add_role.assert_called_with(FakeWorker, agent, "worker")
    assert role == market.add_role.return_value


def test_add_worker_registers_worker(market_without_workers):
    # Given
    agent = Mock()
    market = market_without_workers

    # When
    role = market.add_worker(agent)

    # Then
    assert market.workers == [role]



class FakeEmployer(Mock):
    pass


@pytest.fixture
def market_without_employers(monkeypatch, market_without_setup):
    # Given
    monkeypatch.setattr("model.spaces.labor_market.Employer", FakeEmployer)
    market = market_without_setup
    market.add_role = Mock()
    market.employers = []
    return market


def test_add_employer_add_appropriate_role(market_without_employers):
    # Given
    agent = Mock()
    market = market_without_employers

    # When
    role = market.add_employer(agent)

    # Then
    market.add_role.assert_called_with(FakeEmployer, agent, "employer")
    assert role == market.add_role.return_value


def test_add_employer_registers_employer(market_without_employers):
    # Given
    agent = Mock()
    market = market_without_employers

    # When
    role = market.add_employer(agent)

    # Then
    assert market.employers == [role]


@pytest.fixture
def market_with_employer(market_without_setup):
    # Given
    market = market_without_setup
    employer = Mock(wage=20, labor_demand=10)
    return market, employer


def test_hire_worker_add_edge(market_with_employer):
    # Given
    market, employer = market_with_employer
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


def test_hire_worker_reduces_labor_demand(market_with_employer):
    # Given
    worker = Mock(labor_supply=1.0)
    market, employer = market_with_employer
    market.graph.add_nodes_from([employer, worker])

    # When
    market.hire_worker(worker, employer, 0.9)

    # Then
    assert employer.labor_demand == pytest.approx(9.1)


def test_hire_worker_reduces_labor_supply(market_with_employer):
    # Given
    worker = Mock(labor_supply=1.0)
    market, employer = market_with_employer
    market.graph.add_nodes_from([employer, worker])

    # When
    market.hire_worker(worker, employer, 0.9)

    # Then
    assert worker.labor_supply == pytest.approx(0.1)


# ---------------------------------------------------
# EVOLUTION TESTS
# ----------------------------------------------------


@pytest.fixture
def market_before_update(market_without_setup, make_dlist):
    # Given
    market = market_without_setup
    market.average_wage = 0
    market.unemployment = 0
    market.employers = make_dlist()
    market.workers = make_dlist()
    return market


def test_update_state_updates_average_wage(market_before_update):
    # Given
    market = market_before_update
    market.employers.extend([Mock(wage=5) for _ in range(5)])

    # When
    market.update_state()

    # Then
    assert market.average_wage == pytest.approx(5.0)
    

def test_update_state_updates_unemployment_rate(market_before_update):
    # Given
    market = market_before_update
    market.workers.extend([Mock(labor_supply=1.0) for _ in range(5)])
    market.workers.extend([Mock(labor_supply=0.5) for _ in range(5)])

    # When
    market.update_state()

    # Then
    assert market.unemployment == pytest.approx(0.5)

