import pytest
from unittest.mock import Mock
from model.roles.employer import Employer

# ---------------------------------------------------
# ARCHITECTURE
# ----------------------------------------------------


def test_inherits_from_eco_role():
    # Given
    from model.extensions import EcoRole

    # Then
    assert issubclass(Employer, EcoRole)


@pytest.fixture
def agent():
    # Given
    return Mock()


@pytest.fixture
def env():
    # Given
    return Mock()


@pytest.fixture
def role(agent, env):
    # Given
    return Employer(agent, env)


def test_initializes_wage(role):
    # Then
    assert role.wage == 0


def test_initializes_labor(role):
    # Then
    assert role.labor == 0


def test_initializes_labor_demand(role):
    # Then
    assert role.labor_demand == 0


def test_initializes_defaulted(role):
    # Then
    assert role.defaulted is False


# ---------------------------------------------------
# PERCEPTION TESTS
# ----------------------------------------------------


def test_get_unemployment(role, env):
    # Given
    env.unemployment = 0.12

    # When
    perceived = role.get_unemployment()

    # Then
    assert perceived == 0.12


def test_get_jobs(role, env):
    # Given

    # When
    found = role.get_jobs()

    # Then
    env.links.assert_called_with(role)
    assert found == env.links.return_value


# ---------------------------------------------------
# ACTION TESTS
# ----------------------------------------------------


def test_pay_wages_uses_env_method(role, env):
    # Given
    worker = Mock()

    # When
    role.pay_wages(worker, 1.5)

    # Then
    env.pay_wages.assert_called_with(role, worker, 1.5)
