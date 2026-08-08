import pytest
from unittest.mock import Mock
from mc_ab_sfc.roles import TaxPayerRole

# ---------------------------------------------------
# ARCHITECTURE TESTS
# ----------------------------------------------------


def test_is_eco_role():
    # Given
    from mc_ab_sfc.base import EcoRole

    # Assert
    assert issubclass(TaxPayerRole, EcoRole)


# ---------------------------------------------------
# BEHAVIORAL TESTS
# ----------------------------------------------------


def test_get_tax_rate():
    # Given
    country = Mock()
    country.tax_rate = 0.20
    household = Mock(id=1)
    tax_payer = TaxPayerRole(household, country)

    # When
    tax_rate = tax_payer.get_tax_rate()

    # Then
    assert tax_rate == 0.20
