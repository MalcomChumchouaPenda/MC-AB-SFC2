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
