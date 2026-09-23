import pytest
from unittest.mock import Mock
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
def worker_with_env(worker_before_setup):
    # Given
    env = Mock()
    worker = worker_before_setup
    worker.env = env
    return worker, env


def test_get_unemployment(worker_with_env):
    # Given
    worker, env = worker_with_env
    env.unemployment = 0.12

    # When
    perceived = worker.get_unemployment()

    # Then
    assert perceived == 0.12


def test_find_employers_uses_env_method(worker_with_env):
    # Given
    worker, env = worker_with_env

    # When
    found = worker.find_employers(5)

    # Then
    env.find_employers.assert_called_with(5)
    assert found == env.find_employers.return_value


# ---------------------------------------------------
# ACTION TESTS
# ----------------------------------------------------


def test_accept_job_uses_hire_method(worker_with_env):
    # Given
    employer = Mock()
    worker, env = worker_with_env

    # When
    worker.accept_job(employer, 0.5)

    # Then
    env.hire_worker.assert_called_with(worker, employer, 0.5)
