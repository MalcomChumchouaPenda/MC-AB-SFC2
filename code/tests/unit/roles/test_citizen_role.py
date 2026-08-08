import pytest
from unittest.mock import Mock
from mc_ab_sfc.roles import CitizenRole

# ---------------------------------------------------
# ARCHITECTURAL TESTS
# ----------------------------------------------------


def test_is_ecorole():
    # Given
    from mc_ab_sfc.base import EcoRole

    # Assert
    assert issubclass(CitizenRole, EcoRole)
