import pytest
import agentpy as ap
from unittest.mock import Mock
from dataclasses import dataclass
from mcabsfc.agents import HouseholdAgent

# ---------------------------------------------------
# ARCHITECTURAL TESTS
# ----------------------------------------------------


def test_is_agent():
    # Given
    assert issubclass(HouseholdAgent, ap.Agent)


def test_has_roles_dict():
    household = HouseholdAgent(ap.Model())
    assert household.roles == {}


def test_has_unit_labor_supply():
    household = HouseholdAgent(ap.Model())
    assert household.labor_supply == 1.0


# ---------------------------------------------------
# BEHAVIORAL TESTS
# ----------------------------------------------------


@pytest.fixture
def worker_role():
    role = Mock()
    role.find_employers.return_value = []
    return role


@pytest.fixture
def unemployed_household(worker_role):
    worker_role.labor_sold = 0.0
    model = Mock()
    household = HouseholdAgent(model)
    household.labor_supply = 1.0
    household.reservation_wage = 10
    household.search_size = 6
    household.roles = {"worker": worker_role}
    return household


def test_search_jobs_with_limited_size(unemployed_household):
    # Given
    household = unemployed_household

    # When
    household.search_jobs()

    # Then
    action = household.roles["worker"].find_employers
    action.assert_called_with(household.search_size)


def test_search_jobs_with_highest_wage(unemployed_household):
    # Given
    household = unemployed_household
    employer1 = Mock(wage=15, demand=1.0)
    employer2 = Mock(wage=20, demand=1.0)
    employer3 = Mock(wage=10, demand=1.0)
    role = household.roles["worker"]
    role.find_employers.return_value = [employer1, employer2, employer3]

    # When
    household.search_jobs()

    # Then
    action = role.accept_job
    action.assert_called_with(employer2, pytest.approx(1.0))


def test_search_jobs_with_wage_above_reservation_wage(unemployed_household):
    # Given
    household = unemployed_household
    employer1 = Mock(wage=8, demand=1.0)
    employer2 = Mock(wage=9, demand=1.0)
    role = household.roles["worker"]
    role.find_employers.return_value = [employer1, employer2]

    # When
    household.search_jobs()

    # Then
    role.accept_job.assert_not_called()


def test_search_jobs_and_split_labor_between_employers(unemployed_household):
    # Given
    household = unemployed_household
    employer1 = Mock(wage=20, demand=0.4)
    employer2 = Mock(wage=15, demand=0.6)
    role = household.roles["worker"]
    role.find_employers.return_value = [employer1, employer2]

    # When
    household.search_jobs()

    # Then
    action = role.accept_job
    action.assert_any_call(employer1, pytest.approx(0.4))
    action.assert_any_call(employer2, pytest.approx(0.6))


@pytest.fixture
def employed_household(worker_role):
    worker_role.labor_sold = 0.1
    model = Mock()
    household = HouseholdAgent(model)
    household.labor_supply = 1.0
    household.reservation_wage = 10
    household.search_size = 6
    household.roles = {"worker": worker_role}
    return household


def test_search_jobs_while_labor_supply_is_remaining(employed_household):
    # Given
    household = employed_household
    employer1 = Mock(wage=25, demand=0.7)
    employer2 = Mock(wage=20, demand=0.7)
    employer3 = Mock(wage=15, demand=0.7)
    role = household.roles["worker"]
    role.find_employers.return_value = [employer1, employer2, employer3]

    # When
    household.search_jobs()

    # Then
    action = role.accept_job
    action.assert_any_call(employer1, pytest.approx(0.7))
    action.assert_any_call(employer2, pytest.approx(0.2))


