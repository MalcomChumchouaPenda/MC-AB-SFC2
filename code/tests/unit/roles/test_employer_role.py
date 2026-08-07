import pytest
import agentpy as ap
from unittest.mock import Mock
from mc_ab_sfc.roles import EmployerRole

# ---------------------------------------------------
# ARCHITECTURAL TESTS
# ----------------------------------------------------


def test_is_ecorole():
    # Given
    from mc_ab_sfc.base import EcoRole

    # Assert
    assert issubclass(EmployerRole, EcoRole)


@pytest.fixture
def employer():
    # Given
    market = Mock()
    owner = Mock(id=1)
    return EmployerRole(owner, market)


def test_has_default_labor_demand(employer):
    # Assert
    assert employer.labor_demand == 0.0


def test_exposes_available_quantity(employer):
    # Given
    firm = employer.owner
    firm.wage_offer = 10

    # Assert
    assert employer.wage_offer == 10
