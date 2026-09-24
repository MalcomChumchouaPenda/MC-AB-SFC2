import pytest
from unittest.mock import Mock, MagicMock
from agentpy import AgentDList
from model.base import EcoSpace
from model.spaces.labor_market import LaborMarket

# ---------------------------------------------------
# ARCHITECTURE TESTS
# ----------------------------------------------------


def test_is_eco_space():
    # Assert
    assert issubclass(LaborMarket, EcoSpace)


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
# ROLES ACCESS
# ----------------------------------------------------


def test_has_workers_list(market):
    # Assert
    assert isinstance(market.workers, AgentDList)


def test_has_employers_list(market):
    # Assert
    assert isinstance(market.employers, AgentDList)


# ---------------------------------------------------
# ROLES MANAGEMENT
# ----------------------------------------------------


FakeWorker = Mock()
FakeEmployer = Mock()


@pytest.fixture
def market_without_workers(monkeypatch, market):
    # Given
    monkeypatch.setattr("model.spaces.labor_market.Worker", FakeWorker)
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



@pytest.fixture
def market_without_employers(monkeypatch, market):
    # Given
    monkeypatch.setattr("model.spaces.labor_market.Employer", FakeEmployer)
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


# ---------------------------------------------------
# LABOR MATCHING
# ----------------------------------------------------


@pytest.fixture
def market_with_employers(market):
    # Given
    employers = MagicMock()
    employers.__len__.return_value = 1
    employers.random.return_value = []
    market.employers = employers
    return market, employers


def test_find_employers_get_random_founders(market_with_employers):
    # Given
    expected = [Mock() for _ in range(10)]
    market, employers = market_with_employers
    employers.random.return_value = expected

    # When
    found = market.find_employers(5)

    # Then
    assert found == expected


@pytest.mark.parametrize("psi, expected", [(5, 5), (15, 10)])
def test_find_employers_with_psi_params(market_with_employers, psi, expected):
    # Given
    market, employers = market_with_employers
    employers.__len__.return_value = 10

    # When
    market.find_employers(psi)

    # Then
    employers.random.assert_called_with(expected)



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


def test_find_jobs(market_with_participants):
    # Given
    other = Mock()
    market, employer, worker = market_with_participants
    market.graph.add_edge(worker, employer, quantity=0.4, wage=10)
    market.graph.add_edge(worker, other, quantity=0.6, wage=10)

    # When
    jobs = market.find_jobs(employer)

    # Then
    assert jobs == [{"worker": worker, "quantity": 0.4, "wage": 10}]


# ---------------------------------------------------
# EVOLUTION
# ----------------------------------------------------


@pytest.fixture
def market_before_update(market, make_dlist):
    # Given
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
