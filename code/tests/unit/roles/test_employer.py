import pytest
from unittest.mock import Mock
from model.roles.employer import Employer

# ---------------------------------------------------
# ARCHITECTURE
# ----------------------------------------------------


def test_inherits_from_eco_role():
    # Given
    from model.base import EcoRole

    # When
    is_derived = issubclass(Employer, EcoRole)

    # Then
    assert is_derived


def test_initializes_wage():
    # Given
    agent, env = Mock(), Mock()

    # When
    role = Employer(agent, env)

    # Then
    assert role.wage == 0


def test_initializes_labor_demand():
    # Given
    agent, env = Mock(), Mock()

    # When
    role = Employer(agent, env)

    # Then
    assert role.labor_demand == 0


# ---------------------------------------------------
# PERCEPTION TESTS
# ----------------------------------------------------


@pytest.fixture
def role():
    # Given
    agent, env = Mock(), Mock()
    return Employer(agent, env)


def test_get_unemployment(role):
    # Given
    env = role.env
    env.unemployment = 0.12

    # When
    perceived = role.get_unemployment()

    # Then
    assert perceived == 0.12


def test_get_jobs(role):
    # Given
    env = role.env

    # When
    found = role.get_jobs()

    # Then
    env.find_links.assert_called_with(role, "worker")
    assert found == env.find_links.return_value


# ---------------------------------------------------
# ACTION TESTS
# ----------------------------------------------------
