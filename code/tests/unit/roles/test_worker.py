import pytest
from unittest.mock import Mock, MagicMock
from networkx import Graph
from model.roles.worker import Worker

# ---------------------------------------------------
# ARCHITECTURE TESTS
# ----------------------------------------------------


def test_is_eco_role():
    # Given
    from model.base import EcoRole

    # Assert
    assert issubclass(Worker, EcoRole)


@pytest.fixture
def worker_before_setup():
    # Given
    model = Mock()
    worker = Worker(model)
    return worker


def test_has_unit_labor_supply_prop(worker_before_setup):
    # Given
    worker = worker_before_setup

    # When
    worker.setup()

    # Then
    assert worker.labor_supply == 1.0


# ---------------------------------------------------
# PERCEPTION TESTS
# ----------------------------------------------------


def test_get_labor_sold(worker_before_setup):
    # Given
    worker = worker_before_setup
    worker.labor_supply = 0.6

    # When
    result = worker.labor_sold

    # Then
    assert result == 0.4


@pytest.fixture
def worker_with_space(worker_before_setup):
    # Given
    space = Mock()
    worker = worker_before_setup
    worker.space = space
    return worker, space


def test_get_unemployment(worker_with_space):
    # Given
    worker, space = worker_with_space
    space.unemployment = 0.12

    # When
    perceived = worker.get_unemployment()

    # Then
    assert perceived == 0.12


def test_find_employers_uses_space_method(worker_with_space):
    # Given
    worker, space = worker_with_space

    # When
    found = worker.find_employers(5)

    # Then
    space.find_employers.assert_called_with(5)
    assert found == space.find_employers.return_value


# ---------------------------------------------------
# ACTION TESTS
# ----------------------------------------------------


def test_accept_job_uses_hire_method(worker_with_space):
    # Given
    employer = Mock()
    worker, space = worker_with_space

    # When
    worker.accept_job(employer, 0.5)

    # Then
    space.hire_worker.assert_called_with(worker, employer, 0.5)
