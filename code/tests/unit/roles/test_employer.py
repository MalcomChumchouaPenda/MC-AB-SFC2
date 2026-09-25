import pytest
from unittest.mock import Mock
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
def role_with_env():
    # Given
    agent, env = Mock(), Mock()
    role = Employer(agent, env)
    return role, env


def test_has_wage_prop(role_with_env):
    # Given
    role, _ = role_with_env

    # Assert
    assert role.wage == 0


def test_has_labor_demand_prop(role_with_env):
    # Given
    role, _ = role_with_env

    # Assert
    assert role.labor_demand == 0


# ---------------------------------------------------
# PERCEPTION TESTS
# ----------------------------------------------------


def test_get_unemployment(role_with_env):
    # Given
    role, env = role_with_env
    env.unemployment = 0.12

    # When
    perceived = role.get_unemployment()

    # Then
    assert perceived == 0.12


def test_get_jobs(role_with_env):
    # Given
    role, env = role_with_env
    job = {"worker": Mock(), "quantity": 0.4, "wage": 10}
    env.find_links.return_value = [job]

    # When
    found = role.get_jobs()

    # Then
    env.find_links.assert_called_with(role, "worker")
    assert found == [job]


# ---------------------------------------------------
# ACTION TESTS
# ----------------------------------------------------
