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
def employer_with_space(employer_before_setup):
    # Given
    space = Mock()
    employer = employer_before_setup
    employer.space = space
    return employer, space


def test_get_unemployment(employer_with_space):
    # Given
    employer, space = employer_with_space
    space.unemployment = 0.12

    # When
    perceived = employer.get_unemployment()

    # Then
    assert perceived == 0.12


def test_get_jobs(employer_with_space):
    # Given
    employer, space = employer_with_space
    worker1, worker2 = Mock(), Mock()
    graph = Graph()
    graph.add_nodes_from([worker1, worker2, employer])
    graph.add_edge(worker1, employer, quantity=0.4, wage=10)
    space.graph = graph

    # When
    jobs = employer.get_jobs()

    # Then
    assert jobs == [{"worker": worker1, "quantity": 0.4, "wage": 10}]


# ---------------------------------------------------
# ACTION TESTS
# ----------------------------------------------------
