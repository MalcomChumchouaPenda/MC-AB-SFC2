import pytest
from unittest.mock import Mock
from networkx import Graph
from model.roles.employer import Employer

# ---------------------------------------------------
# ARCHITECTURE TESTS
# ----------------------------------------------------


def test_is_eco_role():
    # Given
    from model.base import EcoRole

    # Assert
    assert issubclass(Employer, EcoRole)


@pytest.fixture
def employer_before_setup():
    # Given
    model = Mock()
    employer = Employer(model)
    return employer


def test_has_wage_prop(employer_before_setup):
    # Given
    employer = employer_before_setup

    # When
    employer.setup()

    # Then
    assert employer.wage == 0


def test_has_labor_demand_prop(employer_before_setup):
    # Given
    employer = employer_before_setup

    # When
    employer.setup()

    # Then
    assert employer.labor_demand == 0


# ---------------------------------------------------
# PERCEPTION TESTS
# ----------------------------------------------------


@pytest.fixture
def employer_with_env(employer_before_setup):
    # Given
    env = Mock()
    employer = employer_before_setup
    employer.env = env
    return employer, env


def test_get_unemployment(employer_with_env):
    # Given
    employer, env = employer_with_env
    env.unemployment = 0.12

    # When
    perceived = employer.get_unemployment()

    # Then
    assert perceived == 0.12


def test_get_jobs(employer_with_env):
    # Given
    employer, env = employer_with_env

    # When
    jobs = employer.get_jobs()

    # Then
    env.find_jobs.assert_called_with(employer)
    assert jobs == env.find_jobs.return_value


# ---------------------------------------------------
# ACTION TESTS
# ----------------------------------------------------
