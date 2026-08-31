import pytest
from unittest.mock import Mock
from mc_ab_sfc2.roles.employer import EmployerRole

# ---------------------------------------------------
# ARCHITECTURE TESTS
# ----------------------------------------------------


def test_is_eco_role():
    # Given
    from mc_ab_sfc2.base import EcoRole

    # Assert
    assert issubclass(EmployerRole, EcoRole)


@pytest.fixture
def employer():
    # Given
    market = Mock()
    agent = Mock(id=1)
    return EmployerRole(agent, market)


def test_has_default_labor_demand(employer):
    # Assert
    assert employer.labor_demand == 0.0


def test_exposes_wage_offer(employer):
    # Given
    firm = employer.agent
    firm.wage_offer = 10

    # Assert
    assert employer.wage_offer == 10
