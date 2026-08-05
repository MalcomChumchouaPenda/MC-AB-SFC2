import pytest
import agentpy as ap
from unittest.mock import Mock
from mcabsfc.roles import CitizenRole

# ---------------------------------------------------
# ARCHITECTURAL TESTS
# ----------------------------------------------------


def test_is_ecorole():
    # Given
    from mcabsfc.base import EcoRole

    # Assert
    assert issubclass(CitizenRole, EcoRole)


def test_citizen_role_get_tax_rate():
    # Given
    country = Mock()
    country.tax_rate = 0.20
    household = Mock(id=1)
    citizen = CitizenRole(household, country)

    # When
    tax_rate = citizen.get_tax_rate()

    # Then
    assert tax_rate == 0.20
