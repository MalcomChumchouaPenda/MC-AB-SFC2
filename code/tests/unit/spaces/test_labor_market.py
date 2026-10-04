import pytest
from unittest.mock import Mock
from model.spaces.labor_market import LaborMarket

# ---------------------------------------------------
# ARCHITECTURE
# ----------------------------------------------------


def test_inherits_from_eco_space():
    # Given
    from model.extensions import EcoSpace

    # When
    is_derived = issubclass(LaborMarket, EcoSpace)

    # Then
    assert is_derived


def test_initializes_average_wage(fake_model):
    # Given
    model = fake_model

    # When
    market = LaborMarket(model)

    # Then
    assert market.average_wage == 0


def test_initializes_unemployment(fake_model):
    # Given
    model = fake_model

    # When
    market = LaborMarket(model)

    # Then
    assert market.unemployment == 0.0


# ---------------------------------------------------
# ROLES MANAGEMENT
# ----------------------------------------------------


FakeWorker = Mock()
FakeEmployer = Mock()


@pytest.fixture
def market_without_roles(monkeypatch, fake_model):
    # Given
    monkeypatch.setattr("model.spaces.labor_market.Employer", FakeEmployer)
    monkeypatch.setattr("model.spaces.labor_market.Worker", FakeWorker)
    market = LaborMarket(fake_model)
    market.add_role = Mock()
    return market


def test_add_household_add_worker_role(market_without_roles):
    # Given
    household = Mock()
    market = market_without_roles

    # When
    market.add_household(household)

    # Then
    market.add_role.assert_called_with(FakeWorker, household, "worker")


def test_add_firm_add_employer_role(market_without_roles):
    # Given
    firm = Mock()
    market = market_without_roles

    # When
    market.add_firm(firm)

    # Then
    market.add_role.assert_called_with(FakeEmployer, firm, "employer")


# ---------------------------------------------------
# LABOR MATCHING
# ----------------------------------------------------


@pytest.fixture
def market_with_participants(market_without_roles):
    # Given
    worker = Mock()
    employer = Mock()
    market = market_without_roles
    market.graph.add_nodes_from([employer, worker])
    return market, employer, worker


def test_hire_worker_add_edge(market_with_participants):
    # Given
    market, employer, worker = market_with_participants
    employer.labor_demand = 10
    worker.labor_supply = 1.0
    graph = market.graph

    # When
    market.hire_worker(worker, employer, 0.9)

    # Then
    assert graph.has_edge(worker, employer)
    assert graph[worker][employer]["wages"] == 0.0
    assert graph[worker][employer]["quantity"] == 0.9


def test_hire_worker_reduces_labor_demand(market_with_participants):
    # Given
    market, employer, worker = market_with_participants
    employer.labor_demand = 10
    worker.labor_supply = 1.0

    # When
    market.hire_worker(worker, employer, 0.9)

    # Then
    assert employer.labor_demand == pytest.approx(9.1)


def test_hire_worker_reduces_labor_supply(market_with_participants):
    # Given
    market, employer, worker = market_with_participants
    employer.labor_demand = 10
    worker.labor_supply = 1.0

    # When
    market.hire_worker(worker, employer, 0.9)

    # Then
    assert worker.labor_supply == pytest.approx(0.1)


# ---------------------------------------------------
# WAGES PAYMENT
# ----------------------------------------------------


@pytest.fixture
def market_with_jobs(market_without_roles):
    # Given
    worker = Mock()
    employer = Mock()
    market = market_without_roles
    market.transfer_stock = Mock()
    market.make_transaction = Mock()
    market.graph.add_edge(employer, worker, wages=0.0)
    return market, employer, worker


def test_pay_wages_update_edge(market_with_jobs):
    # Given
    market, employer, worker = market_with_jobs
    graph = market.graph

    # When
    market.pay_wages(employer, worker, 3.0)

    # Then
    assert graph[worker][employer]["wages"] == 3.0


def test_pay_wages_updates_accounts(market_with_jobs):
    # Given
    market, employer, worker = market_with_jobs

    # When
    market.pay_wages(employer, worker, 3.0)

    # Then
    market.transfer_stock.assert_any_call("cash", employer.id, worker.id, 3.0)
    market.make_transaction.assert_any_call("wages", employer.id, worker.id, 3.0)


# ---------------------------------------------------
# EVOLUTION
# ----------------------------------------------------


@pytest.fixture
def market_before_update(market_without_roles, make_dlist):
    # Given
    market = market_without_roles
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
