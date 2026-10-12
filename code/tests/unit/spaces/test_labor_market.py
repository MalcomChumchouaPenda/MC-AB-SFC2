import pytest
from unittest.mock import Mock, call
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
    market.add_role.assert_called_with(FakeWorker, household)


def test_add_firm_add_employer_role(market_without_roles):
    # Given
    firm = Mock()
    market = market_without_roles

    # When
    market.add_firm(firm)

    # Then
    market.add_role.assert_called_with(FakeEmployer, firm)


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
    worker.labor_supply = 1.0
    employer.labor_demand = 10
    employer.labor = 0.0
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
    worker.labor_supply = 1.0
    employer.labor_demand = 10
    employer.labor = 0.0

    # When
    market.hire_worker(worker, employer, 0.9)

    # Then
    assert employer.labor_demand == pytest.approx(9.1)


def test_hire_worker_reduces_labor_supply(market_with_participants):
    # Given
    market, employer, worker = market_with_participants
    worker.labor_supply = 1.0
    employer.labor_demand = 10
    employer.labor = 0.0

    # When
    market.hire_worker(worker, employer, 0.9)

    # Then
    assert worker.labor_supply == pytest.approx(0.1)


def test_hire_worker_increases_labor(market_with_participants):
    # Given
    market, employer, worker = market_with_participants
    worker.labor_supply = 1.0
    employer.labor_demand = 10
    employer.labor = 0.0

    # When
    market.hire_worker(worker, employer, 0.9)

    # Then
    assert employer.labor == pytest.approx(0.9)


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
#  STATISTICS TESTS
# ----------------------------------------------------


def test_calc_wage_range_for_all_employers(market_without_roles, make_dlist):
    # Given
    employers = [Mock(id=i, wage=10.0) for i in range(4)]
    employers = make_dlist(employers)
    employers.name = "employer"
    employers[1].wage = 15.0
    market = market_without_roles
    market.roles = {role.id: role for role in employers}

    # When
    range_ = market.calc_wage_range()

    # Then
    assert range_ == (10.0, 15.0)


def test_calc_wage_range_if_no_employers(market_without_roles):
    # Given
    market = market_without_roles
    market.roles = {}

    # When
    range_ = market.calc_wage_range()

    # Then
    assert range_ is None


# ---------------------------------------------------
# EVOLUTION
# ----------------------------------------------------


@pytest.fixture
def employers(make_dlist):
    # Given
    roles = make_dlist()
    for _ in range(5):
        role = Mock(wage=5.0)
        role.name = "employer"
        roles.append(role)
    return roles


@pytest.fixture
def employed(make_dlist):
    # Given
    roles = make_dlist()
    for _ in range(5):
        role = Mock(labor_supply=0.5)
        role.name = "worker"
        roles.append(role)
    return roles


@pytest.fixture
def unemployed(make_dlist):
    # Given
    roles = make_dlist()
    for _ in range(5):
        role = Mock(labor_supply=1.0)
        role.name = "worker"
        roles.append(role)
    return roles


@pytest.fixture
def workers(employed, unemployed):
    # Given
    return employed + unemployed


@pytest.fixture
def market_before_update(market_without_roles, employers, workers):
    # Given
    market = market_without_roles
    market.roles = {role.id: role for role in employers + workers}
    market.average_wage = 0
    market.unemployment = 0
    return market


def test_update_state_updates_average_wage(market_before_update):
    # Given
    market = market_before_update

    # When
    market.update_state()

    # Then
    assert market.average_wage == pytest.approx(5.0)


def test_update_state_updates_unemployment_rate(market_before_update):
    # Given
    market = market_before_update

    # When
    market.update_state()

    # Then
    assert market.unemployment == pytest.approx(0.5)


@pytest.fixture
def market_with_defaults(market_without_roles):
    employers = [Mock(defaulted=val) for val in [True, False]]
    market = market_without_roles
    for role in employers:
        role.name = "employer"
        market.roles[role.agent.id] = role
    market.remove_role = Mock()
    return market, employers


def test_clear_defaults_removes_defaulted_employers(market_with_defaults):
    # Given
    market, employers = market_with_defaults

    # When
    market.clear_defaults()

    # Then
    assert call(employers[0]) in market.remove_role.call_args_list
    assert call(employers[1]) not in market.remove_role.call_args_list
    assert market.remove_role.call_count == 1
