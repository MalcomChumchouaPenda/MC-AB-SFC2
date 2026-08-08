import pytest
from unittest.mock import Mock
from mc_ab_sfc.roles import CommercialBankRole

# ---------------------------------------------------
# ARCHITECTURAL TESTS
# ----------------------------------------------------


def test_is_ecorole():
    # Given
    from mc_ab_sfc.base import EcoRole

    # Assert
    assert issubclass(CommercialBankRole, EcoRole)


@pytest.fixture
def role():
    # Given
    space = Mock()
    agent = Mock(id=1)
    return CommercialBankRole(agent, space)


def test_has_default_central_bank(role):
    # Assert
    assert role.central_bank is None


# ---------------------------------------------------
# BEHAVIORAL TESTS
# ----------------------------------------------------


def test_get_discount_rate(role):
    # Given
    central_bank = Mock(discount_rate=0.05)
    role.central_bank = central_bank

    # When
    result = role.get_discount_rate()

    # Then
    assert result == 0.05
