import pytest
from unittest.mock import Mock
from model.base import EcoRole
from model.roles.worker import Worker

# ---------------------------------------------------
# ARCHITECTURE TESTS
# ----------------------------------------------------


def test_is_eco_role():
    # Assert
    assert issubclass(Worker, EcoRole)


@pytest.fixture
def role():
    # Given
    agent, env = Mock(), Mock()
    return Worker(agent, env)


def test_has_unit_labor_supply_prop(role):
    # Assert
    assert role.labor_supply == 1.0


# ---------------------------------------------------
# PERCEPTION TESTS
# ----------------------------------------------------


def test_get_labor_sold(role):
    # Given
    role.labor_supply = 0.6

    # When
    result = role.labor_sold

    # Then
    assert result == 0.4


def test_get_unemployment(role):
    # Given
    env = role.env
    env.unemployment = 0.12

    # When
    perceived = role.get_unemployment()

    # Then
    assert perceived == 0.12


def test_find_employers_get_random_founders(role):
    # Given
    employers = Mock()
    env = role.env
    env.find_random_roles.return_value = employers

    # When
    found = role.find_employers(5)

    # Then
    env.find_random_roles.assert_called_with("employer", 5)
    assert found == employers


# ---------------------------------------------------
# ACTION TESTS
# ----------------------------------------------------


def test_accept_job_uses_hire_method(role):
    # Given
    employer = Mock()
    env = role.env

    # When
    role.accept_job(employer, 0.5)

    # Then
    env.hire_worker.assert_called_with(role, employer, 0.5)
