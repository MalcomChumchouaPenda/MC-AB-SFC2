import math
import pytest
import agentpy as ap
from unittest.mock import Mock
from mcabsfc.agents import HouseholdAgent, EcoAgent

# ---------------------------------------------------
# ARCHITECTURAL TESTS
# ----------------------------------------------------


def test_is_eco_agent():
    # Given
    model = ap.Model()

    # When
    household = HouseholdAgent(model)

    # Then
    assert isinstance(household, EcoAgent)


def test_has_unit_labor_supply():
    # Given
    model = ap.Model()

    # When
    household = HouseholdAgent(model)

    # Then
    assert household.labor_supply == 1.0


# ---------------------------------------------------
# BEHAVIORAL TESTS
# ----------------------------------------------------


@pytest.fixture
def model1():
    return ap.Model()

@pytest.fixture
def worker_role():
    role = Mock()
    role.find_employers.return_value = []
    return role


@pytest.fixture
def household1(model1, worker_role):
    # Given unemployed household
    worker_role.labor_sold = 0.0
    household = HouseholdAgent(model1)
    household.labor_supply = 1.0
    household.reservation_wage = 10
    household.search_size = 6
    household.roles = {"worker": worker_role}
    return household


def test_search_jobs_with_limited_size(household1):
    # Given
    household1.search_size = 4

    # When
    household1.search_jobs()

    # Then
    action = household1.roles["worker"].find_employers
    action.assert_called_with(4)


def test_search_jobs_with_highest_wage(household1):
    # Given
    employer1 = Mock(wage=15, demand=1.0)
    employer2 = Mock(wage=20, demand=1.0)
    employer3 = Mock(wage=10, demand=1.0)
    role = household1.roles["worker"]
    role.find_employers.return_value = [employer1, employer2, employer3]

    # When
    household1.search_jobs()

    # Then
    action = role.accept_job
    action.assert_called_with(employer2, pytest.approx(1.0))


def test_search_jobs_with_wage_above_reservation_wage(household1):
    # Given
    employer1 = Mock(wage=8, demand=1.0)
    employer2 = Mock(wage=9, demand=1.0)
    role = household1.roles["worker"]
    role.find_employers.return_value = [employer1, employer2]

    # When
    household1.search_jobs()

    # Then
    role.accept_job.assert_not_called()


def test_search_jobs_and_split_labor_between_employers(household1):
    # Given
    employer1 = Mock(wage=20, demand=0.4)
    employer2 = Mock(wage=15, demand=0.6)
    role = household1.roles["worker"]
    role.find_employers.return_value = [employer1, employer2]

    # When
    household1.search_jobs()

    # Then
    action = role.accept_job
    action.assert_any_call(employer1, pytest.approx(0.4))
    action.assert_any_call(employer2, pytest.approx(0.6))


@pytest.fixture
def household2(worker_role):
    # Given partially unemployed household
    worker_role.labor_sold = 0.1
    model = Mock()
    household = HouseholdAgent(model)
    household.labor_supply = 1.0
    household.reservation_wage = 10
    household.search_size = 6
    household.roles = {"worker": worker_role}
    return household


def test_search_jobs_while_labor_supply_is_remaining(household2):
    # Given
    employer1 = Mock(wage=25, demand=0.7)
    employer2 = Mock(wage=20, demand=0.7)
    employer3 = Mock(wage=15, demand=0.7)
    role = household2.roles["worker"]
    role.find_employers.return_value = [employer1, employer2, employer3]

    # When
    household2.search_jobs()

    # Then
    action = role.accept_job
    action.assert_any_call(employer1, pytest.approx(0.7))
    action.assert_any_call(employer2, pytest.approx(0.2))


@pytest.fixture
def model2():
    model = Mock()
    model.p.delta = 0.10
    model.p.upsilon = 1.0
    model.p.upsilon_h = 1.0
    return model


@pytest.fixture
def household3(model2, worker_role):
    # Given fully employed household
    household = HouseholdAgent(model2)
    household.labor_supply = 1.0
    household.employed_labor = 1.0
    household.reservation_wage = 10.0
    household.roles = {"worker": worker_role}
    return household


def test_increases_reservation_wage_when_fully_employed(household3, model2):
    # Given
    household3.roles["worker"].unemployment_rate = 0.05
    model2.nprandom.choice.return_value = 1
    model2.nprandom.uniform.return_value = 0.05

    # When
    household3.revise_reservation_wage()

    # Then
    model2.nprandom.uniform.assert_called_with(0, model2.p.delta)
    assert household3.reservation_wage > 10.0


def test_dont_increases_reservation_wage_when_chooses_not_to_revise(household3, model2):
    # Given
    household3.employed_labor = 1.0
    household3.roles["worker"].unemployment_rate = 0.05
    model2.nprandom.choice.return_value = 0
    model2.nprandom.uniform.return_value = 0.05

    # When
    household3.revise_reservation_wage()

    # Then
    model2.nprandom.uniform.assert_not_called()
    assert household3.reservation_wage == 10.0


def test_upward_wage_revision_probability_when_fully_employed(household3, model2):
    # Given
    household3.roles["worker"].unemployment_rate = 0.10
    model2.nprandom.choice.return_value = 0
    model2.nprandom.uniform.return_value = 0.05

    # When
    household3.revise_reservation_wage()

    # Then
    p = model2.p
    prob = p.upsilon_h * math.exp(-p.upsilon * 0.10)
    model2.nprandom.choice.assert_called_with([0, 1], p=[1 - prob, prob])


@pytest.fixture
def household4(model2, worker_role):
    # Given partially employed household
    household = HouseholdAgent(model2)
    household.labor_supply = 1.0
    household.employed_labor = 0.0
    household.reservation_wage = 10.0
    household.roles = {"worker": worker_role}
    return household


def test_decreases_reservation_wage_when_not_fully_employed(household4, model2):
    # Given
    household4.roles["worker"].unemployment_rate = 0.30
    model2.nprandom.choice.return_value = 1
    model2.nprandom.uniform.return_value = 0.05

    # When
    household4.revise_reservation_wage()

    # Then
    model2.nprandom.uniform.assert_called_with(0, model2.p.delta)
    assert household4.reservation_wage < 10.0


def test_dont_decreases_reservation_wage_when_chooses_not_to_revise(household4, model2):
    # Given
    household4.employed_labor = 0.0
    household4.roles["worker"].unemployment_rate = 0.30
    model2.nprandom.choice.return_value = 0
    model2.nprandom.uniform.return_value = 0.05

    # When
    household4.revise_reservation_wage()

    # Then
    model2.nprandom.uniform.assert_not_called()
    assert household4.reservation_wage == 10.0


def test_downward_wage_revision_probability_when_partially_employed(household4, model2):
    # Given
    household4.roles["worker"].unemployment_rate = 0.10
    model2.nprandom.choice.return_value = 1
    model2.nprandom.uniform.return_value = 0.05

    # When
    household4.revise_reservation_wage()

    # Then
    p = model2.p
    prob = p.upsilon_h * math.exp(-p.upsilon * 0.10)
    model2.nprandom.choice.assert_called_with([0, 1], p=[prob, 1 - prob])
