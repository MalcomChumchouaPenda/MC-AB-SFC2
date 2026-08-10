import pytest
from unittest.mock import Mock
from mc_ab_sfc.roles import CommercialBankRole

# ---------------------------------------------------
# ARCHITECTURE TESTS
# ----------------------------------------------------


def test_is_eco_role():
    # Given
    from mc_ab_sfc.base import EcoRole

    # Assert
    assert issubclass(CommercialBankRole, EcoRole)


@pytest.fixture
def bank_role():
    # Given
    space = Mock()
    agent = Mock(id=1)
    return CommercialBankRole(agent, space)


def test_has_default_central_bank(bank_role):
    # Assert
    assert bank_role.central_bank is None


# ---------------------------------------------------
# BEHAVIORAL TESTS
# ----------------------------------------------------


def test_get_discount_rate(bank_role):
    # Given
    central_bank = Mock(discount_rate=0.05)
    bank_role.central_bank = central_bank

    # When
    result = bank_role.get_discount_rate()

    # Then
    assert result == 0.05


def test_request_cash_advances(bank_role):
    # Given
    central_bank = Mock()
    bank_role.central_bank = central_bank
    monetary_union = bank_role.space

    # When
    bank_role.request_cash_advances(100)

    # Then
    action = monetary_union.request_cash_advances
    action.assert_called_with(bank_role, 100)
