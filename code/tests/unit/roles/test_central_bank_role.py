import pytest
from unittest.mock import Mock
from mc_ab_sfc.roles import CentralBankRole

# ---------------------------------------------------
# ARCHITECTURAL TESTS
# ----------------------------------------------------


def test_is_ecorole():
    # Given
    from mc_ab_sfc.base import EcoRole

    # Assert
    assert issubclass(CentralBankRole, EcoRole)


@pytest.fixture
def role():
    # Given
    space = Mock()
    agent = Mock(id=1)
    return CentralBankRole(agent, space)


def test_exposes_discount_rate(role):
    # Given
    agent = role.agent
    agent.discount_rate = 0.05

    # Assert
    assert role.discount_rate == 0.05


# ---------------------------------------------------
# BEHAVIORAL TESTS
# ----------------------------------------------------
