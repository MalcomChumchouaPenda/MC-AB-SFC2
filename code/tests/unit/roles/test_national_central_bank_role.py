import pytest
from unittest.mock import Mock
from mc_ab_sfc.roles.central_bank import NationalCentralBankRole

# ---------------------------------------------------
# ARCHITECTURE TESTS
# ----------------------------------------------------


def test_is_eco_role():
    # Given
    from mc_ab_sfc.base import EcoRole

    # Assert
    assert issubclass(NationalCentralBankRole, EcoRole)


@pytest.fixture
def role():
    # Given
    space = Mock()
    agent = Mock(id=1)
    return NationalCentralBankRole(agent, space)


def test_has_government_reference(role):
    # Assert
    assert role.government is None


def test_exposes_discount_rate(role):
    # Given
    country = role.space
    country.discount_rate = 0.05

    # Assert
    assert role.discount_rate == 0.05


# ---------------------------------------------------
# BEHAVIORAL TESTS
# ----------------------------------------------------


def test_transfer_profit(role):
    # Given
    country = role.space

    # When
    role.transfer_profit(100)

    # Then
    country.transfer_profit(role, 100)
