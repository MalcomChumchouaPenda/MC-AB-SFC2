import pytest
from unittest.mock import Mock
from mc_ab_sfc.roles import NationalCentralBankRole

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


def test_exposes_discount_rate(role):
    # Given
    country = role.space
    country.discount_rate = 0.05

    # Assert
    assert role.discount_rate == 0.05


# ---------------------------------------------------
# BEHAVIORAL TESTS
# ----------------------------------------------------
