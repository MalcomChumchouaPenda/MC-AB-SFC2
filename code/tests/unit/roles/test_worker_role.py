import pytest
import agentpy as ap
from unittest.mock import Mock
from mcabsfc.roles import WorkerRole, Role

# ---------------------------------------------------
# ARCHITECTURAL TESTS
# ----------------------------------------------------


def test_is_role():
    # Given
    market = Mock()
    owner = Mock(id=1)

    # When
    worker = WorkerRole(owner, market)

    # Then
    assert isinstance(worker, Role)


def test_has_market():
    # Given
    market = Mock()
    owner = Mock(id=1)

    # When
    worker = WorkerRole(owner, market)

    # Then
    assert worker.market == market


# ---------------------------------------------------
# BEHAVIORAL TESTS
# ----------------------------------------------------


@pytest.fixture
def market():
    return Mock()


@pytest.fixture
def owner():
    return Mock(id=1)


@pytest.fixture
def worker(owner, market):
    return WorkerRole(owner, market)


def test_find_employers_within_labor_market(worker, market):
    # Given
    employer = Mock(wage=20, demand=1.0)
    market.find_employers.return_value = [employer]

    # When
    found = worker.find_employers(3)

    # Then
    market.find_employers.assert_called_once_with(3)
    assert found == [employer]


def test_accept_job_by_creating_jobs_in_labor_market(worker, market):
    # Given
    quantity = 0.5
    employer = Mock()

    # When
    worker.accept_job(employer, quantity)

    # Then
    market.create_job.assert_called_with(worker, employer, quantity)


def test_returns_labor_sold_in_labor_market(worker, market):
    # Given
    market.labor_sold.return_value = 0.5

    # When
    labor_sold = worker.labor_sold

    # Then
    market.labor_sold.assert_called_with(worker)
    assert labor_sold == 0.5


def test_gets_unemployment_rate_from_market(worker, market):
    # Given
    market.unemployment_rate = 0.15

    # When
    unemployment = worker.unemployment_rate

    # Then
    assert unemployment == 0.15
