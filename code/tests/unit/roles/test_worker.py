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



@pytest.fixture
def worker_with_employers(worker_with_space):
    # Given
    employers = MagicMock()
    employers.__len__.return_value = 1
    employers.random.return_value = []
    worker, space = worker_with_space
    space.employers = employers
    return worker, employers


def test_find_employers_get_random_founders(worker_with_employers):
    # Given
    expected = [Mock() for _ in range(10)]
    worker, employers = worker_with_employers
    employers.random.return_value = expected

    # When
    found = worker.find_employers(5)

    # Then
    assert found == expected


@pytest.mark.parametrize("psi, expected", [(5, 5), (15, 10)])
def test_find_employers_with_psi_params(worker_with_employers, psi, expected):
    # Given
    worker, employers = worker_with_employers
    employers.__len__.return_value = 10

    # When
    worker.find_employers(psi)

    # Then
    employers.random.assert_called_with(expected)


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


