import pytest
import agentpy as ap
from unittest.mock import Mock
from mcabsfc.roles import EmployerRole

# ---------------------------------------------------
# ARCHITECTURAL TESTS
# ----------------------------------------------------


def test_is_ecorole():
    # Given
    from mcabsfc.base import EcoRole

    # Assert
    assert issubclass(EmployerRole, EcoRole)
