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


@pytest.fixture
def market(fake_model):
    # Given
    return LaborMarket(fake_model)


def test_initializes_average_wage(market):
    # When
    default_value = market.average_wage

    # Then
    assert default_value == 0


def test_initializes_unemployment(market):
    # When
    default_value = market.unemployment

    # Then
    assert default_value == 0


# ---------------------------------------------------
# ROLES MANAGEMENT
# ----------------------------------------------------


@pytest.fixture
def market_without_roles(market):
    # Given
    market.env = Mock(pos=1)
    market.add_role = Mock()
    return market


def test_add_household_add_domestic_worker(market_without_roles, monkeypatch):
    # Given
    role_cls = Mock(name="Worker")
    monkeypatch.setattr("model.spaces.labor_market.Worker", role_cls)
    household = Mock(country_pos=1)
    market = market_without_roles

    # When
    market.add_household(household)

    # Then
    market.add_role.assert_called_with(role_cls, household)


def test_add_household_does_nothing_for_foreigner(market_without_roles):
    # Given
    household = Mock(country_pos=2)
    market = market_without_roles

    # When
    market.add_household(household)

    # Then
    market.add_role.assert_not_called()


def test_add_firm_add_domestic_employer(market_without_roles, monkeypatch):
    # Given
    firm = Mock(country_pos=1)
    role_cls = Mock(name="Employer")
    monkeypatch.setattr("model.spaces.labor_market.Employer", role_cls)
    market = market_without_roles

    # When
    market.add_firm(firm)

    # Then
    market.add_role.assert_called_with(role_cls, firm)


def test_add_firm_does_nothing_for_foreigner(market_without_roles):
    # Given
    firm = Mock(country_pos=2)
    market = market_without_roles

    # When
    market.add_firm(firm)

    # Then
    market.add_role.assert_not_called()


# ---------------------------------------------------
# LABOR MATCHING
# ----------------------------------------------------


@pytest.fixture
def worker():
    # Given
    return Mock(labor_supply=1.0)


@pytest.fixture
def employer():
    # Given
    return Mock(labor_demand=10, labor=0.0)


def test_hire_worker_add_edge(market, employer, worker):
    # Given
    graph = market.graph

    # When
    market.hire_worker(worker, employer, 0.9)

    # Then
    assert graph.has_edge(worker, employer)
    assert graph[worker][employer]["wages"] == 0.0
    assert graph[worker][employer]["quantity"] == 0.9


def test_hire_worker_reduces_labor_demand(market, employer, worker):
    # When
    market.hire_worker(worker, employer, 0.9)

    # Then
    assert employer.labor_demand == pytest.approx(9.1)


def test_hire_worker_reduces_labor_supply(market, employer, worker):
    # When
    market.hire_worker(worker, employer, 0.9)

    # Then
    assert worker.labor_supply == pytest.approx(0.1)


def test_hire_worker_increases_labor(market, employer, worker):
    # When
    market.hire_worker(worker, employer, 0.9)

    # Then
    assert employer.labor == pytest.approx(0.9)


# ---------------------------------------------------
# WAGES PAYMENT
# ----------------------------------------------------


@pytest.fixture
def market_with_jobs(market, employer, worker):
    # Given
    market.env = Mock()
    market.transfer_stock = Mock()
    market.make_transaction = Mock()
    market.graph.add_edge(employer, worker, wages=0.0)
    return market


def test_pay_wages_update_edge(market_with_jobs, employer, worker):
    # Given
    market = market_with_jobs
    graph = market.graph

    # When
    market.pay_wages(employer, worker, 3.0)

    # Then
    assert graph[worker][employer]["wages"] == 3.0


def test_pay_wages_transfers_cash(market_with_jobs, employer, worker):
    # Given
    market = market_with_jobs

    # When
    market.pay_wages(employer, worker, 3.0)

    # Then
    market.transfer_stock.assert_any_call("cash", employer.id, worker.id, 3.0)


def test_pay_wages_updates_accounts(market_with_jobs, employer, worker):
    # Given
    market = market_with_jobs

    # When
    market.pay_wages(employer, worker, 3.0)

    # Then
    market.make_transaction.assert_any_call("wages", employer.id, worker.id, 3.0)


# ---------------------------------------------------
#  STATISTICS TESTS
# ----------------------------------------------------


@pytest.fixture
def employers(market, make_dlist):
    # Given
    employers = make_dlist()
    for _ in range(2):
        role = Mock(wage=5.0)
        role.name = "employer"
        market.roles[role.id] = role
        employers.append(role)
    return employers


def test_calc_wage_range_for_all_employers(market, employers):
    # Given
    employers[0].wage = 10.0
    employers[1].wage = 15.0

    # When
    range_ = market.calc_wage_range()

    # Then
    assert range_ == (10.0, 15.0)


def test_calc_wage_range_if_no_employers(market):
    # When
    range_ = market.calc_wage_range()

    # Then
    assert range_ is None


# ---------------------------------------------------
# EVOLUTION
# ----------------------------------------------------


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
def market_before_update(market, employers, workers):
    # Given
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
def market_with_defaults(market, employers):
    employers[0].defaulted = True
    employers[1].defaulted = False
    market.remove_role = Mock()
    return market


def test_clear_defaults_removes_defaulted_employers(market_with_defaults, employers):
    # Given
    market = market_with_defaults

    # When
    market.clear_defaults()

    # Then
    assert call(employers[0]) in market.remove_role.call_args_list
    assert call(employers[1]) not in market.remove_role.call_args_list
    assert market.remove_role.call_count == 1
