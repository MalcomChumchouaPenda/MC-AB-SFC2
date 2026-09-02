import pytest
from unittest.mock import Mock
from model.spaces.labor_market import WorkerRole

# ---------------------------------------------------
# ARCHITECTURE TESTS
# ----------------------------------------------------


def test_is_eco_role():
    # Given
    from model.base import EcoRole

    # Assert
    assert issubclass(WorkerRole, EcoRole)


# ---------------------------------------------------
# BEHAVIORAL TESTS
# ----------------------------------------------------


@pytest.fixture
def worker():
    # Given
    market = Mock()
    agent = Mock(id=1)
    return WorkerRole(agent, market)


def test_perceive_labor_sold(worker):
    # Given
    market = worker.space
    market.get_labor_sold.return_value = 0.5

    # When
    labor_sold = worker.get_labor_sold()

    # Then
    market.get_labor_sold.assert_called_once_with(worker)
    assert labor_sold == 0.5


def test_perceive_unemployment_rate(worker):
    # Given
    market = worker.space
    market.unemployment_rate = 0.15

    # When
    unemployment = worker.get_unemployment_rate()

    # Then
    assert unemployment == 0.15


def test_search_employers(worker):
    # Given
    employers = [Mock() for _ in range(2)]
    market = worker.space
    market.search_employers.return_value = employers

    # When
    result = worker.search_employers(psi=3)

    # Then
    market.search_employers.assert_called_once_with(3)
    assert result == employers


def test_create_job(worker):
    # Given
    market = worker.space
    employer = Mock()

    # When
    worker.create_job(employer, quantity=1)

    # Then
    market.create_job.assert_called_with(worker, employer, 1)
