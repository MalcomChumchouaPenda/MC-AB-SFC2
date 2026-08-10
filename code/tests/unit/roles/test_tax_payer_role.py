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


@pytest.fixture
def tax_payer():
    # Given
    space = Mock()
    agent = Mock(id=1)
    return TaxPayerRole(agent, space)


def test_has_government_reference(tax_payer):
    # Assert
    assert tax_payer.government is None


# ---------------------------------------------------
# BEHAVIORAL TESTS
# ----------------------------------------------------


def test_get_tax_rate(tax_payer):
    # Given
    govt = Mock(tax_rate=0.20)
    tax_payer.government = govt

    # When
    tax_rate = tax_payer.get_tax_rate()

    # Then
    assert tax_rate == 0.20


def test_pay_taxes(tax_payer):
    # Given
    govt = Mock()
    tax_payer.government = govt
    country = tax_payer.space

    # When
    tax_payer.pay_taxes(10)

    # Then
    country.pay_taxes.assert_called_with(tax_payer, govt, 10)
